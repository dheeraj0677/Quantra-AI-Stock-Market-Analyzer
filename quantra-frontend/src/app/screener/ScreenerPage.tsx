import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Filter, Play } from 'lucide-react';
import { screenerApi } from '@/api/screener';
import type { ScreenerFilter } from '@/types/screener';
import { SCREENER_FIELDS, SCREENER_OPERATORS } from '@/types/screener';
import { formatCurrency, formatPct, formatLargeNum } from '@/utils/formatters';
import { getPnLColor } from '@/utils/colors';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Link } from 'react-router-dom';

export function ScreenerPage() {
  const [filters, setFilters] = useState<ScreenerFilter[]>([]);
  const [activePreset, setActivePreset] = useState<string | null>(null);

  const { data: presets } = useQuery({
    queryKey: ['screenerPresets'],
    queryFn: screenerApi.getPresets,
  });

  const { data: results, isLoading, refetch } = useQuery({
    queryKey: ['screenerResults', filters],
    queryFn: () => screenerApi.run({ filters, limit: 50 }),
    enabled: false, // Run manually
  });

  const addFilter = () => {
    setFilters([...filters, { field: 'pe_ratio', operator: '<', value: 15 }]);
    setActivePreset(null);
  };

  const updateFilter = (index: number, updates: Partial<ScreenerFilter>) => {
    const newFilters = [...filters];
    newFilters[index] = { ...newFilters[index], ...updates };
    setFilters(newFilters);
  };

  const removeFilter = (index: number) => {
    setFilters(filters.filter((_, i) => i !== index));
  };

  const loadPreset = (presetId: string) => {
    const preset = presets?.find(p => p.id === presetId);
    if (preset) {
      setFilters(preset.filters);
      setActivePreset(presetId);
    }
  };

  const handleRun = () => {
    refetch();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Stock Screener</h1>
          <p className="text-muted-foreground">Filter the market using technical and AI criteria</p>
        </div>
        
        {presets && presets.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Presets:</span>
            <div className="flex gap-2">
              {presets.map(p => (
                <Button 
                  key={p.id} 
                  variant={activePreset === p.id ? "default" : "outline"} 
                  size="sm"
                  onClick={() => loadPreset(p.id)}
                >
                  {p.name}
                </Button>
              ))}
            </div>
          </div>
        )}
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Filter className="h-4 w-4" /> Filters
          </CardTitle>
          <CardDescription>Add criteria to narrow down stocks</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {filters.map((filter, index) => {
            const fieldDef = SCREENER_FIELDS.find(f => f.value === filter.field);
            const operators = fieldDef ? SCREENER_OPERATORS[fieldDef.type] : [];

            return (
              <div key={index} className="flex flex-wrap items-center gap-2">
                <Select
                  value={filter.field}
                  onValueChange={(val: any) => updateFilter(index, { field: val, operator: SCREENER_OPERATORS[SCREENER_FIELDS.find(f => f.value === val)!.type][0] as any })}
                >
                  <SelectTrigger className="w-[180px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {SCREENER_FIELDS.map(f => (
                      <SelectItem key={f.value} value={f.value}>{f.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <Select
                  value={filter.operator}
                  onValueChange={(val: any) => updateFilter(index, { operator: val })}
                >
                  <SelectTrigger className="w-[100px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {operators.map(op => (
                      <SelectItem key={op} value={op}>{op}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                {filter.operator === 'between' ? (
                  <div className="flex items-center gap-2">
                    <Input 
                      type={fieldDef?.type === 'number' ? 'number' : 'text'} 
                      className="w-[100px]" 
                      value={Array.isArray(filter.value) ? filter.value[0] : ''}
                      onChange={(e: any) => updateFilter(index, { value: [Number(e.target.value), Array.isArray(filter.value) ? (filter.value[1] as number) : 0] })}
                    />
                    <span className="text-muted-foreground">and</span>
                    <Input 
                      type={fieldDef?.type === 'number' ? 'number' : 'text'} 
                      className="w-[100px]" 
                      value={Array.isArray(filter.value) ? filter.value[1] : ''}
                      onChange={(e: any) => updateFilter(index, { value: [Array.isArray(filter.value) ? (filter.value[0] as number) : 0, Number(e.target.value)] })}
                    />
                  </div>
                ) : (
                  <Input 
                    type={fieldDef?.type === 'number' ? 'number' : 'text'} 
                    className="w-[150px]" 
                    value={filter.value as string}
                    onChange={(e: any) => updateFilter(index, { value: fieldDef?.type === 'number' ? Number(e.target.value) : e.target.value })}
                  />
                )}

                <Button variant="ghost" size="icon" onClick={() => removeFilter(index)} className="text-muted-foreground hover:text-destructive">
                  &times;
                </Button>
              </div>
            );
          })}

          <div className="flex items-center justify-between pt-2">
            <Button variant="outline" onClick={addFilter} size="sm">
              + Add Filter
            </Button>
            <div className="flex gap-2">
              <Button onClick={handleRun} disabled={isLoading || filters.length === 0} className="gap-2">
                {isLoading ? <Play className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                Run Screener
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-muted/50 text-muted-foreground">
                <tr className="border-b text-left">
                  <th className="font-medium p-4">Ticker</th>
                  <th className="font-medium p-4">Price</th>
                  <th className="font-medium p-4">Change</th>
                  <th className="font-medium p-4 hidden md:table-cell">Sector</th>
                  <th className="font-medium p-4">AI Score</th>
                  <th className="font-medium p-4 hidden sm:table-cell">P/E</th>
                  <th className="font-medium p-4 text-right">Volume</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr>
                    <td colSpan={7} className="p-8 text-center text-muted-foreground">Loading results...</td>
                  </tr>
                ) : !results ? (
                  <tr>
                    <td colSpan={7} className="p-8 text-center text-muted-foreground">Add filters and run the screener to see results</td>
                  </tr>
                ) : results.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="p-8 text-center text-muted-foreground">No stocks match your criteria</td>
                  </tr>
                ) : (
                  results.map((stock) => (
                    <tr key={stock.ticker} className="border-b transition-colors hover:bg-muted/50 last:border-0">
                      <td className="p-4 font-semibold">
                        <Link to={`/stocks/${stock.ticker}`} className="hover:underline text-primary">
                          {stock.ticker}
                        </Link>
                      </td>
                      <td className="p-4 font-medium">{formatCurrency(stock.price, 'USD')}</td>
                      <td className={`p-4 font-medium ${getPnLColor(stock.change_pct)}`}>
                        {formatPct(stock.change_pct)}
                      </td>
                      <td className="p-4 hidden md:table-cell text-muted-foreground">{stock.sector}</td>
                      <td className="p-4">
                        <Badge variant="outline" className={stock.direction === 'UP' ? 'text-emerald-500 border-emerald-500/30 bg-emerald-500/10' : stock.direction === 'DOWN' ? 'text-red-500 border-red-500/30 bg-red-500/10' : ''}>
                          {stock.ml_score}/100
                        </Badge>
                      </td>
                      <td className="p-4 hidden sm:table-cell">{stock.pe?.toFixed(2) || '-'}</td>
                      <td className="p-4 text-right text-muted-foreground">{formatLargeNum(stock.volume)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
