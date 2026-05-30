import type { Direction } from '../types/prediction';

export const directionColors: Record<Direction, { bg: string; text: string; border: string }> = {
  UP: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30' },
  DOWN: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/30' },
  SIDEWAYS: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/30' },
};

export const sentimentColors: Record<string, { bg: string; text: string }> = {
  POSITIVE: { bg: 'bg-emerald-500/15', text: 'text-emerald-400' },
  NEGATIVE: { bg: 'bg-red-500/15', text: 'text-red-400' },
  NEUTRAL: { bg: 'bg-slate-500/15', text: 'text-slate-400' },
};

export const suggestionActionColors: Record<string, { bg: string; text: string; border: string }> = {
  BUY: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30' },
  WATCH: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/30' },
  AVOID: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/30' },
};

export function getPnLColor(value: number): string {
  if (value > 0) return 'text-emerald-400';
  if (value < 0) return 'text-red-400';
  return 'text-slate-400';
}

export function getPnLBgColor(value: number): string {
  if (value > 0) return 'bg-emerald-500/10';
  if (value < 0) return 'bg-red-500/10';
  return 'bg-slate-500/10';
}

export const chartColors = {
  up: '#22c55e',
  down: '#ef4444',
  neutral: '#94a3b8',
  primary: '#6366f1',
  secondary: '#8b5cf6',
  grid: '#1e293b',
  text: '#94a3b8',
  background: '#0f172a',
};
