import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

export const CuracoReel = () => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();

    // Animación de escala de entrada
    const scale = spring({
        fps,
        frame,
        config: { damping: 12 }
    });

    // Contador numérico 1: $0 -> $3.177.732.167
    const montoCondena = Math.floor(
        interpolate(frame, [45, 120], [0, 3177732167], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp'
        })
    );

    // Contador numérico 2: $0 -> $23.964.000.000
    const montoLicitacion = Math.floor(
        interpolate(frame, [150, 225], [0, 23964000000], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp'
        })
    );

    // Opacidades de escenas
    const scene1Opacity = interpolate(frame, [0, 20, 130, 140], [0, 1, 1, 0]);
    const scene2Opacity = interpolate(frame, [140, 155, 270, 285], [0, 1, 1, 0]);
    const scene3Opacity = interpolate(frame, [285, 295], [0, 1]);

    const formatCLP = (num) => '$' + num.toLocaleString('es-CL');

    return (
        <div
            style={{
                flex: 1,
                backgroundColor: '#090d16',
                backgroundImage: 'radial-gradient(circle at 50% 30%, #1e1b4b 0%, #090d16 70%)',
                color: '#ffffff',
                fontFamily: 'system-ui, -apple-system, sans-serif',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                padding: '60px',
                textAlign: 'center',
                position: 'relative',
                overflow: 'hidden'
            }}
        >
            {/* Cintillo Superior */}
            <div
                style={{
                    position: 'absolute',
                    top: '80px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    background: 'rgba(217, 56, 30, 0.2)',
                    border: '1px solid #d9381e',
                    padding: '12px 28px',
                    borderRadius: '9999px',
                    fontSize: '22px',
                    fontWeight: '800',
                    letterSpacing: '2px',
                    color: '#ff6b52'
                }}
            >
                <div
                    style={{
                        width: '14px',
                        height: '14px',
                        backgroundColor: '#d9381e',
                        borderRadius: '50%',
                        boxShadow: '0 0 15px #d9381e'
                    }}
                />
                INVESTIGACIÓN EXCLUSIVA • ÚLTIMA PRENSA
            </div>

            {/* Escena 1: El Fiasco de Curaco */}
            {frame < 145 && (
                <div style={{ opacity: scene1Opacity, transform: `scale(${scale})` }}>
                    <h2
                        style={{
                            fontSize: '44px',
                            fontWeight: '700',
                            color: '#94a3b8',
                            marginBottom: '20px'
                        }}
                    >
                        EL NEGOCIO DE LA BASURA EN OSORNO
                    </h2>
                    <h1
                        style={{
                            fontSize: '72px',
                            fontWeight: '900',
                            lineHeight: 1.15,
                            color: '#ffffff',
                            marginBottom: '40px'
                        }}
                    >
                        El Espejismo de Curaco
                    </h1>
                    <div
                        style={{
                            background: '#111827',
                            border: '2px solid rgba(239, 68, 68, 0.4)',
                            padding: '30px 40px',
                            borderRadius: '24px',
                            boxShadow: '0 20px 50px rgba(0,0,0,0.6)'
                        }}
                    >
                        <div style={{ fontSize: '26px', color: '#f87171', fontWeight: '700', marginBottom: '10px' }}>
                            CONDENA PATRIMONIAL AL MUNICIPIO
                        </div>
                        <div
                            style={{
                                fontSize: '68px',
                                fontFamily: 'monospace',
                                fontWeight: '900',
                                color: '#ef4444'
                            }}
                        >
                            {formatCLP(montoCondena)}
                        </div>
                        <div style={{ fontSize: '22px', color: '#94a3b8', marginTop: '12px' }}>
                            Por daño emergente y rescisión ilegal de contrato
                        </div>
                    </div>
                </div>
            )}

            {/* Escena 2: El Megacontrato de $24.000M y el cambio de nombre */}
            {frame >= 140 && frame < 290 && (
                <div style={{ opacity: scene2Opacity }}>
                    <div style={{ fontSize: '28px', color: '#38bdf8', fontWeight: '800', letterSpacing: '1px', marginBottom: '16px' }}>
                        18 MESES DESPUÉS DE LA CONDENA
                    </div>
                    <h1
                        style={{
                            fontSize: '64px',
                            fontWeight: '900',
                            lineHeight: 1.2,
                            marginBottom: '30px'
                        }}
                    >
                        El Megacontrato a la misma empresa
                    </h1>
                    <div
                        style={{
                            background: '#111827',
                            border: '2px solid rgba(16, 185, 129, 0.4)',
                            padding: '30px 40px',
                            borderRadius: '24px',
                            marginBottom: '30px'
                        }}
                    >
                        <div style={{ fontSize: '24px', color: '#34d399', fontWeight: '700', marginBottom: '8px' }}>
                            LICITACIÓN PÚBLICA 2308-97-LR23 (60 MESES)
                        </div>
                        <div
                            style={{
                                fontSize: '64px',
                                fontFamily: 'monospace',
                                fontWeight: '900',
                                color: '#10b981'
                            }}
                        >
                            {formatCLP(montoLicitacion)}
                        </div>
                    </div>
                    <div
                        style={{
                            background: 'rgba(245, 158, 11, 0.15)',
                            border: '1px solid #f59e0b',
                            padding: '18px 30px',
                            borderRadius: '16px',
                            fontSize: '28px',
                            fontWeight: '700',
                            color: '#fbbf24'
                        }}
                    >
                        ⚡ Servitrans mutó a «Ciudad Limpia» en solo 9 días
                    </div>
                </div>
            )}

            {/* Escena 3: Cierre y Llamado a la Acción */}
            {frame >= 285 && (
                <div style={{ opacity: scene3Opacity }}>
                    <h1 style={{ fontSize: '76px', fontWeight: '900', marginBottom: '24px' }}>
                        Reportaje Completo
                    </h1>
                    <p style={{ fontSize: '32px', color: '#94a3b8', lineHeight: 1.5, maxWidth: '800px', marginBottom: '40px' }}>
                        500 fojas de expedientes periciales, contratos públicos y análisis tributario del SII.
                    </p>
                    <div
                        style={{
                            background: '#d9381e',
                            color: '#ffffff',
                            fontSize: '36px',
                            fontWeight: '800',
                            padding: '24px 60px',
                            borderRadius: '9999px',
                            boxShadow: '0 10px 30px rgba(217, 56, 30, 0.6)'
                        }}
                    >
                        ultimaprensa.cl
                    </div>
                </div>
            )}

            {/* Pie de Página */}
            <div
                style={{
                    position: 'absolute',
                    bottom: '60px',
                    fontSize: '20px',
                    color: '#64748b',
                    letterSpacing: '1px'
                }}
            >
                PERIODISMO DE INVESTIGACIÓN Y DATOS PÚBLICOS
            </div>
        </div>
    );
};
