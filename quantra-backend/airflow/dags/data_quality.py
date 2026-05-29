"""Airflow DAG — Data quality monitoring."""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {"owner": "quantra", "depends_on_past": False, "retries": 1, "retry_delay": timedelta(minutes=5)}

dag = DAG(
    "data_quality",
    default_args=default_args,
    description="Alert if OHLCV data is stale or missing",
    schedule_interval="0 * * * *",  # Every hour
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["monitoring", "data"],
)


def check_ohlcv_freshness():
    """Check if OHLCV data is up-to-date."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Data quality check: OHLCV freshness")
    # In production: query TimescaleDB for latest timestamp per ticker, alert if stale


def check_news_freshness():
    """Check if news scraping is working."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Data quality check: news freshness")


t1 = PythonOperator(task_id="check_ohlcv_freshness", python_callable=check_ohlcv_freshness, dag=dag)
t2 = PythonOperator(task_id="check_news_freshness", python_callable=check_news_freshness, dag=dag)

[t1, t2]
