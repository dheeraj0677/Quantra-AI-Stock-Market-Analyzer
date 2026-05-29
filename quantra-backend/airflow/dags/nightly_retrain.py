"""Airflow DAG — Nightly model retraining."""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "quantra",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=10),
}

dag = DAG(
    "nightly_retrain",
    default_args=default_args,
    description="Retrain XGBoost scorer and direction classifier daily",
    schedule_interval="30 0 * * *",  # 12:30 AM IST
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["ml", "retrain"],
)


def retrain_scorer():
    """Retrain the stock scorer model."""
    from app.ml.retrain.train_scorer import train_scorer
    from app.ml.model_loader import upload_to_minio
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Nightly scorer retraining started")
    # In production: load features from DB, train, upload to MinIO


def retrain_direction():
    """Retrain the direction classifier."""
    from app.ml.retrain.train_direction import train_direction_classifier
    from app.ml.model_loader import upload_to_minio
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Nightly direction classifier retraining started")


def evaluate_models():
    """Evaluate retrained models against recent predictions."""
    from app.ml.retrain.evaluate import evaluate_predictions
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Model evaluation started")


t1 = PythonOperator(task_id="retrain_scorer", python_callable=retrain_scorer, dag=dag)
t2 = PythonOperator(task_id="retrain_direction", python_callable=retrain_direction, dag=dag)
t3 = PythonOperator(task_id="evaluate_models", python_callable=evaluate_models, dag=dag)

[t1, t2] >> t3
