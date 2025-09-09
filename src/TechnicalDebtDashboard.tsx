import React from "react";
import {
  Activity,
  AlertTriangle,
  BarChart2,
  Bug,
  CalendarClock,
  ChevronRight,
  FileCode2,
  Filter,
  GitCommit,
  Layers,
  LineChart,
  Search,
  Settings,
  TrendingUp
} from "lucide-react";

// shadcn/ui imports (available in canvas runtime)
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

// --- Simple chart/visual placeholders --- //
const Placeholder = ({ label }: { label: string }) => (
  <div className="w-full h-56 rounded-2xl border border-dashed grid place-items-center text-sm text-muted-foreground">
    {label}
  </div>
);

const SmallPlaceholder = ({ label }: { label: string }) => (
  <div className="w-full h-36 rounded-2xl border border-dashed grid place-items-center text-xs text-muted-foreground">
    {label}
  </div>
);

// --- Reusable row for High-Risk Files --- //
function RiskRow({
  file = "src/utils/parser.cpp",
  debt = 78,
  bugs = 12,
  complexity = 24,
  activity = 62
}) {
  return (
    <div className="grid grid-cols-12 items-center gap-3 py-2 px-3 rounded-xl hover:bg-muted/40">
      <div className="col-span-5 flex items-center gap-2 truncate"><FileCode2 className="h-4 w-4"/> <span className="truncate">{file}</span></div>
      <div className="col-span-2 flex items-center gap-2"><AlertTriangle className="h-4 w-4"/> <span>{debt}</span></div>
      <div className="col-span-2 flex items-center gap-2"><Bug className="h-4 w-4"/> <span>{bugs}</span></div>
      <div className="col-span-1 text-center">{complexity}</div>
      <div className="col-span-2">
        <Progress value={activity} className="h-2"/>
      </div>
    </div>
  );
}

export default function TechnicalDebtEvolutionDashboard() {
  return (
    <div className="min-h-screen w-full bg-background text-foreground p-6 lg:p-10">
      {/* Top Bar */}
      <div className="flex flex-wrap items-center gap-3 mb-6">
        <div className="flex items-center gap-3">
          <Layers className="h-6 w-6"/>
          <h1 className="text-2xl font-semibold tracking-tight">Tableau de bord — Dette Technique</h1>
          <Badge variant="secondary" className="rounded-full">Git-based</Badge>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <Button variant="outline" className="gap-2"><Settings className="h-4 w-4"/> Paramètres</Button>
          <Button className="gap-2"><TrendingUp className="h-4 w-4"/> Exporter</Button>
        </div>
      </div>

      {/* Controls */}
      <Card className="mb-6">
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Filtres & exploration</CardTitle>
          <CardDescription>Sélectionnez le dépôt, la période et les métriques à analyser.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-12 gap-3">
            <div className="md:col-span-4 flex items-center gap-2">
              <Label className="w-28">Dépôt</Label>
              <Select defaultValue="main">
                <SelectTrigger className="w-full"><SelectValue placeholder="Choisir"/></SelectTrigger>
                <SelectContent>
                  <SelectItem value="main">acme/monorepo</SelectItem>
                  <SelectItem value="service-a">acme/service-a</SelectItem>
                  <SelectItem value="mobile">acme/mobile-app</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="md:col-span-3 flex items-center gap-2">
              <Label className="w-28">Période</Label>
              <Select defaultValue="90d">
                <SelectTrigger className="w-full"><SelectValue placeholder="Période"/></SelectTrigger>
                <SelectContent>
                  <SelectItem value="30d">30 jours</SelectItem>
                  <SelectItem value="90d">90 jours</SelectItem>
                  <SelectItem value="1y">1 an</SelectItem>
                  <SelectItem value="all">Tout</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="md:col-span-3 flex items-center gap-2">
              <Label className="w-28">Branche</Label>
              <Select defaultValue="main">
                <SelectTrigger className="w-full"><SelectValue placeholder="Branche"/></SelectTrigger>
                <SelectContent>
                  <SelectItem value="main">main</SelectItem>
                  <SelectItem value="develop">develop</SelectItem>
                  <SelectItem value="release">release/*</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="md:col-span-2 flex items-center gap-2">
              <Button variant="outline" className="w-full gap-2"><Filter className="h-4 w-4"/> Affiner</Button>
            </div>
          </div>
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="flex items-center gap-2">
              <Switch id="toggle-todo" defaultChecked />
              <Label htmlFor="toggle-todo">Inclure TODO/FIXME</Label>
            </div>
            <div className="flex items-center gap-2">
              <Switch id="toggle-complexity" defaultChecked />
              <Label htmlFor="toggle-complexity">Inclure complexité</Label>
            </div>
            <div className="flex items-center gap-2">
              <Switch id="toggle-dup" />
              <Label htmlFor="toggle-dup">Inclure duplication</Label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardHeader className="pb-2"><CardDescription>Total instances de dette</CardDescription></CardHeader>
          <CardContent className="flex items-center justify-between">
            <div className="text-3xl font-semibold">1,248</div>
            <BarChart2 className="h-6 w-6"/>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardDescription>Fichiers à risque élevé</CardDescription></CardHeader>
          <CardContent className="flex items-center justify-between">
            <div className="text-3xl font-semibold">37</div>
            <AlertTriangle className="h-6 w-6"/>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardDescription>Bogues liés</CardDescription></CardHeader>
          <CardContent className="flex items-center justify-between">
            <div className="text-3xl font-semibold">112</div>
            <Bug className="h-6 w-6"/>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardDescription>Coût de maintenance (tendance)</CardDescription></CardHeader>
          <CardContent className="flex items-center justify-between">
            <div className="text-3xl font-semibold">+18%</div>
            <TrendingUp className="h-6 w-6"/>
          </CardContent>
        </Card>
      </div>

      {/* Main content split */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Left column: Trends & Correlations */}
        <div className="xl:col-span-2 space-y-6">
          <Card>
            <CardHeader className="pb-2 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-base">Évolution de la dette dans le temps</CardTitle>
                <CardDescription>Somme pondérée (TODO/FIXME, complexité, duplication) par commit/release.</CardDescription>
              </div>
              <Button variant="outline" className="gap-2"><LineChart className="h-4 w-4"/> Métriques</Button>
            </CardHeader>
            <CardContent>
              <Placeholder label="Line chart — Debt over time"/>
              <div className="mt-3 flex items-center gap-2 text-xs text-muted-foreground">
                <GitCommit className="h-3 w-3"/> commits • <CalendarClock className="h-3 w-3"/> releases
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Corrélation dette ↔ bogues</CardTitle>
              <CardDescription>Chaque point = fichier / module (x: sévérité de dette, y: # bogues, couleur: activité de commits).</CardDescription>
            </CardHeader>
            <CardContent>
              <Placeholder label="Scatter plot — Debt severity vs Bugs"/>
            </CardContent>
          </Card>
        </div>

        {/* Right column: Repository map & Search */}
        <div className="space-y-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Carte du dépôt</CardTitle>
              <CardDescription>Treemap Sunburst — densité de dette par répertoire/fichier.</CardDescription>
            </CardHeader>
            <CardContent>
              <SmallPlaceholder label="Treemap / Sunburst — Debt density"/>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Recherche</CardTitle>
              <CardDescription>Trouver un fichier, une fonction ou un TODO.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Input placeholder="ex: src/utils/parser.cpp ou FIXME: memory leak"/>
                <Button className="gap-2"><Search className="h-4 w-4"/> Rechercher</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Drilldown & Guidance */}
      <Card className="mt-6">
        <CardHeader className="pb-0">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base">Fichiers à prioriser</CardTitle>
              <CardDescription>Trié par sévérité estimée (dette, bogues, complexité, activité).</CardDescription>
            </div>
            <Tabs defaultValue="top">
              <TabsList>
                <TabsTrigger value="top">Top risques</TabsTrigger>
                <TabsTrigger value="recent">Récemment dégradés</TabsTrigger>
                <TabsTrigger value="stable">Stables</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-12 text-xs text-muted-foreground px-3 pb-2">
            <div className="col-span-5">Fichier</div>
            <div className="col-span-2">Dette</div>
            <div className="col-span-2">Bogues</div>
            <div className="col-span-1 text-center">Complexité</div>
            <div className="col-span-2">Activité</div>
          </div>
          <div className="space-y-1">
            <RiskRow/>
            <RiskRow file="src/core/cache_manager.cpp" debt={65} bugs={9} complexity={20} activity={48}/>
            <RiskRow file="src/ui/components/graph.tsx" debt={54} bugs={6} complexity={12} activity={35}/>
            <RiskRow file="services/auth/token.go" debt={41} bugs={7} complexity={16} activity={52}/>
          </div>
          <div className="mt-4 flex items-center justify-end">
            <Button variant="ghost" className="gap-1">Voir tout <ChevronRight className="h-4 w-4"/></Button>
          </div>
        </CardContent>
      </Card>

      {/* Guidance & Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recommandations</CardTitle>
            <CardDescription>Actions suggérées sur la base des métriques.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex items-start gap-2">
              <AlertTriangle className="h-4 w-4 mt-0.5"/>
              <div>
                <p><b>Découper</b> <code>src/utils/parser.cpp</code> (fonction &gt; 200 lignes, TODO obsolètes).</p>
                <div className="mt-2 flex gap-2"><Badge variant="secondary">Complexité</Badge><Badge variant="secondary">TODO</Badge></div>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <Activity className="h-4 w-4 mt-0.5"/>
              <div>
                <p>Planifier une <b>campagne de refactor</b> pour modules les plus actifs avant release.</p>
                <div className="mt-2 flex gap-2"><Badge variant="secondary">Activité</Badge><Badge variant="secondary">Release</Badge></div>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <BarChart2 className="h-4 w-4 mt-0.5"/>
              <div>
                <p>Suivre <b>duplication</b> dans <code>core/</code> (soupçon de copier/coller récurrent).</p>
                <div className="mt-2 flex gap-2"><Badge variant="secondary">Duplication</Badge></div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">À faire (Backlog)</CardTitle>
            <CardDescription>Propositions d’extensions par les étudiants.</CardDescription>
          </CardHeader>
          <CardContent className="text-sm space-y-2">
            <div>☐ Extraction automatique des versions à intervalles réguliers.</div>
            <div>☐ Détection de duplication par hashing/AST.</div>
            <div>☐ Liaison bugs ↔ commits (Jira/GitHub Issues).</div>
            <div>☐ Heatmap par auteur / module.</div>
            <div>☐ Prédiction du risque via régression/clustering.</div>
          </CardContent>
        </Card>
      </div>

      {/* Footer */}
      <div className="mt-10 text-xs text-muted-foreground flex items-center justify-between">
        <div>Prototype UI — Dette Technique • v0.1</div>
        <div className="flex items-center gap-2"><span className="hidden sm:inline">Fait pour démo</span> <Activity className="h-3 w-3"/></div>
      </div>
    </div>
  );
}
