import { useQuery } from "@tanstack/react-query";
import { Bot, Cpu, Download, Eraser, Loader2, Send, User } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import API_BASE from "@/lib/api";

const HISTORY_KEY = "readly-chat-history";
const PERSONALITY_KEY = "readly-chat-personality";
const MAX_HISTORY = 100;

const PERSONALITIES: Record<string, string> = {
  "Magazine Editor":
    "You are a magazine content editor. Help with magazine discovery, article curation, and reading list management. Provide insights on magazine categories and issues.",
  "Content Curator":
    "You are a content curation specialist. Focus on finding relevant articles, organizing reading lists, and discovering new content across Readly's magazine catalog.",
  "Quick Summarizer": "Keep responses to 2-3 sentences. Focus on key facts.",
  Custom: "Custom prompt \u2014 editable below.",
};

const EXAMPLE_PROMPTS = [
  {
    group: "Magazines",
    prompts: [
      "Browse latest magazines",
      "Search for technology magazines",
      "Show magazine categories",
    ],
  },
  {
    group: "Articles",
    prompts: [
      "Find articles about AI",
      "Show recent issues",
      "Search by topic",
    ],
  },
  {
    group: "Reading",
    prompts: [
      "Continue reading last issue",
      "Show my reading history",
      "Recommend magazines",
    ],
  },
];

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
  const [personality, setPersonality] = useState(
    () => localStorage.getItem(PERSONALITY_KEY) || "Magazine Editor",
  );
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    try {
      return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
    } catch {
      return [];
    }
  });
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const { data: llmStatus } = useQuery<LlmStatus>({
    queryKey: ["llm-status"],
    queryFn: () => fetch(`${API_BASE}/api/llm/status`).then((r) => r.json()),
    refetchInterval: 30000,
  });

  useEffect(() => {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(messages));
  }, [messages]);
  useEffect(() => {
    localStorage.setItem(PERSONALITY_KEY, personality);
  }, [personality]);
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          role: "assistant",
          content:
            "LLM command interface ready. Ask me to scrape a magazine, search your library, or check system status.",
        },
      ]);
    }
  }, [messages.length]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleSend = useCallback(async () => {
    const text = input.trim();
    if (!text || sending) return;
    setInput("");
    const userMsg: ChatMessage = { role: "user", content: text };
    setMessages((prev) => {
      const next = [...prev, userMsg];
      return next.length > MAX_HISTORY ? next.slice(-MAX_HISTORY) : next;
    });
    setSending(true);
    try {
      const resp = await fetch(`${API_BASE}/api/llm/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          provider: localStorage.getItem("readly-llm-provider") || "ollama",
          model: localStorage.getItem("readly-llm-model") || "qwen3.5:27b",
          base_url:
            localStorage.getItem("readly-llm-url") || "http://localhost:11434",
          api_key: localStorage.getItem("readly-llm-key") || "",
          personality,
        }),
      });
      const data = await resp.json();
      if (data.ok) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.response },
        ]);
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
  }, [input, sending, personality]);

  const exportChat = () => {
    const text = messages
      .map((m) => `[${m.role.toUpperCase()}] ${m.content}`)
      .join("\n\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "readly-chat.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div
      data-testid="chat-page"
      className="flex h-[calc(100vh-8rem)] flex-col space-y-4"
    >
      <div
        data-testid="chat-controls"
        className="flex items-center justify-between flex-wrap gap-2"
      >
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Command Interface
          </h2>
          <p className="text-slate-400">
            Natural language tool orchestration via LLM
          </p>
        </div>
        <div className="flex items-center gap-2">
          {llmStatus && (
            <div className="flex items-center gap-2 text-xs mr-2">
              <Cpu
                className={`h-3.5 w-3.5 ${llmStatus.ok ? "text-emerald-400" : "text-red-400"}`}
              />
              <span
                className={llmStatus.ok ? "text-emerald-400" : "text-red-400"}
              >
                {llmStatus.ok
                  ? `${llmStatus.provider} \u00b7 ${llmStatus.model || "no model"}`
                  : `${llmStatus.provider}: offline`}
              </span>
            </div>
          )}
          <span className="text-xs text-slate-500 bg-slate-800 px-2 py-1 rounded">
            skill:readly-expert
          </span>
          <select
            data-testid="personality-select"
            className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200"
            value={personality}
            onChange={(e) => setPersonality(e.target.value)}
          >
            {Object.keys(PERSONALITIES).map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
          <button
            data-testid="chat-export"
            onClick={exportChat}
            disabled={messages.length === 0}
            className="p-1.5 rounded hover:bg-slate-800 text-slate-400 disabled:opacity-30"
            title="Export"
          >
            <Download className="h-4 w-4" />
          </button>
          <button
            data-testid="chat-clear"
            onClick={clearChat}
            disabled={messages.length === 0}
            className="p-1.5 rounded hover:bg-slate-800 text-slate-400 disabled:opacity-30"
            title="Clear"
          >
            <Eraser className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div
        data-testid="chat-messages"
        className="flex-1 overflow-y-auto space-y-4"
      >
        {messages.map((msg, i) => (
          <div key={i} className="flex gap-3">
            <div
              className={`h-8 w-8 rounded-full flex items-center justify-center border ${msg.role === "user" ? "bg-slate-800 border-slate-700" : "bg-blue-900/20 border-blue-800"}`}
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
                  className={`text-sm font-medium ${msg.role === "user" ? "text-slate-200" : "text-blue-400"}`}
                >
                  {msg.role === "user" ? "You" : "Assistant"}
                </span>
              </div>
              <div
                className={`text-sm p-3 rounded-md border inline-block max-w-[90%] whitespace-pre-wrap ${msg.role === "user" ? "text-slate-300 bg-slate-900/50 border-slate-800" : "text-slate-300 bg-blue-950/10 border-blue-900/30"}`}
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
        <div ref={scrollRef} />
      </div>

      <div data-testid="example-prompts" className="flex flex-wrap gap-2">
        {EXAMPLE_PROMPTS.map((group) => (
          <div key={group.group} className="flex flex-wrap items-center gap-1">
            <span className="text-xs text-slate-500 mr-1">{group.group}:</span>
            {group.prompts.map((p) => (
              <button
                key={p}
                onClick={() => setInput(p)}
                className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-1 rounded"
              >
                {p}
              </button>
            ))}
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          data-testid="chat-input"
          className="flex-1 bg-slate-950 border border-slate-800 rounded-md px-4 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
          placeholder={
            llmStatus?.ok
              ? "Ask something..."
              : "LLM offline \u2014 configure in Settings"
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
        <button
          data-testid="chat-send"
          onClick={handleSend}
          disabled={sending || !input.trim()}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-md"
        >
          {sending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </button>
      </div>
    </div>
  );
}
