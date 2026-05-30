import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { AppShell } from '@/components/layout/AppShell';
import { LoginPage } from '@/app/auth/LoginPage';
import { RegisterPage } from '@/app/auth/RegisterPage';
import { OnboardingPage } from '@/app/auth/OnboardingPage';
import { DashboardPage } from '@/app/dashboard/DashboardPage';
import { ScreenerPage } from '@/app/screener/ScreenerPage';
import { StockSearchPage } from '@/app/stocks/StockSearchPage';
import { StockDetailPage } from '@/app/stocks/StockDetailPage';
import { PortfolioPage } from '@/app/portfolio/PortfolioPage';
import { PortfolioDetailPage } from '@/app/portfolio/PortfolioDetailPage';
import { AlertsPage } from '@/app/alerts/AlertsPage';
import { BacktestPage } from '@/app/backtest/BacktestPage';
import { BacktestResultPage } from '@/app/backtest/BacktestResultPage';
import { SuggestionsPage } from '@/app/suggestions/SuggestionsPage';
import { SettingsPage } from '@/app/settings/SettingsPage';
import { useAuthStore } from '@/store/authStore';

const queryClient = new QueryClient();

// Guest guard (redirect to dashboard if logged in)
function GuestRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <>{children}</>;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          
          <Route path="/login" element={
            <GuestRoute>
              <LoginPage />
            </GuestRoute>
          } />
          <Route path="/register" element={
            <GuestRoute>
              <RegisterPage />
            </GuestRoute>
          } />
          
          <Route element={<AppShell />}>
            <Route path="/onboarding" element={<OnboardingPage />} />
            
            {/* Dashboard and Market Components */}
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/screener" element={<ScreenerPage />} />
            <Route path="/research" element={<StockSearchPage />} />
            <Route path="/stocks/:ticker" element={<StockDetailPage />} />
            <Route path="/portfolio" element={<PortfolioPage />} />
            <Route path="/portfolio/:id" element={<PortfolioDetailPage />} />
            <Route path="/alerts" element={<AlertsPage />} />
            <Route path="/backtest" element={<BacktestPage />} />
            <Route path="/backtest/:id" element={<BacktestResultPage />} />
            <Route path="/suggestions" element={<SuggestionsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" />
    </QueryClientProvider>
  );
}
