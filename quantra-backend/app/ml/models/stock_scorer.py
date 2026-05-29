"""
Quantra — XGBoost stock scorer (0–100).
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)

_model = None
_feature_names: list[str] | None = None


def load_model(model_path: str | None = None):
    """Load the XGBoost scorer model."""
    global _model, _feature_names

    if _model is not None:
        return _model

    try:
        import xgboost as xgb

        if model_path:
            _model = xgb.XGBRegressor()
            _model.load_model(model_path)
            _feature_names = _model.get_booster().feature_names
            logger.info("✅ Stock scorer model loaded from %s", model_path)
        else:
            logger.info("No scorer model path — using rule-based fallback")
            _model = None

    except Exception as e:
        logger.warning("Failed to load scorer model: %s", e)
        _model = None

    return _model


def score(features: dict[str, float]) -> float:
    """
    Score a stock 0–100 based on combined features.

    Falls back to rule-based scoring if model is not loaded.
    """
    if _model is not None:
        try:

            # Align features to expected order
            if _feature_names:
                X = np.array([[features.get(f, 0.0) for f in _feature_names]])
            else:
                X = np.array([list(features.values())])

            raw_score = float(_model.predict(X)[0])
            return max(0.0, min(100.0, raw_score))

        except Exception as e:
            logger.error("XGBoost scoring error: %s", e)

    # Rule-based fallback
    return _rule_based_score(features)


def _rule_based_score(features: dict[str, float]) -> float:
    """Simple rule-based scoring when ML model is unavailable."""
    score = 50.0

    # Technical signals
    rsi = features.get("rsi_14", 50)
    if rsi < 35:
        score += 10
    elif rsi > 65:
        score -= 8

    macd_cross = features.get("macd_crossover", 0)
    score += macd_cross * 8

    bb_pos = features.get("bb_position", 0.5)
    if bb_pos < 0.2:
        score += 8
    elif bb_pos > 0.8:
        score -= 8

    # Momentum
    ret_5d = features.get("return_5d", 0)
    score += ret_5d * 100  # scale returns

    # Sentiment
    sent_mean = features.get("sentiment_mean", 0)
    score += sent_mean * 15

    # Fundamentals
    quality = features.get("fundamental_quality", 0)
    score += quality * 20

    return max(0.0, min(100.0, round(score, 1)))
