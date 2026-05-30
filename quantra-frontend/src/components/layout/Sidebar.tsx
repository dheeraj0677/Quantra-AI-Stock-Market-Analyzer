import { NavLink } from 'react-router-dom';
import { LayoutDashboard, LineChart, Search, PieChart, BellRing, History, Lightbulb, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useNotificationStore } from '@/store/notificationStore';

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: Search, label: 'Screener', path: '/screener' },
  { icon: LineChart, label: 'Research', path: '/research' },
  { icon: PieChart, label: 'Portfolio', path: '/portfolio' },
  { icon: BellRing, label: 'Alerts', path: '/alerts', badge: true },
  { icon: History, label: 'Backtest', path: '/backtest' },
  { icon: Lightbulb, label: 'Suggestions', path: '/suggestions' },
];

export function Sidebar() {
  const { unreadAlerts } = useNotificationStore();

  return (
    <aside className="fixed left-0 top-0 z-40 hidden h-screen w-64 flex-col border-r bg-card md:flex">
      <div className="flex h-16 items-center border-b px-6">
        <h1 className="text-xl font-bold tracking-tight text-primary">
          Quantra<span className="text-emerald-500">.</span>
        </h1>
      </div>
      <div className="flex-1 overflow-y-auto py-4">
        <nav className="flex flex-col gap-2 px-4">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground',
                  isActive ? 'bg-accent text-accent-foreground' : 'text-muted-foreground'
                )
              }
            >
              <item.icon className="h-5 w-5" />
              {item.label}
              {item.badge && unreadAlerts > 0 && (
                <span className="ml-auto flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
                  {unreadAlerts}
                </span>
              )}
            </NavLink>
          ))}
        </nav>
      </div>
      <div className="border-t p-4">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground',
              isActive ? 'bg-accent text-accent-foreground' : 'text-muted-foreground'
            )
          }
        >
          <Settings className="h-5 w-5" />
          Settings
        </NavLink>
      </div>
    </aside>
  );
}
