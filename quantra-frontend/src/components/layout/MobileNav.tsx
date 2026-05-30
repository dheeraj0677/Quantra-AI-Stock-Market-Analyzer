import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Search, LineChart, PieChart, BellRing } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useNotificationStore } from '@/store/notificationStore';

const mobileItems = [
  { icon: LayoutDashboard, label: 'Dash', path: '/dashboard' },
  { icon: Search, label: 'Search', path: '/screener' },
  { icon: LineChart, label: 'Research', path: '/research' },
  { icon: PieChart, label: 'Portfolio', path: '/portfolio' },
  { icon: BellRing, label: 'Alerts', path: '/alerts', badge: true },
];

export function MobileNav() {
  const { unreadAlerts } = useNotificationStore();

  return (
    <nav className="fixed bottom-0 left-0 z-40 flex h-16 w-full items-center justify-around border-t bg-background/95 backdrop-blur md:hidden pb-safe">
      {mobileItems.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          className={({ isActive }) =>
            cn(
              'flex flex-col items-center justify-center gap-1 px-2 py-1 text-xs transition-colors relative',
              isActive ? 'text-primary' : 'text-muted-foreground hover:text-foreground'
            )
          }
        >
          <item.icon className="h-5 w-5" />
          <span>{item.label}</span>
          {item.badge && unreadAlerts > 0 && (
            <span className="absolute right-1 top-0 flex h-3 w-3 items-center justify-center rounded-full bg-primary text-[8px] font-bold text-primary-foreground">
              {unreadAlerts > 9 ? '9+' : unreadAlerts}
            </span>
          )}
        </NavLink>
      ))}
    </nav>
  );
}
