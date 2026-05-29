"""
Quantra — Fundamental-based ML features.
"""

from __future__ import annotations


def extract_features(stock_meta: dict) -> dict[str, float]:
    """
    Extract ML-ready features from fundamental data.

    Args:
        stock_meta: Dict with pe_ratio, pb_ratio, roe, eps, etc.

    Returns:
        Flat dict of feature_name → float value
    """
    features: dict[str, float] = {}

    def _safe(key: str, default: float = 0.0) -> float:
        val = stock_meta.get(key)
        return float(val) if val is not None else default

    features["pe_ratio"] = _safe("pe_ratio", 20.0)
    features["pb_ratio"] = _safe("pb_ratio", 2.0)
    features["roe"] = _safe("roe", 0.1)
    features["eps"] = _safe("eps", 0.0)
    features["dividend_yield"] = _safe("dividend_yield", 0.0)
    features["market_cap_log"] = 0.0

    mc = stock_meta.get("market_cap")
    if mc and mc > 0:
        import math
        features["market_cap_log"] = math.log10(mc)

    # Derived features
    features["pe_inverse"] = 1.0 / features["pe_ratio"] if features["pe_ratio"] > 0 else 0.0
    features["earnings_yield"] = features["pe_inverse"] * 100  # earnings yield %

    # Valuation flag
    features["is_undervalued"] = 1.0 if features["pe_ratio"] < 15 and features["roe"] > 0.15 else 0.0
    features["is_overvalued"] = 1.0 if features["pe_ratio"] > 40 else 0.0

    # Quality score
    quality = 0.0
    if features["roe"] > 0.20:
        quality += 0.3
    if features["pe_ratio"] < 25:
        quality += 0.2
    if features["dividend_yield"] > 0.02:
        quality += 0.1
    features["fundamental_quality"] = quality

    return features
