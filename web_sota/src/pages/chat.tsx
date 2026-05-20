import { useQuery } from "@tanstack/react-query";
import { Bot, Send, User, Cpu, Loader2, AlertCircle } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

interface LlmStatus {
  provider: string;
  ok: boolean;
  model: string | null;
  error?: string | null;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "LLM command interface ready. Ask me to scrape a magazine, search your library, or check system status.",
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const { data: llmStatus } = useQuery<LlmStatus>({
    queryKey: ["llm-status"],
    queryFn: () => fetch("/api/llm/status").then((r) => r.json()),
    refetchInterval: 30000,
  });

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || sending) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setSending(true);

    try {
      const resp = await fetch("/api/llm/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          provider: localStorage.getItem("readly-llm-provider") || "ollama",
          model: localStorage.getItem("readly-llm-model") || "qwen3.5:27b",
          base_url: localStorage.getItem("readly-llm-url") || "http://localhost:11434",
          api_key: localStorage.getItem("readly-llm-key") || "",
        }),
      });
      const data = await resp.json();

      if (data.ok) {
        setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `**Error:** ${data.error || "LLM request failed"}\n\nCheck your LLM settings (Settings > LLM Provider) and make sure your provider is running.`,
          },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `**Connection error:** ${err instanceof Error ? err.message : "Unknown error"}\n\nMake sure the backend is running and your LLM provider is reachable.`,
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Command Interface
          </h2>
          <p className="text-slate-400">
            Natural language tool orchestration via LLM
          </p>
        </div>
        {llmStatus && (
          <div className="flex items-center gap-2 text-xs">
            <Cpu className={`h-3.5 w-3.5 ${llmStatus.ok ? "text-emerald-400" : "text-red-400"}`} />
            <span className={llmStatus.ok ? "text-emerald-400" : "text-red-400"}>
              {llmStatus.ok
                ? `${llmStatus.provider} · ${llmStatus.model || "no model"}`
                : `${llmStatus.provider}: offline`}
            </span>
          </div>
        )}
      </div>

      <Card className="flex-1 border-slate-800 bg-slate-950/50 flex flex-col overflow-hidden">
        <CardContent
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-4 space-y-4"
        >
          {messages.map((msg, i) => (
            <div key={i} className="flex gap-3">
              <div
                className={`h-8 w-8 rounded-full flex items-center justify-center border ${
                  msg.role === "user"
                    ? "bg-slate-800 border-slate-700"
                    : "bg-blue-900/20 border-blue-800"
                }`}
              >
                {msg.role === "user" ? (
                  <User className="h-4 w-4 text-slate-400" />
                ) : (
                  <Bot className="h-4 w-4 text-blue-400" />
                )}
              </div>
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2">
                  <span
                    className={`text-sm font-medium ${
                      msg.role === "user" ? "text-slate-200" : "text-blue-400"
                    }`}
                  >
                    {msg.role === "user" ? "You" : "Assistant"}
                  </span>
                </div>
                <div
                  className={`text-sm p-3 rounded-md border inline-block max-w-[90%] whitespace-pre-wrap ${
                    msg.role === "user"
                      ? "text-slate-300 bg-slate-900/50 border-slate-800"
                      : "text-slate-300 bg-blue-950/10 border-blue-900/30"
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            </div>
          ))}
          {sending && (
            <div className="flex gap-3">
              <div className="h-8 w-8 rounded-full bg-blue-900/20 flex items-center justify-center border border-blue-800">
                <Bot className="h-4 w-4 text-blue-400" />
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <Loader2 className="h-4 w-4 animate-spin" />
                Thinking...
              </div>
            </div>
          )}
        </CardContent>
        <div className="p-4 border-t border-slate-800 bg-slate-900/30">
          <div className="flex gap-2">
            <input
              className="flex-1 bg-slate-950 border border-slate-800 rounded-md px-4 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
              placeholder={
                llmStatus?.ok
                  ? "Ask something..."
                  : "LLM offline — configure in Settings"
              }
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              disabled={sending}
            />
            <Button
              size="icon"
              className="bg-blue-600 hover:bg-blue-700"
              onClick={handleSend}
              disabled={sending || !input.trim()}
            >
              {sending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
