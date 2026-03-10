import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Book, Code, Terminal, Info } from "lucide-react";

export function Help() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Documentation & Help</h2>
                    <p className="text-slate-400">Guide to using Readly MCP and its capabilities</p>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl">
                    <CardHeader className="flex flex-row items-center gap-2">
                        <Book className="h-5 w-5 text-blue-400" />
                        <CardTitle className="text-white">Quick Start</CardTitle>
                    </CardHeader>
                    <CardContent className="text-slate-400 space-y-4 text-sm">
                        <p>
                            Readly MCP is designed to capture and archive magazine content for personal digital libraries.
                            It uses a headless browser to navigate content and compiles high-quality PDFs.
                        </p>
                        <div className="space-y-2">
                            <div className="flex gap-2">
                                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-800 text-xs font-bold text-white">1</span>
                                <span>Navigate to the Readly website using the AI command.</span>
                            </div>
                            <div className="flex gap-2">
                                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-800 text-xs font-bold text-white">2</span>
                                <span>Open the magazine you wish to archive.</span>
                            </div>
                            <div className="flex gap-2">
                                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-800 text-xs font-bold text-white">3</span>
                                <span>Run the `scrape_magazine` tool with your desired parameters.</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl">
                    <CardHeader className="flex flex-row items-center gap-2">
                        <Terminal className="h-5 w-5 text-emerald-400" />
                        <CardTitle className="text-white">API Usage</CardTitle>
                    </CardHeader>
                    <CardContent className="text-slate-400 space-y-4 text-sm">
                        <p>
                            The backend exposes a REST API on port 10863. You can interact with it directly if needed:
                        </p>
                        <div className="bg-slate-900 rounded p-3 font-mono text-[10px] overflow-x-auto border border-slate-800">
                            <p className="text-emerald-400">GET /api/status</p>
                            <p className="text-slate-500 mb-2">Check health and version</p>
                            <p className="text-emerald-400">GET /api/tools</p>
                            <p className="text-slate-500 mb-2">List discovery results</p>
                            <p className="text-emerald-400">POST /api/scrape/start</p>
                            <p className="text-slate-500">Initiate a scraping job</p>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl">
                    <CardHeader className="flex flex-row items-center gap-2">
                        <Code className="h-5 w-5 text-purple-400" />
                        <CardTitle className="text-white">Advanced Configuration</CardTitle>
                    </CardHeader>
                    <CardContent className="text-slate-400 space-y-4 text-sm">
                        <p>
                            Custom timing and page limits can be set in the Settings page or passed directly to the tool calls.
                        </p>
                        <ul className="list-disc list-inside space-y-1">
                            <li>Interval: Milliseconds between page turns</li>
                            <li>Max Pages: Safety limit for capture</li>
                            <li>Concurrency: Handled via worker lock</li>
                        </ul>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl">
                    <CardHeader className="flex flex-row items-center gap-2">
                        <Info className="h-5 w-5 text-orange-400" />
                        <CardTitle className="text-white">Troubleshooting</CardTitle>
                    </CardHeader>
                    <CardContent className="text-slate-400 space-y-4 text-sm">
                        <p>
                            If scraping fails, check the following:
                        </p>
                        <ul className="list-disc list-inside space-y-1">
                            <li>Browser visible/headless mode settings</li>
                            <li>Internet connectivity to the source host</li>
                            <li>Port conflicts on 10862/10863</li>
                        </ul>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
