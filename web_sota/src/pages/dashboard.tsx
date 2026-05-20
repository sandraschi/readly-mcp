import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  AlertCircle,
  CheckCircle2,
  Cpu,
  HardDrive,
  Network,
  Shield,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

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

interface LlmStatus {
  provider: string;
  ok: boolean;
  error: string | null;
  model: string | null;
  available_models?: string[];
}

export function Dashboard() {
  const { data: health } = useQuery<HealthData>({
    queryKey: ["health"],
    queryFn: () => fetch("/api/health").then((r) => r.json()),
    refetchInterval: 15000,
  });

  const { data: scraper } = useQuery<ScraperStatus>({
    queryKey: ["scraper-status"],
    queryFn: () => fetch("/api/status").then((r) => r.json()),
    refetchInterval: 10000,
  });

  const { data: llm } = useQuery<LlmStatus>({
    queryKey: ["llm-status"],
    queryFn: () => fetch("/api/llm/status").then((r) => r.json()),
    refetchInterval: 30000,
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Readly MCP Dashboard
          </h2>
          <p className="text-slate-400">System overview and status</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Service Status
            </CardTitle>
            <Shield className={health?.status === "healthy" ? "h-4 w-4 text-emerald-500" : "h-4 w-4 text-yellow-500"} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {health ? (health.status === "healthy" ? "Online" : "Degraded") : "Checking..."}
            </div>
            <p className="text-xs text-slate-400">
              {health ? `v${health.version} · MCP ${health.mcp_connected ? "connected" : "disconnected"}` : "Connecting..."}
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Scraping Engine
            </CardTitle>
            <Activity className={scraper?.is_running ? "h-4 w-4 text-orange-500" : "h-4 w-4 text-slate-500"} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {scraper?.is_running ? "Active" : (scraper ? "Idle" : "...")}
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

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              LLM Provider
            </CardTitle>
            <Cpu className={llm?.ok ? "h-4 w-4 text-blue-500" : "h-4 w-4 text-slate-500"} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {llm ? (llm.ok ? llm.provider : "Unreachable") : "..."}
            </div>
            <p className="text-xs text-slate-400">
              {llm?.ok
                ? `Model: ${llm.model || "none"}`
                : llm?.error
                  ? llm.error
                  : "Not configured"}
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              API Bridge
            </CardTitle>
            <Network className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">Connected</div>
            <p className="text-xs text-slate-400">FastMCP bridge active</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4 border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Recent Logs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[200px] font-mono text-xs p-4 overflow-y-auto border border-slate-800 rounded-md bg-slate-900/50 text-slate-400 space-y-1">
              {health && <p className={health.status === "healthy" ? "text-emerald-400" : "text-yellow-400"}>[system] API: {health.status} (v{health.version})</p>}
              {scraper && <p className={scraper.is_running ? "text-orange-400" : "text-slate-500"}>[scraper] Status: {scraper.status} · Pages: {scraper.pages_captured}</p>}
              {llm && <p className={llm.ok ? "text-blue-400" : "text-red-400"}>[llm] {llm.provider}: {llm.ok ? `Online (${llm.model || "no model"})` : `Offline — ${llm.error || "not configured"}`}</p>}
              <div className="animate-pulse inline-block h-2 w-1 bg-slate-500 ml-1" />
            </div>
          </CardContent>
        </Card>
        <Card className="col-span-3 border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center">
                <HardDrive className="h-4 w-4 text-slate-400 mr-2" />
                <div className="ml-2 space-y-1">
                  <p className="text-sm font-medium leading-none text-white">
                    Local Storage
                  </p>
                  <p className="text-xs text-slate-400">Access verified</p>
                </div>
              </div>
              <div className="flex items-center">
                <Activity className="h-4 w-4 text-emerald-500 mr-2" />
                <div className="ml-2 space-y-1">
                  <p className="text-sm font-medium leading-none text-white">
                    Heartbeat
                  </p>
                  <p className="text-xs text-slate-400">
                    {health ? "Nominal ping tracking" : "Waiting for connection..."}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
