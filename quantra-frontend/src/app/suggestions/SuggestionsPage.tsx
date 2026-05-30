import { SuggestionFeed } from '@/components/suggestions/SuggestionFeed';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { BrainCircuit, SlidersHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function SuggestionsPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Investment Ideas</h1>
          <p className="text-muted-foreground">Personalized trading suggestions based on your profile</p>
        </div>
        <Button variant="outline" className="gap-2">
          <SlidersHorizontal className="h-4 w-4" />
          Update Risk Profile
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-4">
        <div className="md:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <BrainCircuit className="h-5 w-5 text-primary" />
                Your Profile
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="text-sm font-medium text-muted-foreground">Risk Tolerance</div>
                <div className="font-semibold text-emerald-500">Moderate</div>
              </div>
              <div>
                <div className="text-sm font-medium text-muted-foreground">Investment Horizon</div>
                <div className="font-semibold">Medium Term (3-12 months)</div>
              </div>
              <div>
                <div className="text-sm font-medium text-muted-foreground">Preferred Sectors</div>
                <div className="flex flex-wrap gap-1 mt-1">
                  <span className="text-xs bg-secondary px-2 py-1 rounded">Technology</span>
                  <span className="text-xs bg-secondary px-2 py-1 rounded">Healthcare</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">AI Performance</CardTitle>
              <CardDescription>Historical accuracy of suggestions</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-muted-foreground">Win Rate</span>
                  <span className="font-bold text-emerald-500">68%</span>
                </div>
                <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-500 w-[68%]" />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-muted-foreground">Avg Return</span>
                  <span className="font-bold text-emerald-500">+12.4%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="md:col-span-3">
          <SuggestionFeed />
        </div>
      </div>
    </div>
  );
}
