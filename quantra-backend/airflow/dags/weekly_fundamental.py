"""Airflow DAG — Weekly fundamental data refresh."""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {"owner": "quantra", "depends_on_past": False, "retries": 2, "retry_delay": timedelta(minutes=15)}

dag = DAG(
    "weekly_fundamental",
    default_args=default_args,
    description="Refresh stock fundamentals from yfinance / Alpha Vantage weekly",
    schedule_interval="0 6 * * 0",  # Sunday 6 AM IST
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["data", "fundamentals"],
)


def refresh_fundamentals():
    """Refresh stock_meta table from external APIs."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Weekly fundamental refresh started")
    # In production: iterate stock_meta tickers, fetch fresh data from yfinance


t1 = PythonOperator(task_id="refresh_fundamentals", python_callable=refresh_fundamentals, dag=dag)
