"""Quantra — Model evaluation metrics."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def evaluate_predictions(
    predictions: list[dict],
) -> dict[str, float]:
    """
    Evaluate prediction accuracy using walk-forward backtesting.

    Args:
        predictions: List of {predicted_direction, actual_direction, confidence}
    """
    if not predictions:
        return {"accuracy": 0.0, "precision_up": 0.0, "recall_up": 0.0}

    correct = sum(1 for p in predictions if p["predicted_direction"] == p["actual_direction"])
    total = len(predictions)
    accuracy = correct / total

    # Direction-specific metrics
    up_preds = [p for p in predictions if p["predicted_direction"] == "UP"]
    up_correct = sum(1 for p in up_preds if p["actual_direction"] == "UP")
    precision_up = up_correct / len(up_preds) if up_preds else 0.0

    actual_ups = [p for p in predictions if p["actual_direction"] == "UP"]
    recall_up = up_correct / len(actual_ups) if actual_ups else 0.0

    # Confidence-weighted accuracy
    weighted_correct = sum(
        p["confidence"] for p in predictions
        if p["predicted_direction"] == p["actual_direction"]
    )
    weighted_total = sum(p["confidence"] for p in predictions)
    conf_weighted_acc = weighted_correct / weighted_total if weighted_total > 0 else 0.0

    results = {
        "accuracy": round(accuracy, 4),
        "precision_up": round(precision_up, 4),
        "recall_up": round(recall_up, 4),
        "confidence_weighted_accuracy": round(conf_weighted_acc, 4),
        "total_predictions": total,
        "correct_predictions": correct,
    }

    logger.info("Evaluation: accuracy=%.2f%% (%d/%d)", accuracy * 100, correct, total)
    return results
