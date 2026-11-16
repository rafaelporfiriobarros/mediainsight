# MediaInsight 360 — Etapa 3: Transformação e Qualidade de Dados

## 1. Objetivo

Implementar a camada Silver do projeto MediaInsight 360, transformando os eventos brutos do Google Analytics 4 (GA4) em dados estruturados, padronizados e preparados para análises de marketing digital.

## 2. Tecnologias utilizadas

- Python 3.12
- DuckDB
- SQL
- UV
- pytest
- Ruff
- Git e GitHub

## 3. Arquitetura

**BigQuery (GA4) → CSV → Bronze (DuckDB) → Silver (DuckDB)**

A camada Bronze preserva os eventos importados. A camada Silver aplica transformações, padronização de tipos e regras de qualidade.

## 4. Transformações implementadas

| Campo | Transformação |
|---|---|
| event_date | Conversão para DATE |
| event_timestamp | Conversão de microssegundos Unix para TIMESTAMP |
| event_name | Remoção de espaços e normalização de valores vazios |
| user_pseudo_id | Normalização de valores vazios |
| ga_session_id | Conversão para BIGINT |
| first_user_source | Normalização de valores vazios |
| first_user_medium | Normalização de valores vazios |
| first_user_campaign | Normalização de valores vazios |
| device_category | Normalização de valores vazios |
| country | Normalização de valores vazios |
| purchase_revenue | Conversão para DOUBLE |

## 5. Regras de qualidade

São excluídos da Silver os registros com:

- Data inválida ou ausente.
- Timestamp inválido ou ausente.
- Nome de evento ausente.
- Receita negativa.

Os valores nulos de receita são preservados, pois podem representar eventos sem transação financeira.

## 6. Resultados da execução

| Indicador | Resultado |
|---|---:|
| Eventos na Bronze | 31.272 |
| Eventos na Silver | 31.272 |
| Registros rejeitados | 0 |
| Taxa de aproveitamento | 100% |
| Data inicial | 01/11/2020 |
| Data final | 01/11/2020 |
| Eventos com receita preenchida | 14 |
| Soma dos valores de receita | 773,00 |
| Receitas negativas | 0 |

A unidade monetária ainda não foi validada.

## 7. Qualidade dos dados

A auditoria identificou:

- Nenhum identificador de usuário nulo.
- Nenhum identificador de sessão nulo.
- Nenhuma origem de primeira aquisição nula.
- 31.258 registros sem valor de receita.
- Nenhuma divergência entre a data do evento e a data derivada diretamente do timestamp.

A ausência de receita na maioria dos eventos é esperada em dados de navegação e interação.

## 8. Testes automatizados

A implementação possui 17 testes automatizados aprovados, distribuídos entre configuração, banco de dados, ingestão e transformação.

Os testes da Silver verificam:

1. Criação da tabela Silver.
2. Conversão dos tipos de dados.
3. Preservação da Bronze.
4. Idempotência da transformação.
5. Rejeição de datas inválidas.

## 9. Idempotência e integridade

A transformação pode ser executada novamente sem acumular registros duplicados.

A tabela Silver é recriada a partir da Bronze, utilizando uma transação para proteger a operação contra falhas.

A reconciliação confirmou que os 31.272 eventos da Bronze foram preservados na Silver.

## 10. Limitações conhecidas

- A amostra atual contém somente um dia de eventos.
- Os campos de aquisição representam a primeira origem do usuário, não necessariamente a origem da sessão.
- O fuso horário da propriedade GA4 ainda não foi validado.
- A unidade monetária de `purchase_revenue` ainda precisa ser confirmada.
- Os registros rejeitados são contabilizados, mas não armazenados em uma tabela de quarentena.
- A ausência de rejeições não garante ausência de todos os possíveis problemas de qualidade.

## 11. Conclusão

A Etapa 3 implementou uma camada Silver reproduzível, com transformações SQL, execução em Python, validações automatizadas e auditoria dos dados.

A solução mantém os eventos originais preservados na Bronze e disponibiliza dados tipados para a futura modelagem analítica.

A próxima etapa prevista é a construção da camada Gold, com indicadores de comportamento, aquisição e conversão.