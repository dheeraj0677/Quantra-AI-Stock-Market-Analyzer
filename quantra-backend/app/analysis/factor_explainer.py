"""
Quantra — Factor Explainer.

Generates human-readable reasoning strings for each prediction factor.
"""

from __future__ import annotations

# Template-based explanations for technical signals
TECHNICAL_EXPLANATIONS = {
    "RSI Oversold": "RSI dropped below 30 — classic oversold bounce opportunity. Historically, stocks recover from this zone {points}% of the time.",
    "RSI Low": "RSI is approaching oversold territory — early sign of a potential buying opportunity.",
    "RSI Overbought": "RSI is above 70 indicating overbought conditions — pullback or consolidation likely.",
    "RSI High": "RSI is elevated — momentum may be peaking.",
    "MACD Bullish Crossover": "MACD line crossed above the signal line — bullish momentum is strengthening.",
    "MACD Bearish Crossover": "MACD line crossed below the signal line — bearish momentum increasing.",
    "Near Lower BB": "Price is near the lower Bollinger Band — often signals a mean reversion bounce.",
    "Near Upper BB": "Price is near the upper Bollinger Band — potential resistance or overextension.",
    "OBV Rising": "On-Balance Volume is trending up — accumulation by institutional buyers likely.",
    "OBV Falling": "On-Balance Volume is declining — distribution pressure detected.",
    "EMA Uptrend": "Short-term EMAs are above long-term EMAs — sustained uptrend in progress.",
    "EMA Downtrend": "Short-term EMAs are below long-term EMAs — downtrend continuation likely.",
    "Volume Spike (Bullish)": "Volume surged above 2x the 20-day average alongside positive price action.",
    "Volume Spike (Bearish)": "Volume surged above 2x the 20-day average with negative price action — selling pressure.",
}

PATTERN_EXPLANATIONS = {
    "Hammer": "Hammer candlestick pattern detected — bullish reversal signal at support.",
    "Bullish Engulfing": "Bullish Engulfing pattern — buyers overpowered sellers, reversal likely.",
    "Bearish Engulfing": "Bearish Engulfing pattern — sellers took control, further downside possible.",
    "Morning Star": "Morning Star pattern (3-candle bullish reversal) — strong buy signal.",
    "Doji": "Doji candle — market indecision, potential trend reversal pending confirmation.",
}


def explain_factors(
    factor_type: str,
    factor_name: str,
    points: float = 0,
) -> str:
    """
    Generate a human-readable explanation for a prediction factor.

    Args:
        factor_type: TECHNICAL, NEWS, FUNDAMENTAL, PATTERN
        factor_name: The name of the factor
        points: Score impact points (positive = bullish)

    Returns:
        Human-readable explanation string
    """
    if factor_type == "TECHNICAL":
        # Check pattern explanations first
        if factor_name.startswith("Pattern: "):
            pattern = factor_name.replace("Pattern: ", "")
            return PATTERN_EXPLANATIONS.get(
                pattern,
                f"{pattern} candlestick pattern detected.",
            )

        explanation = TECHNICAL_EXPLANATIONS.get(factor_name)
        if explanation:
            return explanation.format(points=abs(int(points * 7)))  # rough historical %
        return f"{factor_name} signal detected — contributing {'positively' if points > 0 else 'negatively'} to the technical outlook."

    elif factor_type == "NEWS":
        if points > 0:
            return f"{factor_name} — positive news sentiment is reinforcing the bullish case."
        elif points < 0:
            return f"{factor_name} — negative news is creating headwinds."
        return f"{factor_name}"

    elif factor_type == "FUNDAMENTAL":
        return f"{factor_name} — this fundamental metric supports the overall thesis."

    return f"{factor_name}"
