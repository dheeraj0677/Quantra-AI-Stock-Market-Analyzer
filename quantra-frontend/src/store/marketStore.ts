import { create } from 'zustand';

interface PriceData {
  price: number;
  change_pct: number;
  updated_at: number;
}

interface MarketState {
  prices: Record<string, PriceData>;
  setPrice: (ticker: string, price: number, change_pct: number) => void;
  getPrice: (ticker: string) => PriceData | undefined;
  clearPrices: () => void;
}

export const useMarketStore = create<MarketState>()((set, get) => ({
  prices: {},

  setPrice: (ticker, price, change_pct) =>
    set((state) => ({
      prices: {
        ...state.prices,
        [ticker]: { price, change_pct, updated_at: Date.now() },
      },
    })),

  getPrice: (ticker) => get().prices[ticker],

  clearPrices: () => set({ prices: {} }),
}));
