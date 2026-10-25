#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nvidia_router.py — Orquestador de modelos NVIDIA NIM para Última Prensa.

Reparte cada tarea editorial (redacción, análisis de expedientes, extracción de
datos, verificación, ideas, búsqueda semántica) entre varios modelos del catálogo
de build.nvidia.com, respetando cuotas propias por modelo y pasando solo al
respaldo cuando el modelo preferente se queda sin cupo o falla.

El trial de build.nvidia.com es gratuito y se limita por peticiones por minuto
(≈40 RPM por modelo), no por token. Por eso lo que se administra aquí son
llamadas por minuto y por día, no dinero.

Uso:
    python kit-journalism/scripts/nvidia_router.py estado
    python kit-journalism/scripts/nvidia_router.py modelos
    python kit-journalism/scripts/nvidia_router.py llamar --tarea redaccion --archivo nota.md
    python kit-journalism/scripts/nvidia_router.py llamar --tarea extraccion --texto "..." --json
    python kit-journalism/scripts/nvidia_router.py embeddings --texto "..." --texto "..."
    python kit-journalism/scripts/nvidia_router.py --autoprueba

Requisitos:
    NVIDIA_API_KEY en el entorno, en kit-journalism/.env o en el .env del proyecto.
    Clave gratuita en https://build.nvidia.com/settings/api-keys
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import threading
import time
from datetime import date
from pathlib import Path

import requests

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("Falta PyYAML: pip install -r requirements.txt")

BASE = Path(__file__).resolve().parent.parent          # kit-journalism/
CONFIG_DEFECTO = BASE / "config" / "nvidia.yaml"
ESTADO_DEFECTO = BASE / ".nvidia_router" / "uso.json"
BASE_URL_DEFECTO = "https://integrate.api.nvidia.com/v1"

CABECERA_AYUDA = "Router NVIDIA NIM — Última Prensa"


# ---------------------------------------------------------------------------
# Configuración y credenciales
# ---------------------------------------------------------------------------
def cargar_config(ruta: Path | None = None) -> dict:
    ruta = ruta or Path(os.environ.get("NVIDIA_ROUTER_CONFIG", CONFIG_DEFECTO))
    if not ruta.exists():
        sys.exit(f"No existe el archivo de configuración: {ruta}")
    with open(ruta, encoding="utf-8") as f:
        datos = yaml.safe_load(f) or {}
    datos.setdefault("servidor", {})
    datos.setdefault("limites", {})
    datos.setdefault("tareas", {})
    datos["servidor"].setdefault("base_url", BASE_URL_DEFECTO)
    datos["servidor"].setdefault("timeout_s", 180)
    datos["servidor"].setdefault("reintentos_por_modelo", 2)
    return datos


def buscar_clave() -> str:
    """Devuelve la clave si está en el entorno o en los .env; si no, cadena vacía."""
    clave = os.environ.get("NVIDIA_API_KEY", "").strip()
    if clave:
        return clave
    for candidato in (BASE / ".env", BASE.parent / ".env"):
        if not candidato.exists():
            continue
        for linea in candidato.read_text(encoding="utf-8", errors="ignore").splitlines():
            linea = linea.strip()
            if linea.startswith("NVIDIA_API_KEY="):
                valor = linea.split("=", 1)[1].strip().strip('"').strip("'")
                if valor:
                    return valor
    return ""


def leer_clave() -> str:
    """Como buscar_clave, pero aborta con instrucciones si no hay ninguna."""
    clave = buscar_clave()
    if clave:
        return clave
    sys.exit(
        "Falta NVIDIA_API_KEY.\n"
        "  Genera la clave en https://build.nvidia.com/settings/api-keys\n"
        f"  y agrégala a {BASE / '.env'} así:  NVIDIA_API_KEY=nvapi-...\n"
        "  Más rápido:  bash kit-journalism/scripts/configurar_nvidia_key.sh\n"
        "  No la pegues en el chat."
    )


# ---------------------------------------------------------------------------
# Registro de uso (el contador del "cuánto")
# ---------------------------------------------------------------------------
class Registro:
    """Cuenta llamadas por modelo y por minuto; se reinicia a diario."""

    def __init__(self, ruta: Path | None = None):
        self.ruta = Path(ruta or os.environ.get("NVIDIA_ROUTER_ESTADO", ESTADO_DEFECTO))
        self.hoy = date.today().isoformat()
        self.eventos: list[dict] = []
        self._cargar()

    def _cargar(self) -> None:
        if not self.ruta.exists():
            return
        try:
            datos = json.loads(self.ruta.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        if datos.get("fecha") == self.hoy:
            self.eventos = datos.get("eventos", [])

    def guardar(self) -> None:
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = self.ruta.with_suffix(".tmp")
        temporal.write_text(
            json.dumps({"fecha": self.hoy, "eventos": self.eventos}, ensure_ascii=False),
            encoding="utf-8",
        )
        temporal.replace(self.ruta)

    def anotar(self, modelo: str, tarea: str, ok: bool, entrada: int, salida: int, ms: int) -> None:
        self.eventos.append(
            {
                "t": round(time.time(), 3),
                "modelo": modelo,
                "tarea": tarea,
                "ok": ok,
                "in": entrada,
                "out": salida,
                "ms": ms,
            }
        )
        self.guardar()

    def del_modelo(self, modelo: str) -> list[dict]:
        return [e for e in self.eventos if e["modelo"] == modelo]

    def llamadas_hoy(self, modelo: str) -> int:
        return len(self.del_modelo(modelo))

    def en_ventana(self, modelo: str, segundos: int = 60) -> int:
        limite = time.time() - segundos
        return len([e for e in self.del_modelo(modelo) if e["t"] >= limite])

    def total_hoy(self) -> int:
        return len(self.eventos)

    def tokens_hoy(self) -> tuple[int, int]:
        return (
            sum(e.get("in", 0) for e in self.eventos),
            sum(e.get("out", 0) for e in self.eventos),
        )


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
class RouterNVIDIA:
    def __init__(self, config: dict | None = None, clave: str | None = None,
                 registro: Registro | None = None, base_url: str | None = None):
        self.config = config or cargar_config()
        self._clave = clave
        self.servidor = self.config["servidor"]
        self.base_url = (base_url or self.servidor["base_url"]).rstrip("/")
        self.timeout = self.servidor["timeout_s"]
        self.registro = registro or Registro()
        self.agotados: dict[str, str] = {}
        self.sesion = requests.Session()

    @property
    def clave(self) -> str:
        """Se resuelve al primer uso: el catálogo y el estado no necesitan clave."""
        if not self._clave:
            self._clave = leer_clave()
        return self._clave

    # -- cuotas ------------------------------------------------------------
    def limites_de(self, modelo: str) -> dict:
        por_modelo = self.config["limites"].get("por_modelo") or {}
        base = dict(self.config["limites"].get("por_defecto") or {"rpm": 6, "dia": 200})
        base.update(por_modelo.get(modelo, {}))
        return base

    def permiso(self, modelo: str) -> tuple[bool, str]:
        if modelo in self.agotados:
            return False, self.agotados[modelo]
        lim = self.limites_de(modelo)
        if self.registro.total_hoy() >= int(self.config["limites"].get("llamadas_dia", 1500)):
            return False, "tope diario global alcanzado"
        if self.registro.llamadas_hoy(modelo) >= int(lim.get("dia", 200)):
            return False, f"cupo diario agotado ({lim.get('dia')} llamadas)"
        rpm = int(lim.get("rpm", 6))
        rpm_global = int(self.config["limites"].get("rpm_global", 30))
        if self.registro.en_ventana(modelo) >= rpm:
            return False, f"límite de {rpm} RPM alcanzado"
        if len([e for e in self.registro.eventos if e["t"] >= time.time() - 60]) >= rpm_global:
            return False, f"límite global de {rpm_global} RPM alcanzado"
        return True, ""

    def marcar_agotado(self, modelo: str, motivo: str) -> None:
        self.agotados[modelo] = motivo

    # -- HTTP --------------------------------------------------------------
    def _cabeceras(self, con_clave: bool = True) -> dict:
        cabeceras = {"Accept": "application/json", "Content-Type": "application/json"}
        if con_clave:
            cabeceras["Authorization"] = f"Bearer {self.clave}"
        return cabeceras

    def _post(self, ruta: str, payload: dict) -> requests.Response:
        return self.sesion.post(
            f"{self.base_url}{ruta}", headers=self._cabeceras(),
            json=payload, timeout=self.timeout,
        )

    def _get(self, ruta: str, con_clave: bool = False) -> requests.Response:
        return self.sesion.get(f"{self.base_url}{ruta}",
                               headers=self._cabeceras(con_clave=con_clave), timeout=60)

    # -- operaciones -------------------------------------------------------
    def modelos(self) -> list[str]:
        """Catálogo real de modelos disponibles. El endpoint es público: no exige clave."""
        respuesta = self._get("/models")
        if respuesta.status_code in (401, 403):
            sys.exit(f"El catálogo rechazó la petición (HTTP {respuesta.status_code}).")
        respuesta.raise_for_status()
        datos = respuesta.json().get("data", [])
        return sorted({m.get("id", "") for m in datos if m.get("id")})

    def chat(self, tarea: str, mensajes: list[dict], max_tokens: int | None = None,
             temperatura: float | None = None, candidatos: list[str] | None = None) -> dict:
        if tarea not in self.config["tareas"]:
            raise ValueError(f"Tarea desconocida: {tarea}. Disponibles: {', '.join(self.config['tareas'])}")
        definicion = self.config["tareas"][tarea]
        cadena = candidatos or list(definicion.get("candidatos") or [])
        if not cadena:
            raise ValueError(f"La tarea '{tarea}' no tiene candidatos configurados")
        parametros = dict(definicion.get("parametros") or {})
        if max_tokens:
            parametros["max_tokens"] = max_tokens
        if temperatura is not None:
            parametros["temperature"] = temperatura
        parametros.pop("lote", None)

        bitacora: list[dict] = []
        for modelo in cadena:
            permitido, motivo = self.permiso(modelo)
            if not permitido:
                bitacora.append({"modelo": modelo, "resultado": "sin cupo", "detalle": motivo})
                continue

            for intento in range(1, int(self.servidor["reintentos_por_modelo"]) + 1):
                payload = {"model": modelo, "messages": mensajes, **parametros}
                inicio = time.time()
                try:
                    respuesta = self._post("/chat/completions", payload)
                except (requests.ConnectionError, requests.Timeout) as error:
                    bitacora.append({"modelo": modelo, "resultado": "error de red",
                                     "detalle": f"{type(error).__name__} (intento {intento})"})
                    time.sleep(min(2 ** intento, 8))
                    continue

                ms = int((time.time() - inicio) * 1000)
                if respuesta.status_code == 200:
                    cuerpo = respuesta.json()
                    uso = cuerpo.get("usage") or {}
                    eleccion = cuerpo["choices"][0]
                    mensaje = eleccion.get("message") or {}
                    texto = (mensaje.get("content") or "").strip()
                    aviso = ""
                    if not texto:
                        # DeepSeek y glm-5-flash razonan por defecto: si max_tokens es
                        # bajo, todo el presupuesto se va en el razonamiento y
                        # "content" vuelve nulo.
                        razonamiento = (mensaje.get("reasoning_content") or "").strip()
                        if razonamiento:
                            texto = razonamiento
                            aviso = ("el modelo gastó max_tokens razonando y no llegó a responder: "
                                     "sube --max-tokens")
                    self.registro.anotar(modelo, tarea, True,
                                         uso.get("prompt_tokens", 0),
                                         uso.get("completion_tokens", 0), ms)
                    return {
                        "texto": texto,
                        "modelo": modelo,
                        "tarea": tarea,
                        "aviso": aviso,
                        "termino": eleccion.get("finish_reason"),
                        "uso": {"entrada": uso.get("prompt_tokens", 0),
                                "salida": uso.get("completion_tokens", 0),
                                "ms": ms},
                        "bitacora": bitacora,
                    }

                if respuesta.status_code in (401, 403):
                    raise SystemExit(
                        f"Acceso rechazado ({respuesta.status_code}) para {modelo}: {respuesta.text[:200]}\n"
                        "  Revisa NVIDIA_API_KEY (https://build.nvidia.com/settings/api-keys) "
                        "o si ese modelo sigue habilitado para tu cuenta."
                    )
                if respuesta.status_code in (429, 402):
                    self.registro.anotar(modelo, tarea, False, 0, 0, ms)
                    self.marcar_agotado(modelo, f"sin cupo en el servidor ({respuesta.status_code})")
                    bitacora.append({"modelo": modelo, "resultado": "sin cupo",
                                     "detalle": f"HTTP {respuesta.status_code}"})
                    break
                if respuesta.status_code >= 500:
                    bitacora.append({"modelo": modelo, "resultado": "error del servidor",
                                     "detalle": f"HTTP {respuesta.status_code} (intento {intento})"})
                    time.sleep(min(2 ** intento, 8))
                    continue
                bitacora.append({"modelo": modelo, "resultado": "petición rechazada",
                                 "detalle": f"HTTP {respuesta.status_code}: {respuesta.text[:300]}"})
                break
            else:
                continue
            continue

        detalle = "; ".join(f"{b['modelo']} → {b['resultado']} ({b.get('detalle','')})" for b in bitacora)
        raise RuntimeError(f"Ningún modelo pudo atender la tarea '{tarea}'. Detalle: {detalle}")

    def embeddings(self, textos: list[str], tarea: str = "embeddings",
                   candidatos: list[str] | None = None) -> dict:
        definicion = self.config["tareas"].get(tarea, {})
        cadena = candidatos or list(definicion.get("candidatos") or [])
        parametros = dict(definicion.get("parametros") or {})
        lote = int(parametros.pop("lote", 32))
        motivos: list[str] = []
        for modelo in cadena:
            permitido, razon = self.permiso(modelo)
            if not permitido:
                motivos.append(f"{modelo}: sin cupo ({razon})")
                continue
            vectores: list[list[float]] = []
            fallo = ""
            for i in range(0, len(textos), lote):
                payload = {"model": modelo, "input": textos[i:i + lote], **parametros}
                inicio = time.time()
                try:
                    respuesta = self._post("/embeddings", payload)
                except (requests.ConnectionError, requests.Timeout) as error:
                    fallo = f"error de red ({type(error).__name__})"
                    break
                if respuesta.status_code == 200:
                    cuerpo = respuesta.json()
                    self.registro.anotar(modelo, tarea, True,
                                         (cuerpo.get("usage") or {}).get("prompt_tokens", 0), 0,
                                         int((time.time() - inicio) * 1000))
                    vectores.extend(d["embedding"] for d in cuerpo.get("data", []))
                    continue
                if respuesta.status_code in (429, 402):
                    self.marcar_agotado(modelo, f"sin cupo ({respuesta.status_code})")
                    fallo = f"sin cupo (HTTP {respuesta.status_code})"
                else:
                    fallo = f"HTTP {respuesta.status_code}: {respuesta.text[:160]}"
                break
            if not fallo and len(vectores) == len(textos):
                return {"vectores": vectores, "modelo": modelo,
                        "dimension": len(vectores[0]) if vectores else 0}
            motivos.append(f"{modelo}: {fallo or 'devolvió menos vectores de los pedidos'}")
        raise RuntimeError("Ningún modelo pudo generar embeddings. " + " | ".join(motivos))


# ---------------------------------------------------------------------------
# Derivación a CLIs de agente (usan el plan del usuario, no cobran por token)
# ---------------------------------------------------------------------------
def resolver_ejecutable(valor: str) -> str:
    """Acepta una ruta o un nombre en el PATH (claude, agy) y devuelve la ruta real."""
    if os.path.sep in valor or valor.startswith("~"):
        ruta = os.path.expanduser(valor)
        if Path(ruta).exists():
            return ruta
    else:
        encontrado = shutil.which(valor)
        if encontrado:
            return encontrado
    raise SystemExit(f"No encontré el ejecutable: {valor}")


def config_motor(config: dict, motor: str) -> dict:
    derivacion = config.get("derivacion") or {}
    motores = [nombre for nombre, valor in derivacion.items()
               if isinstance(valor, dict) and "ejecutable" in valor]
    if motor not in motores:
        raise SystemExit(f"Motor desconocido: {motor}. Configurados: {', '.join(motores) or 'ninguno'}")
    definicion = derivacion[motor]
    if definicion.get("habilitado") is False:
        raise SystemExit(
            f"El motor '{motor}' está deshabilitado en config/nvidia.yaml.\n"
            f"  {definicion.get('nota', '')}"
        )
    resolver_ejecutable(definicion["ejecutable"])
    return definicion


def derivar(config: dict, motor: str, tarea: str, contenido: str, workdir: Path,
            instruccion: str | None = None, modelo: str | None = None,
            timeout: int | None = None) -> dict:
    """Entrega el trabajo a un CLI de agente (agy, claude) en vez de a la API.

    El contenido va a un archivo dentro del workdir y el CLI recibe la orden de
    leerlo: así no se topa con el límite de longitud de argumentos ni se pierde
    el contexto por el camino.
    """
    import subprocess

    definicion = config_motor(config, motor)
    modelos = definicion.get("modelos") or {}
    modelo = modelo or modelos.get(tarea) or modelos.get("por_defecto")
    if not modelo:
        raise SystemExit(f"El motor '{motor}' no define modelo para la tarea '{tarea}'")
    esfuerzos = definicion.get("esfuerzos") or {}
    esfuerzo = esfuerzos.get(tarea) or esfuerzos.get("por_defecto")
    instruccion = (instruccion
                   or (definicion.get("instrucciones") or {}).get(tarea)
                   or ((config.get("derivacion") or {}).get("instrucciones") or {}).get(tarea))
    if not instruccion:
        raise SystemExit(f"Falta --instruccion para la tarea '{tarea}' en el motor '{motor}'")
    timeout = int(timeout or definicion.get("timeout_s", 900))

    workdir = Path(workdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    entrada = workdir / f".derivacion_{tarea}.md"
    entrada.write_text(contenido, encoding="utf-8")
    orden = (
        f"Lee el archivo {entrada.name} que está en el directorio de trabajo y ejecútalo al pie "
        f"de la letra. Ese archivo no es la tarea completa: contiene el material. La instrucción es: "
        f"{instruccion}\n"
        "Responde solo con el texto pedido. No agregues comentarios sobre lo que hiciste, ni notas, "
        "ni advertencias, ni aclaraciones sobre el archivo o el proceso."
    )

    ejecutable = resolver_ejecutable(definicion["ejecutable"])
    if motor == "agy":
        comando = [ejecutable, "--add-dir", str(workdir), "--model", modelo, "--output-format", "json"]
        # En agy el nivel de esfuerzo va en el nombre del modelo (…-high), así que
        # --effort solo se agrega si la configuración lo pide explícitamente.
        if esfuerzo:
            comando.append(f"--effort={esfuerzo}")
        comando += ["--print-timeout", f"{timeout}s", "--dangerously-skip-permissions",
                    f"--print={orden}"]
    else:  # claude y otros CLI de Anthropic
        comando = [ejecutable, "-p", orden, "--model", modelo,
                   "--output-format", "json", "--allowedTools", "Read",
                   "--max-turns", "8"]
        if esfuerzo:
            comando += ["--effort", esfuerzo]

    inicio = time.time()
    proceso = subprocess.run(comando, cwd=workdir, capture_output=True, text=True, timeout=timeout)
    ms = int((time.time() - inicio) * 1000)
    if proceso.returncode != 0:
        raise SystemExit(
            f"El motor '{motor}' falló (código {proceso.returncode}).\n"
            f"  {proceso.stderr.strip()[:600] or proceso.stdout.strip()[:600]}"
        )

    try:
        datos = json.loads(proceso.stdout)
    except json.JSONDecodeError:
        # Algunos CLI imprimen avisos antes del JSON: se busca el último objeto.
        fragmento = proceso.stdout[proceso.stdout.find("{"):proceso.stdout.rfind("}") + 1]
        try:
            datos = json.loads(fragmento)
        except json.JSONDecodeError:
            raise SystemExit(f"El motor '{motor}' no devolvió JSON válido:\n{proceso.stdout[:800]}")

    negadas = datos.get("denied_actions") or []
    texto = (datos.get("response") or datos.get("result") or "").strip()
    uso = datos.get("usage") or {}
    # Cada CLI informa el consumo a su manera: agy trae total_tokens; claude
    # separa la entrada fresca del caché (que es la mayor parte de la cuenta).
    entrada = (uso.get("input_tokens", 0)
               + uso.get("cache_creation_input_tokens", 0)
               + uso.get("cache_read_input_tokens", 0))
    salida = uso.get("output_tokens", 0)
    total = uso.get("total_tokens") or (entrada + salida)
    if negadas:
        raise SystemExit(
            f"El motor '{motor}' denegó acciones por permisos: {json.dumps(negadas)[:400]}"
        )
    if not texto:
        raise SystemExit(f"El motor '{motor}' devolvió una respuesta vacía.")

    return {
        "texto": texto,
        "motor": motor,
        "modelo": modelo,
        "esfuerzo": esfuerzo,
        "tarea": tarea,
        "uso": {
            "entrada": entrada,
            "salida": salida,
            "total": total,
            "cache": uso.get("cache_read_input_tokens", 0),
            "ms": ms,
            "costo_usd": datos.get("total_cost_usd"),
            "modelos_reportados": list((datos.get("modelUsage") or {}).keys()),
        },
        "conversacion": datos.get("conversation_id") or datos.get("session_id"),
    }


def animar_derivacion(config: dict, resultado: dict, registro: Registro) -> None:
    """Deja la derivación en el mismo registro de uso que las llamadas a la API."""
    etiqueta = f"cli:{resultado['motor']}:{resultado['modelo']}"
    if resultado.get("esfuerzo"):
        etiqueta += f"@{resultado['esfuerzo']}"
    registro.eventos.append({
        "t": round(time.time(), 3),
        "modelo": etiqueta,
        "tarea": resultado["tarea"],
        "ok": True,
        "in": resultado["uso"].get("entrada", 0),
        "out": resultado["uso"].get("salida", 0),
        "ms": resultado["uso"].get("ms", 0),
    })
    registro.guardar()


# ---------------------------------------------------------------------------
# Presentación
# ---------------------------------------------------------------------------
def mostrar_estado(router: RouterNVIDIA) -> None:
    registro = router.registro
    print(f"{CABECERA_AYUDA} — uso del {registro.hoy}")
    tin, tout = registro.tokens_hoy()
    techo = router.config["limites"].get("llamadas_dia", 1500)
    print(f"  Llamadas hoy: {registro.total_hoy()}/{techo}   tokens entrada/salida: {tin}/{tout}")
    print()

    try:
        catalogo = set(router.modelos())
    except Exception:  # sin red o catálogo caído: el estado sigue sirviendo
        catalogo = set()

    print(f"  {'modelo':<42} {'hoy':>5} {'techo':>6} {'últ.60s':>8} {'RPM':>4}  tarea(s)")
    print("  " + "-" * 96)
    desconocidos = []
    modelos = []
    for tarea, definicion in router.config["tareas"].items():
        for modelo in definicion.get("candidatos") or []:
            if modelo not in modelos:
                modelos.append(modelo)
    for modelo in modelos:
        lim = router.limites_de(modelo)
        hoy = registro.llamadas_hoy(modelo)
        ventana = registro.en_ventana(modelo)
        tareas = [t for t, d in router.config["tareas"].items() if modelo in (d.get("candidatos") or [])]
        marcas = ""
        if catalogo and modelo not in catalogo:
            marcas = "  ⚠ no está en el catálogo"
            desconocidos.append(modelo)
        elif hoy >= int(lim.get("dia", 200)):
            marcas = "  ← cupo diario agotado"
        print(f"  {modelo:<42} {hoy:>5} {int(lim.get('dia', 200)):>6} {ventana:>8} "
              f"{int(lim.get('rpm', 6)):>4}  {', '.join(tareas)}{marcas}")
    print()
    if desconocidos:
        print("  Corrige estos identificadores en config/nvidia.yaml "
              "(el catálogo se lista con: nvidia_router.py modelos):")
        for modelo in desconocidos:
            print(f"    - {modelo}")
        print()

    derivaciones = [e for e in registro.eventos if e["modelo"].startswith("cli:")]
    if derivaciones:
        tokens = sum(e.get("in", 0) + e.get("out", 0) for e in derivaciones)
        print(f"  Derivaciones a CLI hoy: {len(derivaciones)} "
              f"({tokens} tokens, sin costo por token)")
        for nombre in sorted({e["modelo"] for e in derivaciones}):
            veces = len([e for e in derivaciones if e["modelo"] == nombre])
            print(f"    {nombre}: {veces}")
        print()
    print("  El trial de NVIDIA no cobra por token: lo que se agota son llamadas por minuto y por día.")


CATEGORIAS = [
    ("traducción", ("riva-translate",)),
    ("transcripción", ("asr", "parakeet", "canary", "conformer", "whisper")),
    ("voz sintética", ("tts", "chatterbox", "magpie")),
    ("documentos y OCR", ("ocr", "parse", "paddleocr", "nemoretriever")),
    ("búsqueda semántica", ("embed", "rerank")),
    ("seguridad de contenido", ("guard", "safety", "nemoguard")),
    ("visión", ("vision", "vl", "cosmos", "image", "video", "detector")),
    ("razonamiento y redacción", ("nemotron", "deepseek", "glm", "llama", "qwen", "mistral", "kimi", "step", "bolt", "omni")),
]


def clasificar(modelo: str) -> str:
    bajo = modelo.lower()
    for nombre, claves in CATEGORIAS:
        if any(clave in bajo for clave in claves):
            return nombre
    return "otros"


def mostrar_modelos(router: RouterNVIDIA) -> None:
    modelos = router.modelos()
    print(f"{CABECERA_AYUDA} — {len(modelos)} modelos en el catálogo público\n")
    grupos: dict[str, list[str]] = {}
    for modelo in modelos:
        grupos.setdefault(clasificar(modelo), []).append(modelo)
    orden = [n for n, _ in CATEGORIAS] + ["otros"]
    for nombre in orden:
        if nombre not in grupos:
            continue
        print(f"  {nombre.upper()}")
        for modelo in grupos[nombre]:
            print(f"    {modelo}")
        print()


# ---------------------------------------------------------------------------
# Autoprueba (sin red, sin clave real)
# ---------------------------------------------------------------------------
def autoprueba() -> int:
    """Levanta un servidor NVIDIA falso y verifica cupos, respaldo y registro."""
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    estado = {"modelos": ["nvidia/nemotron-3-ultra-550b-a55b", "deepseek-ai/deepseek-v4.1-flash",
                          "nvidia/nemotron-3.5-embed-1b"],
              "vistos": []}

    class Manejador(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def _responder(self, codigo: int, cuerpo: dict) -> None:
            datos = json.dumps(cuerpo).encode()
            self.send_response(codigo)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(datos)))
            self.end_headers()
            self.wfile.write(datos)

        def do_GET(self):
            if self.path.endswith("/models"):
                return self._responder(200, {"data": [{"id": m} for m in estado["modelos"]]})
            self._responder(404, {"error": "no encontrado"})

        def do_POST(self):
            largo = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(largo) or b"{}")
            modelo = payload.get("model", "")
            estado["vistos"].append(modelo)
            if self.path.endswith("/chat/completions"):
                if modelo == "nvidia/nemotron-3-ultra-550b-a55b":
                    return self._responder(429, {"error": "rate limit"})
                return self._responder(200, {
                    "choices": [{"message": {"content": "  respuesta de prueba  "}}],
                    "usage": {"prompt_tokens": 11, "completion_tokens": 5},
                })
            if self.path.endswith("/embeddings"):
                entradas = payload.get("input") or []
                return self._responder(200, {
                    "data": [{"embedding": [0.1, 0.2, 0.3]} for _ in entradas],
                    "usage": {"prompt_tokens": len(entradas)},
                })
            self._responder(404, {"error": "no encontrado"})

    servidor = ThreadingHTTPServer(("127.0.0.1", 0), Manejador)
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    puerto = servidor.server_address[1]

    tmp = Path(os.environ.get("TMPDIR", "/tmp")) / f"nvidia_router_prueba_{os.getpid()}.json"
    if tmp.exists():
        tmp.unlink()

    config = {
        "servidor": {"base_url": f"http://127.0.0.1:{puerto}/v1", "timeout_s": 10,
                     "reintentos_por_modelo": 1},
        "limites": {"rpm_global": 50, "llamadas_dia": 100,
                    "por_modelo": {"deepseek-ai/deepseek-v4.1-flash": {"rpm": 1, "dia": 100},
                                   "nvidia/nemotron-3.5-embed-1b": {"rpm": 20, "dia": 100}},
                    "por_defecto": {"rpm": 8, "dia": 100}},
        "tareas": {
            "redaccion": {"candidatos": ["nvidia/nemotron-3-ultra-550b-a55b",
                                         "deepseek-ai/deepseek-v4.1-flash"],
                          "parametros": {"temperature": 0.2, "max_tokens": 16}},
            "embeddings": {"candidatos": ["nvidia/nemotron-3.5-embed-1b"],
                           "parametros": {"lote": 2}},
        },
    }
    router = RouterNVIDIA(config=config, clave="nvapi-prueba", registro=Registro(tmp))
    fallos = 0

    def comprobar(condicion: bool, texto: str) -> None:
        nonlocal fallos
        print(("  ok   " if condicion else "  FALLA") + "  " + texto)
        if not condicion:
            fallos += 1

    print(f"{CABECERA_AYUDA} — autoprueba contra servidor local\n")

    catalogo = router.modelos()
    comprobar(len(catalogo) == 3, f"catálogo leído del servidor ({len(catalogo)} modelos)")

    resultado = router.chat("redaccion", [{"role": "user", "content": "hola"}])
    comprobar(estado["vistos"][:1] == ["nvidia/nemotron-3-ultra-550b-a55b"],
              "se intenta primero el modelo preferente de la tarea")
    comprobar(resultado["modelo"] == "deepseek-ai/deepseek-v4.1-flash",
              "respaldo automático cuando el preferente responde 429")
    comprobar(resultado["texto"] == "respuesta de prueba", "respuesta sin espacios sobrantes")
    comprobar(resultado["uso"]["entrada"] == 11 and resultado["uso"]["salida"] == 5,
              "tokens contabilizados")
    comprobar(any(b["resultado"] == "sin cupo" for b in resultado["bitacora"]),
              "el 429 queda anotado en la bitácora")

    # El respaldo tiene rpm=1 y ya se usó: la siguiente llamada no debe tener cupo.
    try:
        router.chat("redaccion", [{"role": "user", "content": "otra"}])
        comprobar(False, "segunda llamada bloqueada por cuota por minuto")
    except RuntimeError as error:
        comprobar("Ningún modelo pudo atender" in str(error),
                  "segunda llamada bloqueada por cuota por minuto")

    vectores = router.embeddings(["uno", "dos", "tres"])
    comprobar(len(vectores["vectores"]) == 3, "embeddings por lotes (3 textos)")

    registro = Registro(tmp)
    comprobar(registro.total_hoy() >= 3, "el registro sobrevive en disco")
    comprobar(registro.llamadas_hoy("deepseek-ai/deepseek-v4.1-flash") == 1,
              "conteo por modelo persistido (1 llamada efectiva)")
    comprobar(registro.llamadas_hoy("nvidia/nemotron-3-ultra-550b-a55b") == 1,
              "el intento rechazado con 429 también queda contado")
    comprobar(registro.tokens_hoy()[0] >= 13, "tokens de todos los modelos sumados")

    # Derivación a un CLI de agente simulado: verifica armado del comando,
    # escritura del material y lectura del JSON de vuelta.
    guion = tmp.parent / f"cli_falso_{os.getpid()}.sh"
    guion.write_text(
        "#!/bin/sh\n"
        'cat <<JSON\n'
        '{"result":"  texto del cli  ","usage":{"input_tokens":7,"output_tokens":3},'
        '"session_id":"abc-123"}\n'
        "JSON\n",
        encoding="utf-8",
    )
    guion.chmod(0o755)
    config["derivacion"] = {
        "falso": {"ejecutable": str(guion), "timeout_s": 30, "modelos": {"tarea": "modelo-x"},
                  "instrucciones": {"tarea": "resume el material"}},
    }
    carpeta = tmp.parent / f"wd_{os.getpid()}"
    salida = derivar(config, "falso", "tarea", "material de prueba", carpeta)
    comprobar(salida["texto"] == "texto del cli", "derivación a CLI: respuesta parseada y limpia")
    comprobar(salida["uso"]["entrada"] == 7, "derivación a CLI: tokens leídos del JSON")
    comprobar((carpeta / ".derivacion_tarea.md").read_text(encoding="utf-8") == "material de prueba",
              "derivación a CLI: el material queda en el directorio de trabajo")

    motor_apagado = {"claude": {"ejecutable": str(guion), "habilitado": False, "nota": "sin sesión"}}
    try:
        derivar({"derivacion": motor_apagado}, "claude", "tarea", "x", carpeta,
                instruccion="haz algo")
        comprobar(False, "un motor deshabilitado se rechaza con explicación")
    except SystemExit as error:
        comprobar("sin sesión" in str(error), "un motor deshabilitado se rechaza con explicación")

    guion.unlink(missing_ok=True)
    for archivo in carpeta.glob("*"):
        archivo.unlink()
    carpeta.rmdir()

    tmp.unlink(missing_ok=True)
    servidor.shutdown()
    print(f"\n{'AUTOPRUEBA OK' if fallos == 0 else f'{fallos} comprobaciones fallidas'}")
    return 0 if fallos == 0 else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def leer_entrada(args) -> str:
    if args.archivo:
        return Path(args.archivo).read_text(encoding="utf-8")
    if args.texto:
        return args.texto
    if not sys.stdin.isatty():
        return sys.stdin.read()
    sys.exit("Falta el contenido: usa --texto, --archivo o envía el texto por stdin.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=CABECERA_AYUDA,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Clave gratuita en https://build.nvidia.com/settings/api-keys",
    )
    parser.add_argument("comando", nargs="?",
                        choices=["estado", "modelos", "llamar", "embeddings", "derivar"],
                        help="estado: cupos de hoy · modelos: catálogo · llamar / embeddings: "
                             "inferencia · derivar: entregar la tarea a un CLI de agente")
    parser.add_argument("--tarea", help="tarea editorial (por defecto: redaccion; "
                                        "embeddings y derivar eligen la suya)")
    parser.add_argument("--texto", help="contenido de la petición")
    parser.add_argument("--archivo", help="archivo con el contenido de la petición")
    parser.add_argument("--sistema", help="instrucción de sistema previa")
    parser.add_argument("--motor", help="para 'derivar': agy | claude")
    parser.add_argument("--modelo", help="para 'derivar': fuerza un modelo del CLI")
    parser.add_argument("--instruccion", help="para 'derivar': qué debe hacer el CLI con el material")
    parser.add_argument("--workdir", help="para 'derivar': carpeta de trabajo del CLI")
    parser.add_argument("--max-tokens", type=int)
    parser.add_argument("--temperatura", type=float)
    parser.add_argument("--json", action="store_true", help="salida en JSON")
    parser.add_argument("--autoprueba", action="store_true", help="prueba local sin red ni clave")
    args = parser.parse_args()

    if args.autoprueba:
        return autoprueba()
    if not args.comando:
        parser.print_help()
        return 2

    if args.comando == "derivar":
        if not args.motor:
            parser.error("derivar requiere --motor (agy o claude)")
        config = cargar_config()
        contenido = leer_entrada(args)
        tarea = args.tarea or "pase_final"
        workdir = Path(args.workdir) if args.workdir else BASE / ".derivaciones"
        try:
            resultado = derivar(config, args.motor, tarea, contenido, workdir,
                                instruccion=args.instruccion, modelo=args.modelo)
        except (SystemExit, RuntimeError) as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1
        animar_derivacion(config, resultado, Registro())
        if args.json:
            print(json.dumps(resultado, ensure_ascii=False, indent=2))
        else:
            print(resultado["texto"])
            uso = resultado["uso"]
            costo = (f" · costo teórico USD {uso['costo_usd']:.3f} (el plan no lo cobra)"
                     if uso.get("costo_usd") else " · sin costo por token")
            print(f"\n— {resultado['motor']} · {resultado['modelo']}"
                  + (f" (esfuerzo {resultado['esfuerzo']})" if resultado.get("esfuerzo") else "")
                  + f" · tarea {resultado['tarea']} · "
                  f"{uso['total']} tokens ({uso['entrada']} entrada"
                  + (f", {uso['cache']} de caché" if uso.get("cache") else "")
                  + f" / {uso['salida']} salida) · {uso['ms']} ms{costo}", file=sys.stderr)
        return 0

    router = RouterNVIDIA()
    if args.comando == "estado":
        mostrar_estado(router)
        return 0
    if args.comando == "modelos":
        mostrar_modelos(router)
        return 0

    contenido = leer_entrada(args)
    if args.comando == "embeddings":
        textos = [t for t in contenido.split("\n\n") if t.strip()] or [contenido]
        try:
            resultado = router.embeddings(textos, tarea=args.tarea or "embeddings")
        except RuntimeError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1
        print(json.dumps(resultado) if args.json
              else f"{len(resultado['vectores'])} vectores de {resultado['dimension']} dimensiones "
                   f"con {resultado['modelo']}")
        return 0

    mensajes = []
    if args.sistema:
        mensajes.append({"role": "system", "content": args.sistema})
    mensajes.append({"role": "user", "content": contenido})
    try:
        resultado = router.chat(args.tarea or "redaccion", mensajes, max_tokens=args.max_tokens,
                                temperatura=args.temperatura)
    except (RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    else:
        print(resultado["texto"])
        if resultado.get("aviso"):
            print(f"⚠ {resultado['aviso']}", file=sys.stderr)
        print(f"\n— {resultado['modelo']} · tarea {resultado['tarea']} · "
              f"{resultado['uso']['entrada']}+{resultado['uso']['salida']} tokens · "
              f"{resultado['uso']['ms']} ms", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
