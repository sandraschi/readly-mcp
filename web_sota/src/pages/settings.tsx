import { useQuery } from "@tanstack/react-query";
import {
  CheckCircle2,
  Cpu,
  Loader2,
  Save,
  XCircle,
} from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface LlmModels {
  ok: boolean;
  provider: string;
  models: string[];
  error?: string;
}

export function Settings() {
  const [backendUrl, setBackendUrl] = useState("http://localhost:10863");
  const [testStatus, setTestStatus] = useState<"idle" | "testing" | "ok" | "fail">("idle");
  const [scrapeInterval, setScrapeInterval] = useState("120");
  const [maxPages, setMaxPages] = useState("200");
  const [saved, setSaved] = useState(false);
  const [authToken, setAuthToken] = useState(() =>
    localStorage.getItem("readly-auth-token") || ""
  );
  const [tokenSent, setTokenSent] = useState(false);

  const [llmProvider, setLlmProvider] = useState(() =>
    localStorage.getItem("readly-llm-provider") || "ollama"
  );
  const [llmModel, setLlmModel] = useState(() =>
    localStorage.getItem("readly-llm-model") || "qwen3.5:27b"
  );
  const [llmUrl, setLlmUrl] = useState(() =>
    localStorage.getItem("readly-llm-url") || "http://localhost:11434"
  );
  const [llmKey, setLlmKey] = useState(() =>
    localStorage.getItem("readly-llm-key") || ""
  );
  const [llmSaved, setLlmSaved] = useState(false);

  const { data: ollamaModels } = useQuery<LlmModels>({
    queryKey: ["ollama-models"],
    queryFn: () => fetch("/api/llm/models?provider=ollama").then((r) => r.json()),
    enabled: llmProvider === "ollama",
    refetchInterval: 60000,
  });

  const { data: lmstudioModels } = useQuery<LlmModels>({
    queryKey: ["lmstudio-models"],
    queryFn: () => fetch("/api/llm/models?provider=lmstudio").then((r) => r.json()),
    enabled: llmProvider === "lmstudio",
    refetchInterval: 60000,
  });

  const handleTest = async () => {
    setTestStatus("testing");
    try {
      const resp = await fetch(`${backendUrl}/api/health`, {
        signal: AbortSignal.timeout(5000),
      });
      setTestStatus(resp.ok ? "ok" : "fail");
    } catch {
      setTestStatus("fail");
    }
  };

  const handleSendToken = async () => {
    try {
      await fetch(`${backendUrl}/api/settings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ auth_token: authToken }),
      });
      localStorage.setItem("readly-auth-token", authToken);
      setTokenSent(true);
      setTimeout(() => setTokenSent(false), 3000);
    } catch {
      // ignore
    }
  };

  const handleSave = () => {
    localStorage.setItem("readly-backend-url", backendUrl);
    localStorage.setItem("readly-scrape-interval", scrapeInterval);
    localStorage.setItem("readly-max-pages", maxPages);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleSaveLlm = async () => {
    localStorage.setItem("readly-llm-provider", llmProvider);
    localStorage.setItem("readly-llm-model", llmModel);
    localStorage.setItem("readly-llm-url", llmUrl);
    localStorage.setItem("readly-llm-key", llmKey);

    const body: Record<string, string> = { provider: llmProvider };
    if (llmProvider === "ollama") {
      body.ollama_url = llmUrl;
      body.ollama_model = llmModel;
    } else if (llmProvider === "lmstudio") {
      body.lmstudio_url = llmUrl;
      body.lmstudio_model = llmModel;
    } else if (llmProvider === "openai") {
      body.local_llm_url = llmUrl;
      body.local_llm_model = llmModel;
      body.local_llm_key = llmKey;
    }

    try {
      await fetch("/api/settings/llm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
    } catch {
      // backend may be unreachable; still saved locally
    }

    setLlmSaved(true);
    setTimeout(() => setLlmSaved(false), 2000);
  };

  const availableModels = llmProvider === "ollama"
    ? ollamaModels?.models || []
    : llmProvider === "lmstudio"
      ? lmstudioModels?.models || []
      : [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">
          Configuration
        </h2>
        <p className="text-slate-400">
          Manage connections, LLM provider, and scraping preferences
        </p>
      </div>

      <div className="grid gap-6">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Backend Connection</CardTitle>
            <CardDescription className="text-slate-400">
              URL of the readly-mcp REST API backend (default: port 10863)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-2">
              <Label className="text-slate-300">API Backend URL</Label>
              <Input
                className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
                value={backendUrl}
                onChange={(e) => setBackendUrl(e.target.value)}
                placeholder="http://localhost:10863"
              />
            </div>
            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                className="border-slate-800 text-emerald-400 hover:bg-slate-800 hover:text-emerald-300"
                onClick={handleTest}
                disabled={testStatus === "testing"}
              >
                {testStatus === "testing" ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-1" />
                ) : null}
                Test Connectivity
              </Button>
              {testStatus === "ok" ? (
                <span className="flex items-center gap-1 text-xs text-emerald-400">
                  <CheckCircle2 className="h-3 w-3" /> Connected
                </span>
              ) : testStatus === "fail" ? (
                <span className="flex items-center gap-1 text-xs text-red-400">
                  <XCircle className="h-3 w-3" /> Failed
                </span>
              ) : null}
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Auto-Login Token</CardTitle>
            <CardDescription className="text-slate-400">
              Paste your Readly auth token (readlyAuth JWT) to skip manual login
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-2">
              <Label className="text-slate-300">readlyAuth Token</Label>
              <Input
                className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400 font-mono text-xs"
                value={authToken}
                onChange={(e) => setAuthToken(e.target.value)}
                placeholder="eyJhbGciOiJSUzI1..."
              />
            </div>
            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                className="border-slate-800 text-blue-400 hover:bg-slate-800 hover:text-blue-300"
                onClick={handleSendToken}
                disabled={!authToken}
              >
                Send Token to Backend
              </Button>
              {tokenSent ? (
                <span className="flex items-center gap-1 text-xs text-emerald-400">
                  <CheckCircle2 className="h-3 w-3" /> Token set for session
                </span>
              ) : null}
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Scraping Defaults</CardTitle>
            <CardDescription className="text-slate-400">
              Default parameters for the smart_scrape tool
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label className="text-slate-300">Interval (seconds)</Label>
                <Input
                  className="bg-slate-900 border-slate-800 text-slate-100"
                  value={scrapeInterval}
                  onChange={(e) => setScrapeInterval(e.target.value)}
                  type="number"
                  min={10}
                />
                <p className="text-xs text-slate-500">Seconds between page turns</p>
              </div>
              <div className="grid gap-2">
                <Label className="text-slate-300">Max Pages</Label>
                <Input
                  className="bg-slate-900 border-slate-800 text-slate-100"
                  value={maxPages}
                  onChange={(e) => setMaxPages(e.target.value)}
                  type="number"
                  min={1}
                />
                <p className="text-xs text-slate-500">Safety limit per issue</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">
              <div className="flex items-center gap-2">
                <Cpu className="h-5 w-5 text-blue-400" />
                LLM Provider
              </div>
            </CardTitle>
            <CardDescription className="text-slate-400">
              Configure local LLM for the command interface and article extraction
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-2">
              <Label className="text-slate-300">Provider</Label>
              <select
                className="bg-slate-900 border border-slate-800 text-slate-100 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                value={llmProvider}
                onChange={(e) => setLlmProvider(e.target.value)}
              >
                <option value="ollama">Ollama (Local)</option>
                <option value="lmstudio">LM Studio (Local)</option>
                <option value="openai">OpenAI Compatible</option>
              </select>
            </div>
            <div className="grid gap-2">
              <Label className="text-slate-300">Base URL</Label>
              <Input
                className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
                value={llmUrl}
                onChange={(e) => setLlmUrl(e.target.value)}
                placeholder="http://localhost:11434"
              />
            </div>
            <div className="grid gap-2">
              <Label className="text-slate-300">Model</Label>
              <div className="flex gap-2">
                <Input
                  className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
                  value={llmModel}
                  onChange={(e) => setLlmModel(e.target.value)}
                  placeholder="qwen3.5:27b"
                  list="llm-model-suggestions"
                />
                <datalist id="llm-model-suggestions">
                  {availableModels.map((m) => (
                    <option key={m} value={m} />
                  ))}
                </datalist>
              </div>
              {availableModels.length > 0 && (
                <p className="text-xs text-slate-500">
                  Detected models: {availableModels.slice(0, 6).join(", ")}
                  {availableModels.length > 6 ? ` +${availableModels.length - 6} more` : ""}
                </p>
              )}
            </div>
            {llmProvider === "openai" && (
              <div className="grid gap-2">
                <Label className="text-slate-300">API Key</Label>
                <Input
                  className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
                  value={llmKey}
                  onChange={(e) => setLlmKey(e.target.value)}
                  placeholder="sk-..."
                  type="password"
                />
              </div>
            )}
            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                className="border-slate-800 text-blue-400 hover:bg-slate-800 hover:text-blue-300"
                onClick={handleSaveLlm}
              >
                {llmSaved ? (
                  <CheckCircle2 className="h-4 w-4 mr-1" />
                ) : (
                  <Save className="h-4 w-4 mr-1" />
                )}
                {llmSaved ? "Saved" : "Save LLM Settings"}
              </Button>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <Button
            className="bg-emerald-600 hover:bg-emerald-700 text-white"
            onClick={handleSave}
          >
            {saved ? (
              <CheckCircle2 className="h-4 w-4 mr-1" />
            ) : (
              <Save className="h-4 w-4 mr-1" />
            )}
            {saved ? "Saved" : "Save Settings"}
          </Button>
        </div>
      </div>
    </div>
  );
}
