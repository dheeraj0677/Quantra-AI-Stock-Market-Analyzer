import { useEffect, useRef } from 'react';
import { useAuthStore } from '@/store/authStore';
import { useMarketStore } from '@/store/marketStore';

export function useSSE(endpoint: string = '/api/v1/market/stream') {
  const { accessToken } = useAuthStore();
  const { setPrice } = useMarketStore();
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!accessToken) return;

    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    // EventSource doesn't support custom headers (like Authorization: Bearer ...) natively in all browsers
    // A common workaround is passing the token in the URL query string if the backend supports it,
    // or using a polyfill. We'll pass it in the query string here.
    const url = `${baseURL}${endpoint}?token=${accessToken}`;

    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'price_update') {
          setPrice(data.ticker, data.price, data.change_pct);
        }
      } catch (err) {
        console.error('Failed to parse SSE message', err);
      }
    };

    es.onerror = (err) => {
      console.error('SSE Error:', err);
      es.close();
    };

    return () => {
      es.close();
    };
  }, [endpoint, accessToken, setPrice]);

  return eventSourceRef;
}
