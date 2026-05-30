/**
 * Client-side helpers for displaying indicator values.
 */

export function rsiLabel(value: number | null): { text: string; color: string } {
  if (value === null) return { text: 'N/A', color: 'text-slate-400' };
  if (value >= 70) return { text: 'Overbought', color: 'text-red-400' };
  if (value <= 30) return { text: 'Oversold', color: 'text-emerald-400' };
  return { text: 'Neutral', color: 'text-slate-400' };
}

export function macdLabel(macd: number | null, signal: number | null): { text: string; color: string } {
  if (macd === null || signal === null) return { text: 'N/A', color: 'text-slate-400' };
  if (macd > signal) return { text: 'Bullish', color: 'text-emerald-400' };
  if (macd < signal) return { text: 'Bearish', color: 'text-red-400' };
  return { text: 'Neutral', color: 'text-slate-400' };
}

export function trendLabel(ema9: number | null, ema21: number | null, price: number): { text: string; color: string } {
  if (ema9 === null || ema21 === null) return { text: 'N/A', color: 'text-slate-400' };
  if (price > ema9 && ema9 > ema21) return { text: 'Strong Uptrend', color: 'text-emerald-400' };
  if (price > ema21) return { text: 'Uptrend', color: 'text-emerald-400' };
  if (price < ema9 && ema9 < ema21) return { text: 'Strong Downtrend', color: 'text-red-400' };
  if (price < ema21) return { text: 'Downtrend', color: 'text-red-400' };
  return { text: 'Sideways', color: 'text-amber-400' };
}

export function scoreLabel(score: number): { text: string; color: string } {
  if (score >= 80) return { text: 'Strong Buy', color: 'text-emerald-400' };
  if (score >= 60) return { text: 'Buy', color: 'text-green-400' };
  if (score >= 40) return { text: 'Hold', color: 'text-amber-400' };
  if (score >= 20) return { text: 'Sell', color: 'text-orange-400' };
  return { text: 'Strong Sell', color: 'text-red-400' };
}
