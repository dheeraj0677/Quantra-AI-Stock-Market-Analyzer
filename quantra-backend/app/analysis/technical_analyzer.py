"""
Quantra — Technical Analysis Engine.

Computes all technical indicators from OHLCV data and produces
a composite technical score (0–100).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class TechnicalResult:
    """Full technical analysis output for a ticker."""

    ticker: str
    # Individual indicators
    rsi: float | None = None
    rsi_signal: str | None = None  # OVERSOLD | OVERBOUGHT | NEUTRAL
    macd: float | None = None
    macd_signal_line: float | None = None
    macd_histogram: float | None = None
    macd_crossover: str | None = None  # BULLISH | BEARISH | NONE
    bb_upper: float | None = None
    bb_middle: float | None = None
    bb_lower: float | None = None
    bb_position: float | None = None  # 0–1 position within bands
    atr: float | None = None
    obv: float | None = None
    obv_trend: str | None = None  # RISING | FALLING | FLAT
    ema_9: float | None = None
    ema_21: float | None = None
    ema_50: float | None = None
    ema_200: float | None = None
    volume_spike: bool | None = None
    patterns_detected: list[str] = field(default_factory=list)
    support_levels: list[float] = field(default_factory=list)
    resistance_levels: list[float] = field(default_factory=list)
    trend: str | None = None  # UPTREND | DOWNTREND | SIDEWAYS
    # Composite
    composite_score: float = 50.0  # 0–100
    signals: list[dict] = field(default_factory=list)


def compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Compute RSI (Relative Strength Index)."""
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    # Use Wilder's smoothing after initial SMA
    for i in range(period, len(close)):
        avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * (period - 1) + loss.iloc[i]) / period

    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def compute_macd(
    close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Compute MACD, signal line, and histogram."""
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def compute_bollinger_bands(
    close: pd.Series, period: int = 20, std_dev: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Compute Bollinger Bands (upper, middle, lower)."""
    middle = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()
    upper = middle + std_dev * std
    lower = middle - std_dev * std
    return upper, middle, lower


def compute_atr(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
) -> pd.Series:
    """Compute Average True Range."""
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.rolling(window=period).mean()


def compute_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """Compute On-Balance Volume."""
    direction = np.sign(close.diff())
    direction.iloc[0] = 0
    return (volume * direction).cumsum()


def detect_volume_spike(volume: pd.Series, period: int = 20, threshold: float = 2.0) -> bool:
    """Check if latest volume exceeds threshold × 20-day average."""
    if len(volume) < period + 1:
        return False
    avg_volume = volume.iloc[-(period + 1) : -1].mean()
    return bool(volume.iloc[-1] > threshold * avg_volume)


def detect_patterns(df: pd.DataFrame) -> list[str]:
    """
    Detect candlestick patterns.

    Uses simple heuristics for common patterns.
    """
    patterns = []
    if len(df) < 3:
        return patterns

    o, h, l, c = df["Open"].iloc[-1], df["High"].iloc[-1], df["Low"].iloc[-1], df["Close"].iloc[-1]
    o1, h1, l1, c1 = df["Open"].iloc[-2], df["High"].iloc[-2], df["Low"].iloc[-2], df["Close"].iloc[-2]
    body = abs(c - o)
    body1 = abs(c1 - o1)
    range_ = h - l if h != l else 0.01

    # Doji — body is very small relative to range
    if body < range_ * 0.1:
        patterns.append("Doji")

    # Hammer — small body at top, long lower shadow
    lower_shadow = min(o, c) - l
    upper_shadow = h - max(o, c)
    if lower_shadow > 2 * body and upper_shadow < body * 0.5 and body > 0:
        patterns.append("Hammer")

    # Bullish Engulfing — bearish candle followed by larger bullish candle
    if c1 < o1 and c > o and o <= c1 and c >= o1 and body > body1:
        patterns.append("Bullish Engulfing")

    # Bearish Engulfing
    if c1 > o1 and c < o and o >= c1 and c <= o1 and body > body1:
        patterns.append("Bearish Engulfing")

    # Morning Star (3-candle) — bearish, small body (gap down), bullish
    if len(df) >= 3:
        o2, c2 = df["Open"].iloc[-3], df["Close"].iloc[-3]
        body2 = abs(c2 - o2)
        if c2 < o2 and body1 < body2 * 0.3 and c > o and c > (o2 + c2) / 2:
            patterns.append("Morning Star")

    return patterns


def find_support_resistance(close: pd.Series, window: int = 20) -> tuple[list[float], list[float]]:
    """Find support and resistance levels from recent price action."""
    supports = []
    resistances = []

    if len(close) < window:
        return supports, resistances

    # Find local minima (supports) and maxima (resistances)
    for i in range(window, len(close) - 1):
        window_slice = close.iloc[i - window : i + 1]
        if close.iloc[i] == window_slice.min():
            supports.append(round(float(close.iloc[i]), 2))
        if close.iloc[i] == window_slice.max():
            resistances.append(round(float(close.iloc[i]), 2))

    # Deduplicate — cluster nearby levels (within 1%)
    supports = _cluster_levels(supports)
    resistances = _cluster_levels(resistances)

    current = float(close.iloc[-1])
    supports = [s for s in supports if s < current][-3:]  # nearest 3 below
    resistances = [r for r in resistances if r > current][:3]  # nearest 3 above

    return supports, resistances


def _cluster_levels(levels: list[float], pct: float = 0.01) -> list[float]:
    """Cluster nearby price levels within pct%."""
    if not levels:
        return []
    levels = sorted(set(levels))
    clustered = [levels[0]]
    for level in levels[1:]:
        if abs(level - clustered[-1]) / clustered[-1] > pct:
            clustered.append(level)
    return clustered


def analyze(ticker: str, df: pd.DataFrame) -> TechnicalResult:
    """
    Run full technical analysis on OHLCV DataFrame.

    Args:
        ticker: Stock ticker symbol
        df: DataFrame with columns Open, High, Low, Close, Volume (DatetimeIndex)

    Returns:
        TechnicalResult with all indicators and composite score
    """
    result = TechnicalResult(ticker=ticker)

    if df.empty or len(df) < 30:
        logger.warning("Insufficient data for %s (%d bars)", ticker, len(df))
        return result

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # ── RSI ──
    rsi_series = compute_rsi(close)
    result.rsi = round(float(rsi_series.iloc[-1]), 2) if not rsi_series.iloc[-1] != rsi_series.iloc[-1] else None
    if result.rsi is not None:
        if result.rsi < 30:
            result.rsi_signal = "OVERSOLD"
        elif result.rsi > 70:
            result.rsi_signal = "OVERBOUGHT"
        else:
            result.rsi_signal = "NEUTRAL"

    # ── MACD ──
    macd_line, signal_line, histogram = compute_macd(close)
    result.macd = round(float(macd_line.iloc[-1]), 4)
    result.macd_signal_line = round(float(signal_line.iloc[-1]), 4)
    result.macd_histogram = round(float(histogram.iloc[-1]), 4)

    # Detect crossover
    if len(histogram) >= 2:
        if histogram.iloc[-1] > 0 and histogram.iloc[-2] <= 0:
            result.macd_crossover = "BULLISH"
        elif histogram.iloc[-1] < 0 and histogram.iloc[-2] >= 0:
            result.macd_crossover = "BEARISH"
        else:
            result.macd_crossover = "NONE"

    # ── Bollinger Bands ──
    bb_upper, bb_middle, bb_lower = compute_bollinger_bands(close)
    result.bb_upper = round(float(bb_upper.iloc[-1]), 2)
    result.bb_middle = round(float(bb_middle.iloc[-1]), 2)
    result.bb_lower = round(float(bb_lower.iloc[-1]), 2)

    bb_range = bb_upper.iloc[-1] - bb_lower.iloc[-1]
    if bb_range > 0:
        result.bb_position = round(
            float((close.iloc[-1] - bb_lower.iloc[-1]) / bb_range), 3
        )

    # ── ATR ──
    atr = compute_atr(high, low, close)
    result.atr = round(float(atr.iloc[-1]), 2) if not pd.isna(atr.iloc[-1]) else None

    # ── OBV ──
    obv = compute_obv(close, volume)
    result.obv = float(obv.iloc[-1])
    if len(obv) >= 20:
        obv_sma = obv.rolling(20).mean()
        if obv.iloc[-1] > obv_sma.iloc[-1] * 1.02:
            result.obv_trend = "RISING"
        elif obv.iloc[-1] < obv_sma.iloc[-1] * 0.98:
            result.obv_trend = "FALLING"
        else:
            result.obv_trend = "FLAT"

    # ── EMAs ──
    for span, attr in [(9, "ema_9"), (21, "ema_21"), (50, "ema_50"), (200, "ema_200")]:
        if len(close) >= span:
            ema = close.ewm(span=span, adjust=False).mean()
            setattr(result, attr, round(float(ema.iloc[-1]), 2))

    # ── Volume Spike ──
    result.volume_spike = detect_volume_spike(volume)

    # ── Candlestick Patterns ──
    result.patterns_detected = detect_patterns(df)

    # ── Support / Resistance ──
    result.support_levels, result.resistance_levels = find_support_resistance(close)

    # ── Trend Detection ──
    if result.ema_50 and result.ema_200:
        if result.ema_50 > result.ema_200:
            result.trend = "UPTREND"
        elif result.ema_50 < result.ema_200:
            result.trend = "DOWNTREND"
        else:
            result.trend = "SIDEWAYS"
    elif result.ema_21 and result.ema_50:
        if result.ema_21 > result.ema_50:
            result.trend = "UPTREND"
        else:
            result.trend = "DOWNTREND"

    # ── Composite Score (0–100) ──
    result.composite_score, result.signals = _compute_composite_score(result)

    return result


def _compute_composite_score(r: TechnicalResult) -> tuple[float, list[dict]]:
    """
    Compute composite technical score (0–100).

    Bullish signals add points, bearish subtract.
    """
    score = 50.0  # Start neutral
    signals = []

    # RSI (max ±15 points)
    if r.rsi is not None:
        if r.rsi < 30:
            pts = 15
            signals.append({"name": "RSI Oversold", "impact": "BULLISH", "points": pts})
            score += pts
        elif r.rsi < 40:
            pts = 8
            signals.append({"name": "RSI Low", "impact": "BULLISH", "points": pts})
            score += pts
        elif r.rsi > 70:
            pts = -15
            signals.append({"name": "RSI Overbought", "impact": "BEARISH", "points": pts})
            score += pts
        elif r.rsi > 60:
            pts = -5
            signals.append({"name": "RSI High", "impact": "BEARISH", "points": pts})
            score += pts

    # MACD Crossover (max ±12 points)
    if r.macd_crossover == "BULLISH":
        pts = 12
        signals.append({"name": "MACD Bullish Crossover", "impact": "BULLISH", "points": pts})
        score += pts
    elif r.macd_crossover == "BEARISH":
        pts = -12
        signals.append({"name": "MACD Bearish Crossover", "impact": "BEARISH", "points": pts})
        score += pts

    # Bollinger Band Position (max ±8 points)
    if r.bb_position is not None:
        if r.bb_position < 0.2:
            pts = 8
            signals.append({"name": "Near Lower BB", "impact": "BULLISH", "points": pts})
            score += pts
        elif r.bb_position > 0.8:
            pts = -8
            signals.append({"name": "Near Upper BB", "impact": "BEARISH", "points": pts})
            score += pts

    # OBV Trend (max ±6 points)
    if r.obv_trend == "RISING":
        pts = 6
        signals.append({"name": "OBV Rising", "impact": "BULLISH", "points": pts})
        score += pts
    elif r.obv_trend == "FALLING":
        pts = -6
        signals.append({"name": "OBV Falling", "impact": "BEARISH", "points": pts})
        score += pts

    # EMA Trend (max ±10 points)
    if r.trend == "UPTREND":
        pts = 10
        signals.append({"name": "EMA Uptrend", "impact": "BULLISH", "points": pts})
        score += pts
    elif r.trend == "DOWNTREND":
        pts = -10
        signals.append({"name": "EMA Downtrend", "impact": "BEARISH", "points": pts})
        score += pts

    # Volume Spike (±5 points — bullish if price is rising)
    if r.volume_spike:
        if r.rsi and r.rsi > 50:
            pts = 5
            signals.append({"name": "Volume Spike (Bullish)", "impact": "BULLISH", "points": pts})
        else:
            pts = -5
            signals.append({"name": "Volume Spike (Bearish)", "impact": "BEARISH", "points": pts})
        score += pts

    # Candlestick Patterns (±5 points each)
    bullish_patterns = {"Hammer", "Bullish Engulfing", "Morning Star"}
    bearish_patterns = {"Bearish Engulfing"}
    for pattern in r.patterns_detected:
        if pattern in bullish_patterns:
            pts = 5
            signals.append({"name": f"Pattern: {pattern}", "impact": "BULLISH", "points": pts})
            score += pts
        elif pattern in bearish_patterns:
            pts = -5
            signals.append({"name": f"Pattern: {pattern}", "impact": "BEARISH", "points": pts})
            score += pts

    # Clamp to 0–100
    score = max(0.0, min(100.0, score))
    return round(score, 1), signals
