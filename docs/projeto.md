
# MediaInsight - Documento do Projeto

## 1. Contexto

Projeto de Engenharia de Dados e Analytics
inspirado nas atividades de BI de uma agência de publicidade.

## 2. Problema de negócio

Transformar dados de aquisição e comportamento digital
em indicadores confiáveis para apoiar decisões de mídia.

## 3. Fonte de dados

Google Analytics 4 — Google Merchandise Store.

Dataset:
bigquery-public-data.ga4_obfuscated_sample_ecommerce

Período:
2020-11-01 a 2021-01-31.

Origem:
BigQuery Public Datasets.

Observação:
Os dados são históricos e ofuscados. Algumas informações
podem apresentar valores ausentes ou inconsistências.

## 4. Objetivos analíticos

- Analisar aquisição por canais.
- Acompanhar eventos e sessões.
- Estudar comportamento e conversões.
- Identificar oportunidades de otimização.
- Avaliar a qualidade dos dados.

## 5. Indicadores candidatos

- Usuários.
- Sessões.
- Sessões engajadas.
- Eventos de compra.
- Receita de compras, se utilizável.
- Taxa de conversão definida pelo projeto.

As métricas serão confirmadas após a inspeção do dataset.

## 6. Limitações

O dataset não garante disponibilidade de investimento,
impressões ou cliques publicitários.

Portanto, CPC, CPM, CPA e ROAS não serão calculados
sem dados adequados de custos e resultados.

## 7. Arquitetura

Fonte GA4 / BigQuery
    -> Extração limitada
    -> Bronze
    -> Silver
    -> Gold
    -> Power BI

## 8. Escopo da Etapa 1

- Configuração do ambiente.
- Estrutura inicial.
- Conexão DuckDB.
- Testes automatizados.
- Qualidade de código.
- Documentação.

## 9. Critérios de sucesso

- Aplicação executa sem erros.
- DuckDB responde às consultas.
- Seis testes passam.
- Ruff não apresenta erros.
- Repositório está versionado.
