import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ExternalLink, Box, Database, Network } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function Apps() {
    // Mock fleet data - usually this would come from a glama-aware registry
    const apps = [
        { name: "Obsidian MCP", port: 10750, color: "text-purple-500", status: "Active" },
        { name: "Devices MCP", port: 10760, color: "text-emerald-500", status: "Active" },
        { name: "System Admin", port: 10810, color: "text-blue-500", status: "Active" },
        { name: "Readly MCP", port: 10862, color: "text-orange-500", status: "Current" },
        { name: "OCR Pipeline", port: 10820, color: "text-cyan-500", status: "Inactive" },
    ];

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">SOTA Fleet Hub</h2>
                    <p className="text-slate-400">Network overview of all active MCP server interfaces</p>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {apps.map((app) => (
                    <Card key={app.name} className="border-slate-800 bg-slate-950/50 hover:bg-slate-900/50 transition-all cursor-pointer group">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium text-slate-200">
                                {app.name}
                            </CardTitle>
                            <Box className={`h-4 w-4 ${app.color}`} />
                        </CardHeader>
                        <CardContent>
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-xs text-slate-500 mb-1">LOCAL PORT</p>
                                    <div className="text-xl font-bold text-white font-mono">{app.port}</div>
                                </div>
                                <div className="text-right">
                                    <Badge variant="outline" className={app.status === "Active" ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20" : app.status === "Current" ? "bg-blue-500/10 text-blue-500 border-blue-500/20" : "bg-slate-800 text-slate-500"}>
                                        {app.status}
                                    </Badge>
                                </div>
                            </div>
                            <div className="mt-4 flex items-center justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                                <span className="text-xs text-blue-400 flex items-center gap-1">
                                    Launch Interface <ExternalLink className="h-3 w-3" />
                                </span>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white">Registry Infrastructure</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="flex items-center gap-4 text-sm text-slate-400">
                        <div className="flex items-center gap-2">
                            <Database className="h-4 w-4 text-slate-500" />
                            <span>Central Registry: Connected</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <Network className="h-4 w-4 text-slate-500" />
                            <span>Mesh Network: Active</span>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
