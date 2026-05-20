import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  BookOpen,
  RefreshCw,
  ExternalLink,
  Loader2,
  Search,
  LibraryBig,
} from "lucide-react";

interface Magazine {
  title: string;
  url: string;
  cover_url: string;
  type: string;
}

interface LibraryData {
  magazines: Magazine[];
  count: number;
  page_url: string;
}

export function Library() {
  const [filter, setFilter] = useState("");

  const { data, isLoading, isError, refetch, isRefetching } =
    useQuery<LibraryData>({
      queryKey: ["library"],
      queryFn: () =>
        fetch("/api/library").then((res) => {
          if (!res.ok) throw new Error("Backend unreachable");
          return res.json();
        }),
      retry: 1,
      staleTime: 30000,
    });

  const magazines = data?.magazines || [];
  const filtered = filter
    ? magazines.filter((m) =>
        m.title.toLowerCase().includes(filter.toLowerCase())
      )
    : magazines;
  const grouped = groupBy(filtered, "type");

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            My Library
          </h2>
          <p className="text-slate-400">
            {data
              ? `${data.count} magazines available`
              : "Your Readly magazine collection"}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            <Input
              className="bg-slate-900 border-slate-800 text-slate-100 pl-9 w-60"
              placeholder="Filter magazines..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            />
          </div>
          <Button
            variant="outline"
            className="border-slate-800 text-slate-300 hover:bg-slate-800"
            onClick={() => refetch()}
            disabled={isRefetching}
          >
            <RefreshCw
              className={`h-4 w-4 mr-1 ${isRefetching ? "animate-spin" : ""}`}
            />
            Refresh
          </Button>
        </div>
      </div>

      {isLoading ? (
        <Card className="border-slate-800 bg-slate-950/50">
          <CardContent className="flex items-center justify-center py-20">
            <div className="text-center space-y-3">
              <Loader2 className="h-8 w-8 animate-spin text-blue-400 mx-auto" />
              <p className="text-slate-400 text-sm">
                Opening browser and scanning your library...
              </p>
            </div>
          </CardContent>
        </Card>
      ) : isError ? (
        <Card className="border-slate-800 bg-slate-950/50">
          <CardContent className="flex items-center justify-center py-16">
            <div className="text-center space-y-3 max-w-md">
              <LibraryBig className="h-10 w-10 text-slate-600 mx-auto" />
              <p className="text-slate-400 text-sm">
                Could not load your library. Make sure:
              </p>
              <ul className="text-xs text-slate-500 text-left space-y-1">
                <li>
                  1. The backend is running:{" "}
                  <code className="text-blue-400">readly-mcp --web</code>
                </li>
                <li>
                  2. The browser auto-login works (READLY_AUTH_TOKEN set in
                  Settings)
                </li>
                <li>
                  3. The Vite proxy is configured (port 10706 → port 10863)
                </li>
              </ul>
              <Button
                variant="outline"
                className="mt-2"
                onClick={() => refetch()}
              >
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : magazines.length === 0 ? (
        <Card className="border-slate-800 bg-slate-950/50">
          <CardContent className="flex items-center justify-center py-16">
            <div className="text-center space-y-3">
              <BookOpen className="h-10 w-10 text-slate-600 mx-auto" />
              <p className="text-slate-400 text-sm">
                No magazines found in your library.
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-8">
          {Object.entries(grouped).map(([type, items]) => (
            <section key={type}>
              <div className="flex items-center gap-2 mb-4">
                <h3 className="text-lg font-semibold text-slate-200 capitalize">
                  {type}s
                </h3>
                <Badge
                  variant="outline"
                  className="bg-slate-800 text-slate-400 border-slate-700"
                >
                  {items.length}
                </Badge>
              </div>
              <div className="grid gap-4 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
                {items.map((mag) => (
                  <a
                    key={mag.title}
                    href={mag.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group cursor-pointer"
                  >
                    <Card className="border-slate-800 bg-slate-950/50 hover:bg-slate-900/70 transition-all hover:border-slate-700 overflow-hidden">
                      <div className="aspect-[3/4] bg-slate-900 relative overflow-hidden">
                        {mag.cover_url ? (
                          <img
                            src={mag.cover_url}
                            alt={mag.title}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                            loading="lazy"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <BookOpen className="h-12 w-12 text-slate-700" />
                          </div>
                        )}
                        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                        <div className="absolute bottom-0 left-0 right-0 p-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <ExternalLink className="h-4 w-4 text-white ml-auto" />
                        </div>
                      </div>
                      <CardContent className="p-2.5">
                        <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                          {mag.title}
                        </p>
                        <p className="text-[10px] text-slate-600 mt-1 uppercase tracking-wider">
                          {mag.type}
                        </p>
                      </CardContent>
                    </Card>
                  </a>
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}

function groupBy<T extends Record<string, unknown>>(
  items: T[],
  key: keyof T
): Record<string, T[]> {
  return items.reduce(
    (acc, item) => {
      const k = String(item[key] || "unknown");
      if (!acc[k]) acc[k] = [];
      acc[k].push(item);
      return acc;
    },
    {} as Record<string, T[]>
  );
}
