# MediaInsight - Engenharia de Dados e Marketing Analytics

Projeto de Engenharia de Dados, Analytics e Business Intelligence desenvolvido com dados históricos do Google Analytics 4 (GA4).

O objetivo é construir uma solução de dados **end-to-end**, desde a ingestão e o tratamento de eventos digitais até a criação de indicadores analíticos para apoiar decisões de marketing.

O projeto utiliza Python, SQL, DuckDB, testes automatizados e boas práticas de Engenharia de Software, com preparação dos dados para consumo no Power BI.

## 1. Objetivo do projeto

Simular um cenário de Engenharia de Dados e Marketing Analytics no qual uma equipe de marketing precisa transformar dados de navegação e comportamento digital em informações confiáveis.

A solução busca responder perguntas como:

- Quantos usuários e sessões o site recebeu?
- Qual foi o volume de visualizações de páginas?
- Quantos eventos de compra foram registrados?
- Qual foi a taxa de conversão por sessão?
- Como os indicadores variam por origem de aquisição e dispositivo?
- Como os eventos estão distribuídos pelas etapas da jornada de compra?

O projeto também demonstra práticas de qualidade, rastreabilidade, reconciliação e automação de pipelines de dados.

## 2. Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python 3.12 | Desenvolvimento dos pipelines e automações |
| UV | Gerenciamento de dependências e ambiente virtual |
| DuckDB | Armazenamento e processamento analítico |
| SQL | Transformação, modelagem e agregação |
| pytest | Testes automatizados |
| Ruff | Análise estática e formatação |
| Power BI | Visualização e Business Intelligence (em desenvolvimento) |
| Git e GitHub | Versionamento e documentação |

**Ambiente de desenvolvimento:** Windows, VS Code e PowerShell.

## 3. Fonte de dados

O projeto utiliza dados históricos do conjunto público Google Analytics 4 — Google Merchandise Store, disponibilizado no BigQuery.

Os dados são ofuscados e utilizados exclusivamente para fins educacionais.

**Período atualmente processado:** 01/11/2020.

**Volume de eventos:** 31.272 registros.

A amostra de um único dia limita análises temporais, sazonalidade e inferências sobre o comportamento dos usuários.

## 4. Arquitetura da solução

```text
Google Analytics 4
        |
        v
Extração de dados
        |
        v
Bronze
Ingestão e preservação dos dados
        |
        v
Silver
Padronização, tipagem e qualidade
        |
        v
Gold
Modelagem e indicadores de marketing
        |
        v
Python + DuckDB
Exportação automatizada
        |
        v
Arquivos CSV
        |
        v
Power BI Desktop
Dashboard executivo (em desenvolvimento)
```

A arquitetura segue o conceito de camadas de dados, separando ingestão, tratamento e consumo analítico.

### Bronze — Ingestão

Responsável por carregar os eventos de origem, preservando os dados para processamento posterior.

### Silver — Transformação e qualidade

Responsável pela padronização dos campos, conversão de tipos, tratamento de valores e aplicação de regras de qualidade.

### Gold — Modelagem analítica

Responsável pela criação de tabelas agregadas e indicadores destinados ao consumo por ferramentas de BI.

## 5. Estrutura do projeto

Principais diretórios e arquivos:

```text
mediainsight/
|
|-- data/
|   |-- bronze/
|   |-- silver/
|   |-- exports/
|       |-- powerbi/
|
|-- docs/
|   |-- etapa_03_silver.md
|   |-- metricas_gold.md
|
|-- scripts/
|   |-- audit_gold.py
|   |-- export_powerbi.py
|
|-- sql/
|   |-- silver/
|   |-- gold/
|       |-- 001_marketing_daily.sql
|       |-- 002_acquisition_performance.sql
|       |-- 003_device_performance.sql
|       |-- 004_conversion_funnel.sql
|
|-- src/
|   |-- mediainsight/
|       |-- gold.py
|       |-- run_gold.py
|
|-- tests/
|   |-- test_gold.py
|   |-- test_gold_pipeline.py
|
|-- .gitignore
|-- pyproject.toml
|-- uv.lock
|-- README.md
```

A estrutura apresentada destaca os principais componentes. Outros módulos de configuração, ingestão, transformação e testes também fazem parte do projeto.

Os arquivos de dados e exportações locais não precisam ser publicados no repositório.

## 6. Etapas de desenvolvimento

| Etapa | Descrição | Status |
|---|---|---|
| 1 | Fundação técnica e arquitetura | Concluída |
| 2 | Ingestão Bronze | Concluída |
| 3 | Transformação e qualidade Silver | Concluída |
| 4 | Modelagem Gold e Marketing Analytics | Concluída |
| 5 | Integração e dashboard Power BI | Em desenvolvimento |

### Etapa 1 — Fundação técnica

Configuração do ambiente Python, gerenciamento de dependências com UV, organização do projeto, conexão com DuckDB e estrutura inicial de testes.

### Etapa 2 — Ingestão Bronze

Implementação da ingestão dos eventos GA4, validação dos arquivos de entrada e mecanismos para evitar duplicações em reprocessamentos.

### Etapa 3 — Transformação Silver

Implementação de regras de limpeza, padronização e conversão de tipos.

A camada Silver disponibiliza dados estruturados para a construção dos indicadores analíticos.

### Etapa 4 — Modelagem Gold

Construção de quatro tabelas analíticas com SQL e DuckDB, incluindo automação, testes, auditoria e reconciliação com a Silver.

### Etapa 5 — Integração com Power BI

Desenvolvimento de um exportador Python que prepara os dados Gold para consumo no Power BI.

A exportação CSV está concluída. A modelagem e o dashboard no Power BI ainda estão em desenvolvimento.

## 7. Camada Gold — Indicadores de Marketing

Foram implementadas quatro tabelas analíticas.

| Tabela | Finalidade |
|---|---|
| `gold.marketing_daily` | Consolidar indicadores diários |
| `gold.acquisition_performance` | Analisar origem e mídia de primeira aquisição |
| `gold.device_performance` | Comparar indicadores por dispositivo |
| `gold.conversion_funnel` | Analisar a distribuição dos eventos da jornada de compra |

### Resultados consolidados

Dados referentes a 01/11/2020:

| Indicador | Resultado |
|---|---:|
| Eventos processados | 31.272 |
| Usuários distintos | 2.365 |
| Sessões distintas | 2.625 |
| Visualizações de página | 9.767 |
| Eventos de engajamento | 8.667 |
| Eventos de compra | 14 |
| Sessões com compra | 13 |
| Taxa de conversão por sessão | 0,50% |
| Receita registrada | 773,00 |
| Receita por sessão | 0,29 |

A moeda da receita não foi confirmada na extração e, portanto, os valores monetários são apresentados sem símbolo de moeda.

A taxa de conversão corresponde à proporção de sessões distintas com pelo menos um evento de compra.

### Análise do funil de conversão

| Etapa | Evento | Quantidade |
|---:|---|---:|
| 1 | `view_item` | 3.380 |
| 2 | `add_to_cart` | 4 |
| 3 | `begin_checkout` | 127 |
| 4 | `add_payment_info` | 73 |
| 5 | `purchase` | 14 |

**Observação analítica:** o funil representa contagens de eventos, não a progressão sequencial dos mesmos usuários. Por isso, não deve ser utilizado diretamente para calcular taxas de abandono entre etapas.

Os campos `first_user_source` e `first_user_medium` representam a primeira aquisição do usuário e não a atribuição da sessão.

## 8. Engenharia de Software e qualidade de dados

O projeto incorpora práticas para melhorar a confiabilidade e a manutenção do pipeline.

Entre elas:

- Organização modular do código Python.
- Transformações SQL versionadas.
- Separação das responsabilidades por camada.
- Validação dos dados de entrada.
- Processamento idempotente.
- Testes automatizados.
- Reconciliação entre Silver e Gold.
- Transações com rollback em caso de falha.
- Auditoria dos indicadores.
- Padronização com Ruff.
- Versionamento com Git.

### Resultado dos testes

Última validação realizada:

```text
35 passed in 2.06s
```

Os testes abrangem configuração, banco de dados, ingestão, transformação, modelagem Gold e execução do pipeline Gold.

A exportação para Power BI foi validada por execução e conferência dos arquivos, mas ainda não possui testes automatizados específicos.

## 9. Etapa 5 — Integração com Power BI

### Objetivo

Preparar as tabelas Gold para utilização no Power BI Desktop, permitindo a construção de relatórios gerenciais e dashboards de marketing digital.

### Implementação do exportador

Foi desenvolvido o script:

`scripts/export_powerbi.py`

Ele realiza as seguintes operações:

1. Verifica a existência do banco DuckDB.
2. Abre uma conexão somente para leitura.
3. Consulta as quatro tabelas Gold.
4. Ordena os registros conforme suas dimensões.
5. Exporta os dados para CSV com cabeçalho.
6. Consulta e apresenta a quantidade de registros de cada tabela.

A exportação utiliza o comando SQL `COPY` do DuckDB.

### Tabelas exportadas

| Arquivo CSV | Registros |
|---|---:|
| `marketing_daily.csv` | 1 |
| `acquisition_performance.csv` | 9 |
| `device_performance.csv` | 3 |
| `conversion_funnel.csv` | 5 |

**Total:** 18 registros distribuídos entre quatro arquivos analíticos.

Os CSVs são gerados em:

```text
data/exports/powerbi/
```

A exportação é reproduzível e não modifica as tabelas do banco.

## 10. Como executar o projeto

### Pré-requisitos

- Python 3.12.
- UV instalado.
- Git.
- Power BI Desktop para as etapas de visualização.
- Arquivo de entrada GA4 disponível para o pipeline de ingestão.

O banco local e os dados de entrada não são distribuídos automaticamente pelo repositório.

### Clonar o repositório

```powershell
git clone https://github.com/rafaelporfiriobarros/mediainsight.git

cd mediainsight
```

### Instalar as dependências

```powershell
uv sync
```

### Executar o diagnóstico

```powershell
uv run mediainsight
```

### Executar a transformação Silver

```powershell
uv run mediainsight-transform
```

### Construir as tabelas Gold

```powershell
uv run mediainsight-gold
```

### Executar a auditoria Gold

```powershell
uv run python scripts/audit_gold.py
```

### Exportar dados para Power BI

```powershell
uv run python scripts/export_powerbi.py
```

**Importante:** os comandos de transformação e exportação dependem da existência das camadas anteriores. Em uma instalação nova, é necessário preparar e ingerir os dados de origem antes de executar a Silver e a Gold.

### Verificar os arquivos exportados

```powershell
Get-ChildItem .\data\exports\powerbi\
```

### Verificar a ordenação do funil

```powershell
Import-Csv .\data\exports\powerbi\conversion_funnel.csv |
    Select-Object step_order, event_name, total_events |
    Format-Table -AutoSize
```

## 11. Executar os testes e validações

### Testes automatizados

```powershell
uv run pytest -v
```

### Análise estática

```powershell
uv run ruff check .
```

### Verificação de formatação

```powershell
uv run ruff format --check .
```

Últimos resultados registrados:

| Verificação | Resultado |
|---|---|
| pytest | 35 testes aprovados |
| Ruff — lint | Aprovado |
| Ruff — formatação | 24 arquivos formatados |
| Auditoria Gold | Aprovada |
| Exportação CSV | Aprovada |
| Ordenação do funil | Validada |

## 12. Limitações do projeto

As principais limitações atuais são:

- A amostra contém eventos de apenas um dia.
- Os dados GA4 são históricos e ofuscados.
- A moeda dos valores de receita não foi confirmada.
- Eventos de compra não devem ser interpretados automaticamente como transações únicas.
- Métricas distintas, como usuários e sessões, não devem ser somadas indiscriminadamente entre agrupamentos.
- Os campos de primeira aquisição não representam atribuição de sessão.
- O funil não acompanha necessariamente a progressão sequencial dos mesmos usuários.
- O dashboard Power BI ainda não foi concluído.

Essas limitações devem ser consideradas na interpretação dos indicadores e na elaboração de recomendações de negócio.

## 13. Próximas atividades

A continuidade da Etapa 5 contempla:

1. Importação dos CSVs no Power BI Desktop.
2. Preparação e tipagem dos dados no Power Query.
3. Modelagem das tabelas analíticas.
4. Desenvolvimento de medidas DAX.
5. Construção de indicadores e gráficos executivos.
6. Análise de aquisição, dispositivos e conversão.
7. Validação dos resultados com DuckDB.
8. Documentação e publicação das evidências do dashboard.

## 14. Documentação complementar

- `docs/etapa_03_silver.md` — Transformação e qualidade da camada Silver.
- `docs/metricas_gold.md` — Definições e regras dos indicadores Gold.
- `scripts/audit_gold.py` — Auditoria e reconciliação dos indicadores.
- `scripts/export_powerbi.py` — Exportação das tabelas Gold para Power BI.

## 15. Finalidade

O MediaInsight é um projeto educacional e de portfólio, desenvolvido para demonstrar conhecimentos práticos em:

- Engenharia de Dados.
- Engenharia de Software.
- SQL e modelagem analítica.
- Qualidade e confiabilidade de dados.
- Automação de pipelines.
- Marketing Analytics.
- Business Intelligence.

**Este projeto é independente e não possui vínculo com a Agência Africa.**

---

**Status atual:** Etapas 1 a 4 concluídas. Etapa 5 em desenvolvimento, com exportação das tabelas Gold para Power BI concluída e validada.