import { create } from 'zustand';

interface NotificationState {
  unreadAlerts: number;
  incrementAlerts: () => void;
  resetAlerts: () => void;
  setAlertCount: (count: number) => void;
}

export const useNotificationStore = create<NotificationState>()((set) => ({
  unreadAlerts: 0,
  incrementAlerts: () => set((s) => ({ unreadAlerts: s.unreadAlerts + 1 })),
  resetAlerts: () => set({ unreadAlerts: 0 }),
  setAlertCount: (count) => set({ unreadAlerts: count }),
}));
