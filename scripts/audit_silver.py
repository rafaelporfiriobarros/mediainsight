from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "mediainsight.duckdb"


def main() -> None:
    connection = duckdb.connect(
        str(DATABASE_PATH),
        read_only=True,
    )

    try:
        print("=" * 55)
        print("MEDIAINSIGHT 360 - AUDITORIA SILVER")
        print("=" * 55)

        print("\n[1] RECONCILIACAO")

        bronze, silver = connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM bronze.ga4_events),
                (SELECT COUNT(*) FROM silver.ga4_events)
            """
        ).fetchone()

        print(f"Bronze: {bronze:,}")
        print(f"Silver: {silver:,}")
        print(f"Diferenca: {bronze - silver:,}")

        print("\n[2] VALORES NULOS")

        nulls = connection.execute(
            """
            SELECT
                COUNT(*) FILTER (
                    WHERE user_pseudo_id IS NULL
                ) AS null_users,

                COUNT(*) FILTER (
                    WHERE ga_session_id IS NULL
                ) AS null_sessions,

                COUNT(*) FILTER (
                    WHERE first_user_source IS NULL
                ) AS null_sources,

                COUNT(*) FILTER (
                    WHERE purchase_revenue IS NULL
                ) AS null_revenue
            FROM silver.ga4_events
            """
        ).fetchone()

        labels = [
            "user_pseudo_id",
            "ga_session_id",
            "first_user_source",
            "purchase_revenue",
        ]

        for label, value in zip(labels, nulls, strict=True):
            percentage = value / silver * 100
            print(f"{label}: {value:,} ({percentage:.2f}%)")

        print("\n[3] DISTRIBUICAO DE EVENTOS")

        events = connection.execute(
            """
            SELECT event_name, COUNT(*) AS total
            FROM silver.ga4_events
            GROUP BY event_name
            ORDER BY total DESC, event_name
            """
        ).fetchall()

        for event_name, total in events:
            print(f"{event_name}: {total:,}")

        print("\n[4] TIMESTAMPS")

        timestamps = connection.execute(
            """
            SELECT
                CAST(MIN(event_timestamp) AS VARCHAR),
                CAST(MAX(event_timestamp) AS VARCHAR),
                COUNT(*) FILTER (
                    WHERE CAST(event_timestamp AS DATE)
                          <> event_date
                )
            FROM silver.ga4_events
            """
        ).fetchone()

        print(f"Primeiro evento (UTC): {timestamps[0]}")
        print(f"Ultimo evento (UTC): {timestamps[1]}")
        print(f"Datas divergentes (comparacao direta): {timestamps[2]:,}")

        print("\n[5] RECEITA")

        revenue = connection.execute(
            """
            SELECT
                COUNT(*) FILTER (
                    WHERE purchase_revenue IS NOT NULL
                ),
                COALESCE(SUM(purchase_revenue), 0),
                COUNT(*) FILTER (
                    WHERE purchase_revenue < 0
                )
            FROM silver.ga4_events
            """
        ).fetchone()

        print(f"Eventos com receita: {revenue[0]:,}")
        print(f"Receita total registrada: {revenue[1]:,.2f}")
        print(f"Receitas negativas: {revenue[2]:,}")

        print("\nAuditoria concluida.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
