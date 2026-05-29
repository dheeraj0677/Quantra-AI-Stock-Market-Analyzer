"""
Quantra — ML feature extraction from technical indicators.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from app.analysis.technical_analyzer import (
    compute_atr,
    compute_bollinger_bands,
    compute_macd,
    compute_obv,
    compute_rsi,
)

logger = logging.getLogger(__name__)


def extract_features(df: pd.DataFrame) -> dict[str, float]:
    """
    Extract ML-ready features from OHLCV data.

    Returns a flat dict of feature_name → float value.
    """
    features: dict[str, float] = {}

    if df.empty or len(df) < 50:
        return features

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # ── RSI Features ──
    rsi = compute_rsi(close)
    features["rsi_14"] = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
    features["rsi_14_lag5"] = float(rsi.iloc[-5]) if len(rsi) >= 5 and not pd.isna(rsi.iloc[-5]) else 50.0
    features["rsi_delta_5d"] = features["rsi_14"] - features["rsi_14_lag5"]

    # ── MACD Features ──
    macd_line, signal_line, histogram = compute_macd(close)
    features["macd_histogram"] = float(histogram.iloc[-1]) if not pd.isna(histogram.iloc[-1]) else 0.0
    features["macd_histogram_lag5"] = float(histogram.iloc[-5]) if len(histogram) >= 5 else 0.0
    features["macd_hist_delta"] = features["macd_histogram"] - features["macd_histogram_lag5"]
    features["macd_crossover"] = 1.0 if (
        len(histogram) >= 2 and histogram.iloc[-1] > 0 and histogram.iloc[-2] <= 0
    ) else (-1.0 if len(histogram) >= 2 and histogram.iloc[-1] < 0 and histogram.iloc[-2] >= 0 else 0.0)

    # ── Bollinger Band Features ──
    bb_upper, bb_middle, bb_lower = compute_bollinger_bands(close)
    bb_range = bb_upper.iloc[-1] - bb_lower.iloc[-1]
    features["bb_position"] = float((close.iloc[-1] - bb_lower.iloc[-1]) / bb_range) if bb_range > 0 else 0.5
    features["bb_width"] = float(bb_range / bb_middle.iloc[-1]) if bb_middle.iloc[-1] > 0 else 0.0

    # ── ATR Features ──
    atr = compute_atr(high, low, close)
    features["atr_ratio"] = float(atr.iloc[-1] / close.iloc[-1]) if close.iloc[-1] > 0 and not pd.isna(atr.iloc[-1]) else 0.0

    # ── Volume Features ──
    vol_sma_20 = volume.rolling(20).mean()
    features["volume_ratio"] = float(volume.iloc[-1] / vol_sma_20.iloc[-1]) if vol_sma_20.iloc[-1] > 0 else 1.0
    features["volume_zscore"] = float((volume.iloc[-1] - vol_sma_20.iloc[-1]) / volume.rolling(20).std().iloc[-1]) if volume.rolling(20).std().iloc[-1] > 0 else 0.0

    # ── EMA Ratios ──
    for span in [9, 21, 50, 200]:
        if len(close) >= span:
            ema = close.ewm(span=span, adjust=False).mean()
            features[f"ema_{span}_ratio"] = float(close.iloc[-1] / ema.iloc[-1]) if ema.iloc[-1] > 0 else 1.0

    # ── Momentum Features ──
    for period in [5, 10, 20]:
        if len(close) > period:
            features[f"return_{period}d"] = float((close.iloc[-1] / close.iloc[-period - 1]) - 1)
        else:
            features[f"return_{period}d"] = 0.0

    # ── Volatility ──
    returns = close.pct_change()
    features["volatility_20d"] = float(returns.tail(20).std() * np.sqrt(252)) if len(returns) >= 20 else 0.0

    # ── OBV Trend ──
    obv = compute_obv(close, volume)
    obv_sma = obv.rolling(20).mean()
    features["obv_ratio"] = float(obv.iloc[-1] / obv_sma.iloc[-1]) if obv_sma.iloc[-1] != 0 else 1.0

    # ── Price relative to 52-week range ──
    high_52w = high.tail(252).max()
    low_52w = low.tail(252).min()
    range_52w = high_52w - low_52w
    features["price_52w_position"] = float((close.iloc[-1] - low_52w) / range_52w) if range_52w > 0 else 0.5

    return features
