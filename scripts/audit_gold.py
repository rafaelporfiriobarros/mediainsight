from pathlib import Path

import duckdb

DATABASE_PATH = Path("data/mediainsight.duckdb")

GOLD_TABLES = (
    "marketing_daily",
    "acquisition_performance",
    "device_performance",
)


def main() -> None:
    if not DATABASE_PATH.is_file():
        raise FileNotFoundError(f"Banco nao encontrado: {DATABASE_PATH}")

    with duckdb.connect(
        str(DATABASE_PATH),
        read_only=True,
    ) as con:
        print("=" * 60)
        print("MEDIAINSIGHT 360 - AUDITORIA GOLD")
        print("=" * 60)

        silver_totals = con.execute("""
            SELECT
                COUNT(*) AS total_events,
                COUNT(*) FILTER (
                    WHERE event_name = 'page_view'
                ) AS page_views,
                COUNT(*) FILTER (
                    WHERE event_name = 'purchase'
                ) AS purchases,
                COALESCE(SUM(purchase_revenue), 0)
                    AS total_revenue
            FROM silver.ga4_events
        """).fetchone()

        print("\n1. TOTAIS SILVER")
        print(f"Eventos: {silver_totals[0]:,}")
        print(f"Page views: {silver_totals[1]:,}")
        print(f"Compras: {silver_totals[2]:,}")
        print(f"Receita: {silver_totals[3]:,.2f}")

        print("\n2. RECONCILIACAO GOLD")

        for table in GOLD_TABLES:
            totals = con.execute(f"""
                SELECT
                    COALESCE(SUM(total_events), 0),
                    COALESCE(SUM(page_views), 0),
                    COALESCE(SUM(purchases), 0),
                    COALESCE(SUM(total_revenue), 0)
                FROM gold.{table}
            """).fetchone()

            status = "OK" if totals == silver_totals else "DIVERGENCIA"

            print(f"gold.{table}: {status}")

            if status != "OK":
                raise ValueError(f"Falha de reconciliacao: {table}")

        print("\n3. INDICADORES DE MARKETING")

        metrics = con.execute("""
            SELECT
                SUM(unique_users),
                SUM(total_sessions),
                SUM(purchases),
                SUM(purchasing_sessions),
                SUM(total_revenue)
            FROM gold.marketing_daily
        """).fetchone()

        print(f"Usuarios (soma diaria): {metrics[0]:,}")
        print(f"Sessoes (soma diaria): {metrics[1]:,}")
        print(f"Eventos de compra: {metrics[2]:,}")
        print(f"Sessoes com compra: {metrics[3]:,}")
        print(f"Receita: {metrics[4]:,.2f}")

        print("\n4. FUNIL DE CONVERSAO")

        funnel = con.execute("""
            SELECT
                step_order,
                event_name,
                SUM(total_events)
            FROM gold.conversion_funnel
            GROUP BY step_order, event_name
            ORDER BY step_order
        """).fetchall()

        for _, event_name, total in funnel:
            print(f"{event_name}: {total:,}")

        funnel_gold_total = sum(row[2] for row in funnel)

        funnel_silver_total = con.execute("""
            SELECT COUNT(*)
            FROM silver.ga4_events
            WHERE event_name IN (
                'view_item',
                'add_to_cart',
                'begin_checkout',
                'add_payment_info',
                'purchase'
            )
        """).fetchone()[0]

        if funnel_gold_total != funnel_silver_total:
            raise ValueError("Divergencia entre funil Gold e Silver")

        print("\n5. RESULTADO FINAL")
        print("AUDITORIA GOLD: APROVADA")


if __name__ == "__main__":
    main()
