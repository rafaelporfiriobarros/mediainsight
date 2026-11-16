
# MediaInsight

Projeto de Engenharia de Dados e Marketing Analytics com dados
históricos do Google Analytics 4.

## Objetivo

Construir um pipeline de dados simples e reproduzível,
transformando eventos de aquisição e comportamento digital
em indicadores para Business Intelligence.

## Tecnologias

- Python 3.12
- UV
- DuckDB
- SQL
- pytest
- Ruff
- Power BI
- Git e GitHub

## Fonte de dados

Google Merchandise Store — GA4 Public Dataset.

Os dados são históricos e ofuscados.

## Como executar

Instalar dependências:

```powershell
uv sync
```

Executar diagnóstico:

```powershell
uv run mediainsight
```

Executar testes:

```powershell
uv run pytest -v
```

Validar qualidade:

```powershell
uv run ruff check .
uv run ruff format --check .
```

## Status

Etapa 1 — Fundação técnica em desenvolvimento.

## Próximas etapas

1. Ingestão dos dados.
2. Transformação e qualidade.
3. Modelagem analítica.
4. Dashboard Power BI.
5. Validação e publicação final.

## Finalidade

Projeto educacional e de portfólio.
Não possui vínculo com a Agência Africa.
