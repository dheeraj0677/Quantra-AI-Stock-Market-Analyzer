"""
Quantra — ML Pipeline orchestrator.

Master pipeline: features → score → prediction
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from app.ml.features import fundamental as fund_features
from app.ml.features import sentiment as sent_features
from app.ml.features import technical as tech_features
from app.ml.models import direction_classifier, stock_scorer

logger = logging.getLogger(__name__)


def build_feature_vector(
    ohlcv_df: pd.DataFrame | None = None,
    articles: list[dict] | None = None,
    stock_meta: dict | None = None,
) -> dict[str, float]:
    """
    Build a complete feature vector from all data sources.

    Returns:
        Merged dict of all features (technical + sentiment + fundamental)
    """
    features: dict[str, float] = {}

    if ohlcv_df is not None and not ohlcv_df.empty:
        features.update(tech_features.extract_features(ohlcv_df))

    if articles:
        features.update(sent_features.extract_features(articles))

    if stock_meta:
        features.update(fund_features.extract_features(stock_meta))

    return features


def run_pipeline(
    ohlcv_df: pd.DataFrame | None = None,
    articles: list[dict] | None = None,
    stock_meta: dict | None = None,
) -> dict[str, Any]:
    """
    Run the full ML pipeline.

    Returns:
        {
            "ml_score": float (0–100),
            "direction": str (UP/DOWN/SIDEWAYS),
            "direction_confidence": float (0–1),
            "features": dict
        }
    """
    features = build_feature_vector(ohlcv_df, articles, stock_meta)

    if not features:
        return {
            "ml_score": 50.0,
            "direction": "SIDEWAYS",
            "direction_confidence": 0.4,
            "features": {},
        }

    # Score
    ml_score = stock_scorer.score(features)

    # Direction
    direction, direction_conf = direction_classifier.predict(features)

    return {
        "ml_score": ml_score,
        "direction": direction,
        "direction_confidence": direction_conf,
        "features": features,
    }
