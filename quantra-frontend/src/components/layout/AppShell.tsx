import { Outlet, Navigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { MobileNav } from './MobileNav';
import { useAuthStore } from '@/store/authStore';

export function AppShell() {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex min-h-screen w-full bg-background">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Topbar />
        <main className="flex-1 pb-16 md:pb-0 md:pl-64">
          <div className="h-full p-4 md:p-8 w-full max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
        <MobileNav />
      </div>
    </div>
  );
}
