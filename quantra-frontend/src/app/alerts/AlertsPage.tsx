import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Bell, BellOff, Plus, Trash2 } from 'lucide-react';
import { alertsApi } from '@/api/alerts';
import { formatCurrency } from '@/utils/formatters';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { formatRelativeTime } from '@/utils/formatters';

export function AlertsPage() {
  const queryClient = useQueryClient();
  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: alertsApi.getAlerts,
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, active }: { id: string, active: boolean }) => alertsApi.toggleAlert(id, active),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => alertsApi.deleteAlert(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Price & Signal Alerts</h1>
          <p className="text-muted-foreground">Get notified when stocks hit your targets or AI signals change</p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          Create Alert
        </Button>
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="h-32 animate-pulse bg-muted/50" />
          ))}
        </div>
      ) : !alerts || alerts.length === 0 ? (
        <Card className="flex flex-col items-center justify-center p-12 text-center">
          <Bell className="mb-4 h-12 w-12 text-muted-foreground opacity-20" />
          <h3 className="text-lg font-medium">No Alerts Set</h3>
          <p className="mt-2 mb-6 text-sm text-muted-foreground max-w-sm">
            Create alerts for price targets, volume spikes, or AI prediction changes.
          </p>
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            Create Alert
          </Button>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {alerts.map((alert) => (
            <Card key={alert.id} className={!alert.is_active ? 'opacity-60' : ''}>
              <CardContent className="p-4 sm:p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-bold text-lg">{alert.ticker}</h3>
                    <div className="mt-1 flex items-center gap-2">
                      <span className="text-sm text-muted-foreground">{alert.condition}</span>
                      <span className="font-medium">{formatCurrency(alert.threshold, 'USD')}</span>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <Switch 
                      checked={alert.is_active} 
                      onCheckedChange={(c) => toggleMutation.mutate({ id: alert.id, active: c })}
                    />
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="h-8 w-8 text-muted-foreground hover:text-destructive"
                      onClick={() => deleteMutation.mutate(alert.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                
                <div className="mt-4 pt-4 border-t flex items-center justify-between text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    {alert.is_active ? <Bell className="h-3 w-3 text-primary" /> : <BellOff className="h-3 w-3" />}
                    {alert.is_active ? 'Active' : 'Paused'}
                  </span>
                  {alert.triggered_at ? (
                    <span className="text-amber-500">Triggered {formatRelativeTime(alert.triggered_at)}</span>
                  ) : (
                    <span>Created {formatRelativeTime(alert.created_at)}</span>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
