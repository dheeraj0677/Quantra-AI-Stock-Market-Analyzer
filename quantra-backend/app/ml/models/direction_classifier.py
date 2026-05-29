"""
Quantra — Direction classifier (UP/DOWN/SIDEWAYS).
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)

_model = None
_feature_names: list[str] | None = None
CLASSES = ["DOWN", "SIDEWAYS", "UP"]


def load_model(model_path: str | None = None):
    """Load the XGBoost direction classifier."""
    global _model, _feature_names

    if _model is not None:
        return _model

    try:
        import xgboost as xgb

        if model_path:
            _model = xgb.XGBClassifier()
            _model.load_model(model_path)
            _feature_names = _model.get_booster().feature_names
            logger.info("✅ Direction classifier loaded from %s", model_path)
        else:
            logger.info("No direction model path — using rule-based fallback")
            _model = None

    except Exception as e:
        logger.warning("Failed to load direction model: %s", e)
        _model = None

    return _model


def predict(features: dict[str, float]) -> tuple[str, float]:
    """
    Predict direction (UP/DOWN/SIDEWAYS) and confidence.

    Returns:
        (direction, probability) tuple
    """
    if _model is not None:
        try:
            if _feature_names:
                X = np.array([[features.get(f, 0.0) for f in _feature_names]])
            else:
                X = np.array([list(features.values())])

            probs = _model.predict_proba(X)[0]
            pred_idx = np.argmax(probs)
            direction = CLASSES[pred_idx] if pred_idx < len(CLASSES) else "SIDEWAYS"
            confidence = float(probs[pred_idx])

            return direction, round(confidence, 4)

        except Exception as e:
            logger.error("Direction prediction error: %s", e)

    # Rule-based fallback
    return _rule_based_predict(features)


def _rule_based_predict(features: dict[str, float]) -> tuple[str, float]:
    """Rule-based direction prediction when ML model is unavailable."""
    score = 0.0

    # Momentum
    ret_5d = features.get("return_5d", 0)
    ret_10d = features.get("return_10d", 0)
    score += ret_5d * 50
    score += ret_10d * 30

    # RSI
    rsi = features.get("rsi_14", 50)
    if rsi < 30:
        score += 15
    elif rsi > 70:
        score -= 15

    # MACD
    score += features.get("macd_crossover", 0) * 10

    # Sentiment
    score += features.get("sentiment_mean", 0) * 20

    if score > 10:
        return "UP", min(0.85, 0.5 + score / 100)
    elif score < -10:
        return "DOWN", min(0.85, 0.5 + abs(score) / 100)
    else:
        return "SIDEWAYS", 0.45
