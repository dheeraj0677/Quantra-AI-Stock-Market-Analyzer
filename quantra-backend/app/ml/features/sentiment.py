"""
Quantra — Sentiment-based ML features.
"""

from __future__ import annotations


def extract_features(articles: list[dict]) -> dict[str, float]:
    """
    Extract ML-ready features from news articles with sentiment.

    Args:
        articles: List of article dicts with sentiment_score, impact_level, published_at

    Returns:
        Flat dict of feature_name → float value
    """
    features: dict[str, float] = {}

    if not articles:
        features["sentiment_mean"] = 0.0
        features["sentiment_std"] = 0.0
        features["sentiment_positive_ratio"] = 0.0
        features["sentiment_negative_ratio"] = 0.0
        features["article_count"] = 0.0
        features["high_impact_count"] = 0.0
        features["sentiment_momentum"] = 0.0
        return features

    scores = [a.get("sentiment_score", 0.0) for a in articles if a.get("sentiment_score") is not None]
    impact_levels = [a.get("impact_level", "LOW") for a in articles]

    # Basic stats
    import numpy as np
    scores_arr = np.array(scores) if scores else np.array([0.0])
    features["sentiment_mean"] = float(np.mean(scores_arr))
    features["sentiment_std"] = float(np.std(scores_arr)) if len(scores_arr) > 1 else 0.0
    features["sentiment_median"] = float(np.median(scores_arr))
    features["sentiment_min"] = float(np.min(scores_arr))
    features["sentiment_max"] = float(np.max(scores_arr))

    # Ratios
    total = len(scores)
    features["sentiment_positive_ratio"] = sum(1 for s in scores if s > 0.2) / max(total, 1)
    features["sentiment_negative_ratio"] = sum(1 for s in scores if s < -0.2) / max(total, 1)
    features["sentiment_neutral_ratio"] = 1.0 - features["sentiment_positive_ratio"] - features["sentiment_negative_ratio"]

    # Volume
    features["article_count"] = float(total)
    features["high_impact_count"] = float(sum(1 for il in impact_levels if il == "HIGH"))
    features["medium_impact_count"] = float(sum(1 for il in impact_levels if il == "MEDIUM"))

    # Momentum (first half vs second half)
    if len(scores) >= 4:
        mid = len(scores) // 2
        first_half = np.mean(scores[:mid])
        second_half = np.mean(scores[mid:])
        features["sentiment_momentum"] = float(second_half - first_half)
    else:
        features["sentiment_momentum"] = 0.0

    return features
