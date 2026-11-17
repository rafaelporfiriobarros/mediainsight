# MediaInsight - Ambiente Docker

## 1. Objetivo

O MediaInsight é um projeto de Engenharia de Dados e Marketing Analytics que utiliza dados de eventos do Google Analytics 4 (GA4) para construir indicadores analíticos.

A containerização permite executar as transformações e os testes em um ambiente Python reproduzível, reduzindo diferenças entre máquinas de desenvolvimento.

## 2. Tecnologias utilizadas

- Python 3.12
- UV — gerenciamento de dependências
- Docker e Docker Compose
- DuckDB — banco de dados analítico
- SQL — transformação e modelagem
- Pytest — testes automatizados
- Ruff — qualidade e formatação do código
- Power BI — visualização dos dados exportados

## 3. Arquitetura

O projeto utiliza uma arquitetura de dados em três camadas:

```text
CSV GA4
   |
   v
BRONZE — Eventos brutos
   |
   v
SILVER — Limpeza e padronização
   |
   v
GOLD — Indicadores analíticos
   |
   v
CSV — Exportação para Power BI
```

O DuckDB armazena as tabelas Bronze, Silver e Gold em um arquivo local.

O Docker executa a aplicação Python e os scripts SQL. O diretório de dados é disponibilizado ao container por meio de um bind mount.

Não é necessário executar um servidor PostgreSQL ou DuckDB.

## 4. Estrutura dos arquivos Docker

```text
mediainsight/
├── Dockerfile
├── compose.yaml
├── .dockerignore
├── pyproject.toml
├── uv.lock
├── src/
├── sql/
├── scripts/
├── tests/
├── data/
└── docs/
    └── docker.md
```

**Dockerfile:** define a imagem da aplicação, instala as dependências com UV e configura o ambiente de execução.

**compose.yaml:** descreve o serviço e monta o diretório local `data/` em `/app/data`.

**.dockerignore:** impede que bancos locais, dados, credenciais, caches e outros arquivos desnecessários sejam enviados ao contexto de construção da imagem.

## 5. Pré-requisitos

- Docker Desktop instalado e em execução.
- Docker Compose disponível.
- Git para clonar o repositório.
- Arquivo DuckDB existente para executar as transformações Silver e Gold.

O projeto utiliza dados locais que não são distribuídos na imagem Docker.

## 6. Construir a imagem

Na raiz do repositório:

```powershell
docker build -t mediainsight:dev .
```

Alternativamente:

```powershell
docker compose build
```

## 7. Executar os testes automatizados

```powershell
docker compose run --rm mediainsight
```

A execução validada em 17/11/2026 apresentou:

**35 testes aprovados.**

Para executar o Ruff:

```powershell
docker compose run --rm mediainsight ruff check .
```

```powershell
docker compose run --rm mediainsight ruff format --check .
```

## 8. Executar o pipeline com dados isolados

Para proteger o banco original, recomenda-se utilizar um diretório de validação.

Com o banco original fechado e sem transações pendentes, no PowerShell:

```powershell
New-Item -ItemType Directory -Path .\data\docker_validation -Force

Copy-Item `
    .\data\mediainsight.duckdb `
    .\data\docker_validation\mediainsight.duckdb
```

### 8.1. Transformação Silver

```powershell
docker run --rm `
  --mount "type=bind,source=$((Resolve-Path .\data\docker_validation).Path),target=/app/data" `
  mediainsight:dev `
  mediainsight-transform
```

### 8.2. Modelagem Gold

```powershell
docker run --rm `
  --mount "type=bind,source=$((Resolve-Path .\data\docker_validation).Path),target=/app/data" `
  mediainsight:dev `
  mediainsight-gold
```

### 8.3. Exportação Power BI

```powershell
docker run --rm `
  --mount "type=bind,source=$((Resolve-Path .\data\docker_validation).Path),target=/app/data" `
  mediainsight:dev `
  python scripts/export_powerbi.py
```

Os arquivos serão gravados em:

```text
data/docker_validation/exports/powerbi/
```

## 9. Resultados da validação

Em 17/11/2026, o pipeline foi executado com sucesso no Docker.

| Indicador | Resultado |
|---|---:|
| Eventos Bronze | 31.272 |
| Eventos Silver | 31.272 |
| Registros rejeitados | 0 |
| Marketing diário | 1 registro |
| Performance por aquisição | 9 registros |
| Performance por dispositivo | 3 registros |
| Funil de conversão | 5 registros |
| CSVs exportados | 4 |
| Testes automatizados | 35 aprovados |

A construção da Gold retornou `SUCCESS`, incluindo as verificações internas de reconciliação.

## 10. Segurança e boas práticas

- Não incluir bancos DuckDB ou arquivos de backup na imagem.
- Não publicar credenciais no GitHub.
- Utilizar `.dockerignore` para reduzir o contexto de construção.
- Utilizar `.gitignore` para proteger arquivos locais.
- Executar transformações em cópias isoladas antes de alterar o banco principal.
- Manter o arquivo `uv.lock` versionado para reproduzir as dependências.
- Executar testes automatizados antes de publicar alterações.

## 11. Limitações atuais

O projeto utiliza dados GA4 referentes a 01/11/2020. Portanto, os resultados demonstram um recorte de um único dia, não tendências históricas.

A ingestão Bronze utiliza substituição de tabelas. Assim, novas ingest