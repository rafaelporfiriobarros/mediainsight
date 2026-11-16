
# MediaInsight — Dicionário de Métricas Gold

## 1. Objetivo

Disponibilizar indicadores de marketing digital a partir
dos eventos GA4 processados nas camadas Bronze e Silver.

## 2. Tabelas Gold

### gold.marketing_daily

Granularidade: uma linha por data de evento.

Indicadores:
- total_events: quantidade de eventos.
- unique_users: usuários distintos no dia.
- total_sessions: sessões distintas no dia.
- page_views: eventos page_view.
- engagement_events: eventos user_engagement.
- purchases: eventos purchase.
- purchasing_sessions: sessões com evento purchase.
- total_revenue: soma de purchase_revenue.
- session_conversion_rate: purchasing_sessions / total_sessions.
- revenue_per_session: total_revenue / total_sessions.

### gold.acquisition_performance

Granularidade:
- event_date
- first_user_source
- first_user_medium

Atenção: first_user_source e first_user_medium
representam a primeira aquisição do usuário,
não a atribuição da sessão.

### gold.device_performance

Granularidade:
- event_date
- device_category

Permite comparar indicadores por categoria de dispositivo.

### gold.conversion_funnel

Granularidade:
- event_date
- step_order

Etapas:
1. view_item
2. add_to_cart
3. begin_checkout
4. add_payment_info
5. purchase

Este funil é descritivo e baseado em eventos.

As contagens não demonstram progressão sequencial
dos mesmos usuários entre as etapas.

## 3. Regras de qualidade

- Reconciliação dos eventos entre Silver e Gold.
- Reconciliação de page views e compras.
- Reconciliação da receita.
- Validação das contagens do funil.
- Execução idempotente das transformações.
- Rollback em caso de falha no pipeline.

## 4. Limitações

- Amostra inicial restrita a 2020-11-01.
- A moeda da receita precisa ser confirmada.
- Eventos de compra não equivalem necessariamente
  a transações únicas.
- Usuários e sessões distintos não são necessariamente
  aditivos entre diferentes segmentos.
- O funil não é uma análise de abandono sequencial.
- A contagem diária de sessões é baseada nos eventos
  observados em cada data.
```

## 4. Validação final

Execute:

```powershell
uv run python scripts/audit_gold.py

uv run ruff check .

uv run ruff format --check .

uv run pytest -v

git status --short
```

O resultado esperado é uma auditoria aprovada, os **35 testes anteriores passando** e o Ruff sem erros. O `git status` mostrará os arquivos que precisam ser incluídos no próximo commit.

Após receber os resultados, vamos preparar o README, registrar as evidências e publicar a Etapa 4 no GitHub.

**Não avançaremos para a Etapa 5 (Power BI) antes de concluir essa validação e receber sua confirmação.**