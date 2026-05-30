import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, TrendingUp, Shield, Zap } from 'lucide-react';
import { authApi } from '@/api/auth';
import { useAuthStore } from '@/store/authStore';
import toast from 'react-hot-toast';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';

export function OnboardingPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [riskProfile, setRiskProfile] = useState('moderate');
  const [horizon, setHorizon] = useState('medium');
  const navigate = useNavigate();
  const { updatePreferences } = useAuthStore();

  const handleComplete = async () => {
    try {
      setIsLoading(true);
      await authApi.updatePreferences({
        risk_profile: riskProfile,
        investment_horizon: horizon,
      });
      updatePreferences({
        risk_profile: riskProfile as any,
        investment_horizon: horizon as any,
      });
      toast.success('Preferences saved!');
      navigate('/dashboard');
    } catch (error) {
      toast.error('Failed to save preferences');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background p-4 md:p-8">
      <div className="w-full max-w-3xl space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Welcome to Quantra</h1>
          <p className="text-muted-foreground">Let&apos;s personalize your AI investing experience</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Risk Tolerance</CardTitle>
              <CardDescription>How much risk are you comfortable with?</CardDescription>
            </CardHeader>
            <CardContent>
              <RadioGroup value={riskProfile} onValueChange={setRiskProfile} className="space-y-3">
                <div className="flex items-center space-x-3 space-y-0 rounded-md border p-4 hover:bg-accent/50 transition-colors cursor-pointer" onClick={() => setRiskProfile('conservative')}>
                  <RadioGroupItem value="conservative" id="conservative" />
                  <div className="flex-1 space-y-1">
                    <Label htmlFor="conservative" className="font-medium flex items-center gap-2 cursor-pointer">
                      <Shield className="h-4 w-4 text-emerald-500" /> Conservative
                    </Label>
                    <p className="text-xs text-muted-foreground">Focus on capital preservation and steady income.</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 space-y-0 rounded-md border p-4 hover:bg-accent/50 transition-colors cursor-pointer" onClick={() => setRiskProfile('moderate')}>
                  <RadioGroupItem value="moderate" id="moderate" />
                  <div className="flex-1 space-y-1">
                    <Label htmlFor="moderate" className="font-medium flex items-center gap-2 cursor-pointer">
                      <TrendingUp className="h-4 w-4 text-blue-500" /> Moderate
                    </Label>
                    <p className="text-xs text-muted-foreground">Balance between growth and capital preservation.</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 space-y-0 rounded-md border p-4 hover:bg-accent/50 transition-colors cursor-pointer" onClick={() => setRiskProfile('aggressive')}>
                  <RadioGroupItem value="aggressive" id="aggressive" />
                  <div className="flex-1 space-y-1">
                    <Label htmlFor="aggressive" className="font-medium flex items-center gap-2 cursor-pointer">
                      <Zap className="h-4 w-4 text-amber-500" /> Aggressive
                    </Label>
                    <p className="text-xs text-muted-foreground">Maximize growth, comfortable with high volatility.</p>
                  </div>
                </div>
              </RadioGroup>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Investment Horizon</CardTitle>
              <CardDescription>How long do you plan to hold your investments?</CardDescription>
            </CardHeader>
            <CardContent>
              <RadioGroup value={horizon} onValueChange={setHorizon} className="space-y-3">
                <div className="flex items-center space-x-3 space-y-0 rounded-md border p-4 hover:bg-accent/50 transition-colors cursor-pointer" onClick={() => setHorizon('short')}>
                  <RadioGroupItem value="short" id="short" />
                  <div className="flex-1 space-y-1">
                    <Label htmlFor="short" className="font-medium cursor-pointer">Short-term</Label>
                    <p className="text-xs text-muted-foreground">Swing trading (days to weeks)</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 space-y-0 rounded-md border p-4 hover:bg-accent/50 transition-colors cursor-pointer" onClick={() => setHorizon('medium')}>
                  <RadioGroupItem value="medium" id="medium" />
                  <div className="flex-1 space-y-1">
                    <Label htmlFor="medium" className="font-medium cursor-pointer">Medium-term</Label>
                    <p className="text-xs text-muted-foreground">Months to a few years</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 space-y-0 rounded-md border p-4 hover:bg-accent/50 transition-colors cursor-pointer" onClick={() => setHorizon('long')}>
                  <RadioGroupItem value="long" id="long" />
                  <div className="flex-1 space-y-1">
                    <Label htmlFor="long" className="font-medium cursor-pointer">Long-term</Label>
                    <p className="text-xs text-muted-foreground">Buy and hold (5+ years)</p>
                  </div>
                </div>
              </RadioGroup>
            </CardContent>
          </Card>
        </div>

        <div className="flex justify-end">
          <Button onClick={handleComplete} disabled={isLoading} size="lg" className="w-full md:w-auto">
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Complete Setup
          </Button>
        </div>
      </div>
    </div>
  );
}
