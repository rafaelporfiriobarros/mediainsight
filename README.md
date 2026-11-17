# MediaInsight - Engenharia de Dados e Marketing Analytics

**Pipeline de dados de marketing digital com Python, SQL, DuckDB e Docker, preparado para análises no Power BI.**

O MediaInsight é um projeto educacional de **Engenharia de Dados, Engenharia de Software e Analytics** que transforma eventos históricos do Google Analytics 4 (GA4) em tabelas analíticas confiáveis. O projeto cobre ingestão, transformação, modelagem, validação, testes automatizados e exportação para BI.

> **Status (17/11/2026):** camadas Bronze, Silver e Gold concluídas; execução com Docker validada e publicada; exportação para Power BI concluída. **Dashboard no Power BI Desktop em desenvolvimento.**

## 1. Problema de negócio

Uma equipe de marketing precisa acompanhar navegação, aquisição e conversão, mas os eventos brutos do site não estão prontos para análises gerenciais. É necessário organizar os dados, padronizar campos, definir métricas e verificar sua consistência antes de utilizá-los em relatórios.

O projeto busca responder:

- Quantos eventos, usuários e sessões foram registrados?
- Qual foi o volume de visualizações de página e de eventos de compra?
- Qual a proporção de sessões com pelo menos uma compra?
- Como os indicadores se distribuem por **primeira origem/mídia de aquisição** e por dispositivo?
- Quantos eventos foram registrados em cada etapa selecionada da jornada de compra?

**Entrega:** quatro tabelas Gold, auditadas e exportadas em CSV para consumo analítico.

## 2. Resultados validados

A amostra atualmente processada corresponde a **01/11/2020** e contém **31.272 eventos**.

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

A **taxa de conversão por sessão** considera as sessões distintas com pelo menos um evento de compra, divididas pelo total de sessões. Os valores de receita estão apresentados **sem símbolo monetário**, pois a moeda não foi confirmada na extração.

### Qualidade e entregas

| Verificação ou entrega | Resultado |
|---|---|
| Reconciliação Bronze → Silver | 31.272 → 31.272 eventos |
| Registros rejeitados na transformação validada | 0 |
| Tabelas analíticas Gold | 4 |
| Arquivos CSV exportados | 4 |
| Testes automatizados em Docker | **35 aprovados** |
| Ruff lint | Aprovado |
| Ruff formatação no Docker | 21 arquivos já formatados |
| Auditoria e reconciliação Gold | Aprovadas |

Esses números descrevem a execução validada do projeto; não representam indicadores de uma operação de marketing em produção.

## 3. Arquitetura da solução

```text
Dados históricos GA4 (arquivo CSV de entrada)
                    |
                    v
         Bronze — Ingestão
         Eventos e metadados
                    |
                    v
       Silver — Transformação
      Tipagem, limpeza e validação
                    |
                    v
       Gold — Modelagem analítica
         SQL + agregações
                    |
                    v
       Exportação automatizada
             Quatro CSVs
                    |
                    v
        Power BI Desktop
       (dashboard em andamento)

Infraestrutura transversal: Python 3.12 + DuckDB + UV
Qualidade e execução: pytest + Ruff + Docker + Git
```

A separação em camadas facilita o desenvolvimento, a auditoria e o consumo das métricas. O DuckDB é utilizado como mecanismo analítico nas diferentes etapas do pipeline, e não apenas na exportação.

### Camadas

- **Bronze:** ingestão dos eventos de origem e registro de metadados.
- **Silver:** padronização, tipagem e validações para preparar os dados analíticos.
- **Gold:** tabelas agregadas e indicadores para análise de marketing.

## 4. Fonte dos dados e cuidados analíticos

O projeto utiliza uma extração em CSV de dados históricos e ofuscados do conjunto público **Google Analytics 4 — Google Merchandise Store**, disponibilizado no BigQuery. A amostra processada contém apenas **um dia: 01/11/2020**.

Essa restrição impede conclusões confiáveis sobre tendências, sazonalidade e evolução temporal. Além disso:

- Os campos `first_user_source` e `first_user_medium` representam **primeira aquisição do usuário**, não atribuição de sessão.
- Eventos de `purchase` não equivalem necessariamente a transações únicas.
- Usuários e sessões distintos não devem ser somados indiscriminadamente entre agrupamentos.
- A moeda associada à receita não foi confirmada.
- As contagens do funil são **eventos**, não uma trajetória sequencial comprovada dos mesmos usuários; não devem ser usadas diretamente para calcular abandono entre etapas.

## 5. Tecnologias

| Tecnologia | Utilização |
|---|---|
| Python 3.12 | Ingestão, transformações, auditoria e exportação |
| SQL | Regras de transformação e tabelas analíticas |
| DuckDB | Armazenamento e consultas analíticas |
| UV | Dependências e ambiente Python |
| Docker / Docker Compose | Execução reproduzível e testes isolados |
| pytest | Testes automatizados |
| Ruff | Lint e formatação |
| Git / GitHub | Versionamento e publicação |
| Power BI Desktop | Consumo analítico e dashboard (em desenvolvimento) |

**Ambiente de desenvolvimento:** Windows, VS Code e PowerShell.

## 6. Modelagem Gold

| Tabela | Objetivo | Registros exportados |
|---|---|---:|
| `gold.marketing_daily` | Consolidar indicadores do dia | 1 |
| `gold.acquisition_performance` | Comparar primeira origem/mídia de aquisição | 9 |
| `gold.device_performance` | Comparar indicadores por dispositivo | 3 |
| `gold.conversion_funnel` | Contar eventos selecionados da jornada | 5 |

### Eventos selecionados para o funil

| Ordem | Evento | Contagem |
|---:|---|---:|
| 1 | `view_item` | 3.380 |
| 2 | `add_to_cart` | 4 |
| 3 | `begin_checkout` | 127 |
| 4 | `add_payment_info` | 73 |
| 5 | `purchase` | 14 |

**Atenção:** a ordem acima é uma organização analítica dos tipos de evento, não uma prova de passagem sequencial dos mesmos usuários. A contagem de `begin_checkout` ser maior que a de `add_to_cart` reforça a necessidade de interpretar os eventos separadamente.

Consulte [Definições das métricas Gold](docs/metricas_gold.md) para detalhes das regras de cálculo.

## 7. Estrutura do repositório

```text
mediainsight/
├── .dockerignore
├── .gitignore
├── Dockerfile
├── compose.yaml
├── README.md
├── pyproject.toml
├── uv.lock
├── data/                         # Dados locais, não distribuídos
├── docs/
│   ├── docker.md
│   ├── etapa_03_silver.md
│   └── metricas_gold.md
├── scripts/
│   ├── audit_gold.py
│   └── export_powerbi.py
├── sql/
│   ├── silver/
│   └── gold/
│       ├── 001_marketing_daily.sql
│       ├── 002_acquisition_performance.sql
│       ├── 003_device_performance.sql
│       └── 004_conversion_funnel.sql
├── src/
│   └── mediainsight/            # Código da aplicação e pipelines
└── tests/                       # Testes automatizados
```

A árvore destaca os principais componentes, não todos os arquivos. **Bancos DuckDB, CSVs de entrada, exportações locais e backups não são distribuídos pelo repositório.**

## 8. Como executar

### Opção A — Docker (recomendada para validar o ambiente)

**Pré-requisitos:** Git e Docker Desktop com Docker Compose funcionando.

```powershell
git clone https://github.com/rafaelporfiriobarros/mediainsight.git
cd mediainsight

docker compose build
docker compose run --rm mediainsight
```

Na execução validada, a suíte retornou **35 testes aprovados**.

Para verificar o código dentro do container:

```powershell
docker compose run --rm mediainsight ruff check .
docker compose run --rm mediainsight ruff format --check .
```

**Importante:** construir a imagem e executar os testes **não cria automaticamente a base GA4**. A execução das transformações exige que os dados de entrada e as camadas anteriores estejam preparados.

Para executar Silver, Gold e exportação em uma **cópia isolada** do banco, consulte a [documentação Docker](docs/docker.md). Não execute comandos de transformação sobre o banco original sem antes conferir o caminho e fazer backup.

### Opção B — Ambiente local com UV

**Pré-requisitos:** Python 3.12, UV, Git e arquivo de entrada GA4 preparado.

```powershell
git clone https://github.com/rafaelporfiriobarros/mediainsight.git
cd mediainsight
uv sync
```

Diagnóstico da aplicação:

```powershell
uv run mediainsight
```

**Ordem de processamento:** preparar o CSV de origem → executar a ingestão Bronze → transformar Silver → construir Gold → auditar → exportar.

Os comandos abaixo pressupõem que **a ingestão Bronze já foi realizada** e que o banco DuckDB contém os dados esperados:

```powershell
uv run mediainsight-transform
uv run mediainsight-gold
uv run python scripts/audit_gold.py
uv run python scripts/export_powerbi.py
```

Os quatro arquivos exportados são gravados em `data/exports/powerbi/` na execução local padrão:

```text
marketing_daily.csv
acquisition_performance.csv
device_performance.csv
conversion_funnel.csv
```

**Reprodutibilidade dos dados:** como o arquivo de entrada não está no Git, um clone novo não reproduz automaticamente os resultados numéricos apresentados neste README. É necessário obter e preparar a extração GA4 compatível e executar a ingestão antes das demais camadas. A documentação da obtenção/preparação da fonte deve ser consultada ou complementada antes de tratar o pipeline como reproduzível de ponta a ponta por terceiros.

## 9. Testes, auditoria e qualidade

O projeto utiliza:

- Testes automatizados com `pytest`.
- Análise estática e formatação com Ruff.
- Transformações SQL versionadas.
- Validação de entradas e reconciliação de agregados entre Silver e Gold.
- Transações com rollback nas transformações validadas.
- Processamento reaplicável nas etapas implementadas, com cuidados específicos para substituição de tabelas.
- Auditoria dos indicadores e conferência dos CSVs exportados.

Para validar localmente:

```powershell
uv run pytest -v
uv run ruff check .
uv run ruff format --check .
```

**Nota sobre idempotência:** a ingestão Bronze utiliza substituição de tabela (`CREATE OR REPLACE TABLE`) na implementação analisada. Isso não deve ser confundido com uma estratégia completa de ingestão incremental, histórico de alterações ou deduplicação entre múltiplas cargas.

**Cobertura:** os 35 testes cobrem diferentes partes da aplicação e do pipeline; a exportação para Power BI foi validada por execução e conferência dos arquivos, mas ainda não conta com testes automatizados específicos documentados.

## 10. Power BI — Próxima entrega

O exportador Python já prepara quatro arquivos CSV para consumo no Power BI Desktop. O dashboard **ainda não está concluído**.

O planejamento inclui:

1. Importar os CSVs e validar tipos no Power Query.
2. Revisar a modelagem e as relações necessárias, evitando associações artificiais entre tabelas agregadas.
3. Criar medidas DAX para os indicadores executivos.
4. Construir visuais de tráfego, primeira aquisição, dispositivos e eventos de conversão.
5. Conferir os resultados com as consultas SQL/DuckDB.
6. Documentar e publicar evidências do dashboard.

Como existe apenas um dia de dados, não serão apresentadas tendências temporais como se houvesse uma série histórica.

## 11. Etapas do projeto

| Etapa | Entrega | Situação |
|---|---|---|
| 1 | Fundação técnica e arquitetura | Concluída |
| 2 | Ingestão Bronze | Concluída |
| 3 | Transformação e qualidade Silver | Concluída |
| 4 | Modelagem Gold e Marketing Analytics | Concluída |
| 5A | Containerização, documentação e publicação | **Concluída** |
| 5B | Dashboard executivo Power BI | Em desenvolvimento |

**Evidência de publicação da etapa Docker:** commit [`5f55742`](https://github.com/rafaelporfiriobarros/mediainsight/commit/5f55742) na branch `main`.

## 12. Documentação complementar

- [Docker — arquitetura, testes e execução isolada](docs/docker.md)
- [Transformação e qualidade da camada Silver](docs/etapa_03_silver.md)
- [Definições e regras das métricas Gold](docs/metricas_gold.md)
- [`scripts/audit_gold.py`](scripts/audit_gold.py) — auditoria e reconciliação.
- [`scripts/export_powerbi.py`](scripts/export_powerbi.py) — exportação dos dados analíticos.

## 13. Escopo e finalidade

Este é um projeto **educacional e de portfólio**, voltado à demonstração prática de Engenharia de Dados, Engenharia de Software, SQL, qualidade de dados e Marketing Analytics. Não representa uma solução implantada em produção nem uma análise operacional da Google Merchandise Store.

**Projeto independente, sem vínculo com a Agência Africa.**
