# CLAUDE.md – Claude Code CLI Guidelines
# Project: Última Prensa IA Journalism Kit

This repository contains the **Investigative Journalism Framework** for Última Prensa (ultimaprensa.cl).

## CLI Agent Guidelines

When operating via Claude Code CLI (`claude`):

1. **Editorial Guidelines:** Always adhere to the standards defined in `AGENTS.md` and `skills/ultimaprensa-reportajes/SKILL.md`.
2. **Fact-Checking:** Prioritize primary official documents (CGR audits, TRICEL/TER sentences, public procurement records).
3. **Grammar & Style:**
   - Headlines and subheaders MUST NOT have trailing periods.
   - Use active verbs; avoid rumors and speculative conditional tenses.
   - Maintain zero circular redundancy and apply progressive enrichment.
4. **Template Management:** When the user asks to start an investigation, copy `_plantilla_reportaje/` into `reportajes/[nombre_del_caso]/`.

## Useful Commands

- OCR scanned rulings: `python scripts/ocr_sentencias_pdf.py <input.pdf> <output.txt>`
- Municipal Solvency Ratios: `python scripts/calculo_ratios_municipales.py`
