const fs = require('fs');

let f1 = fs.readFileSync('src/app/alerts/AlertsPage.tsx', 'utf8');
f1 = f1.replace('import { alertsApi, type Alert } from ''@/api/alerts'';', 'import { alertsApi } from ''@/api/alerts'';');
fs.writeFileSync('src/app/alerts/AlertsPage.tsx', f1);

let f2 = fs.readFileSync('src/app/stocks/StockDetailPage.tsx', 'utf8');
f2 = f2.replace('import { useState } from ''react'';\n', '');
f2 = f2.replace('import { Activity, LayoutDashboard, LineChart, Newspaper, Brain } from ''lucide-react'';', 'import { LayoutDashboard, LineChart, Newspaper, Brain } from ''lucide-react'';');
fs.writeFileSync('src/app/stocks/StockDetailPage.tsx', f2);

let f3 = fs.readFileSync('src/components/charts/EquityCurveChart.tsx', 'utf8');
f3 = f3.replace('chartColors.primary.main', 'chartColors.primary');
fs.writeFileSync('src/components/charts/EquityCurveChart.tsx', f3);

let f4 = fs.readFileSync('src/components/market/TopMoversTable.tsx', 'utf8');
f4 = f4.replace('Tabs, TabsList, TabsTrigger, TabsContent', 'Tabs, TabsList, TabsTrigger');
fs.writeFileSync('src/components/market/TopMoversTable.tsx', f4);

let f5 = fs.readFileSync('src/components/prediction/DeepResearchPanel.tsx', 'utf8');
f5 = f5.replace('import { Brain, FileText, Loader2, PlayCircle, Target, TrendingUp, TrendingDown, AlertTriangle } from ''lucide-react'';', 'import { Brain, FileText, Loader2, PlayCircle, Target, TrendingDown, AlertTriangle } from ''lucide-react'';');
let lines = f5.split('\n');
if (lines[4].startsWith('import type')) { lines.splice(4, 1); }
fs.writeFileSync('src/components/prediction/DeepResearchPanel.tsx', lines.join('\n'));

console.log('Fixed');
