import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  AlertCircle,
  CheckCircle2,
  Globe,
  ShieldCheck,
  Wrench,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";

interface HealthData {
  status: string;
  version: string;
  mcp_connected: boolean;
}

interface ScraperStatus {
  status: string;
  is_running: boolean;
  issue: string;
  current_page: number;
  pages_captured: number;
}

interface ToolData {
  name: string;
  description: string;
}

export function Status() {
  const { data: health } = useQuery<HealthData>({
    queryKey: ["health"],
    queryFn: () => fetch("/api/health").then((res) => res.json()),
    refetchInterval: 10000,
  });

  const { data: scraper } = useQuery<ScraperStatus>({
    queryKey: ["scraper-status"],
    queryFn: () => fetch("/api/status").then((res) => res.json()),
    refetchInterval: 5000,
  });

  const { data: tools, isLoading: toolsLoading } = useQuery<ToolData[]>({
    queryKey: ["tools"],
    queryFn: () => fetch("/api/tools").then((res) => res.json()),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            System Status
          </h2>
          <p className="text-slate-400">Health monitoring and tool registry</p>
        </div>
        {health?.status === "healthy" ? (
          <Badge
            variant="outline"
            className="bg-emerald-500/10 text-emerald-500 border-emerald-500/20 gap-1 px-3 py-1"
          >
            <CheckCircle2 className="h-3.5 w-3.5" />
            System Healthy
          </Badge>
        ) : (
          <Badge
            variant="outline"
            className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20 gap-1 px-3 py-1"
          >
            <AlertCircle className="h-3.5 w-3.5" />
            Checking System...
          </Badge>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              API Bridge
            </CardTitle>
            <Globe className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {health
                ? health.status === "healthy"
                  ? "Online"
                  : "Degraded"
                : "Unknown"}
            </div>
            <p className="text-xs text-slate-400">
              Port 10863 {health ? `v${health.version}` : ""}
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              MCP Foundation
            </CardTitle>
            <ShieldCheck className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {health?.mcp_connected ? "Connected" : "Disconnected"}
            </div>
            <p className="text-xs text-slate-400">FastMCP Session</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Scraping Engine
            </CardTitle>
            <Activity className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {scraper?.is_running ? "Active" : "Idle"}
            </div>
            <p className="text-xs text-slate-400">
              {scraper?.is_running
                ? `Page ${scraper.current_page} · ${scraper.pages_captured} captured`
                : scraper?.status && scraper.status !== "Idle"
                  ? scraper.status
                  : "Worker idle"}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl">
        <CardHeader className="flex flex-row items-center gap-2">
          <Wrench className="h-5 w-5 text-blue-400" />
          <CardTitle className="text-white text-lg">Registered Tools</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[400px] pr-4">
            <div className="space-y-4">
              {toolsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Activity className="h-8 w-8 animate-spin text-slate-700" />
                </div>
              ) : tools?.length ? (
                tools.map((tool) => (
                  <div
                    key={tool.name}
                    className="flex flex-col space-y-1 p-3 rounded-lg border border-slate-800 bg-slate-900/30 hover:bg-slate-900/50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-semibold text-blue-400">
                        {tool.name}
                      </h4>
                      <Badge
                        variant="outline"
                        className="text-[10px] uppercase font-bold tracking-wider opacity-60"
                      >
                        Tool
                      </Badge>
                    </div>
                    <p className="text-sm text-slate-400 leading-relaxed">
                      {tool.description || "No description provided."}
                    </p>
                  </div>
                ))
              ) : (
                <div className="flex items-center justify-center py-8 text-slate-500">
                  No tools found — backend may be unreachable.
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
