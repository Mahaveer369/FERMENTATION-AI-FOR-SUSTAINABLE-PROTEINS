"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
    Beaker, Plus, History, Settings, LogOut, Leaf,
    Zap, TrendingUp, FlaskConical, ChevronRight, Activity
} from "lucide-react";
import { experiments, ai } from "@/lib/api";

interface User {
    id: number;
    email: string;
    full_name: string;
    role: string;
}

interface ExperimentSummary {
    experiment: {
        id: number;
        name: string;
        microbe_type: string;
        created_at: string;
        status: string;
    };
    result: {
        predicted_yield: number;
        sustainability_score: number;
    } | null;
}

export default function DashboardPage() {
    const router = useRouter();
    const [user, setUser] = useState<User | null>(null);
    const [recentExperiments, setRecentExperiments] = useState<ExperimentSummary[]>([]);
    const [loading, setLoading] = useState(true);
    const [tips, setTips] = useState<any[]>([]);

    useEffect(() => {
        // Check auth
        const token = localStorage.getItem("token");
        const userData = localStorage.getItem("user");

        if (!token || !userData) {
            router.push("/login");
            return;
        }

        setUser(JSON.parse(userData));
        loadData();
    }, [router]);

    const loadData = async () => {
        try {
            const [expData, tipsData] = await Promise.all([
                experiments.list(1, 5).catch(() => ({ experiments: [] })),
                ai.getSustainabilityTips().catch(() => ({ tips: [] })),
            ]);

            setRecentExperiments(expData.experiments || []);
            setTips(tipsData.tips || []);
        } catch (err) {
            console.error("Failed to load data:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        router.push("/");
    };

    if (!user) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin text-4xl">⏳</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex">
            {/* Sidebar */}
            <aside className="w-64 glass min-h-screen p-6 flex flex-col">
                <div className="flex items-center gap-2 mb-8">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                        <Beaker className="w-6 h-6 text-white" />
                    </div>
                    <span className="font-bold">FermaGen AI</span>
                </div>

                <nav className="flex-1 space-y-2">
                    <Link href="/dashboard" className="flex items-center gap-3 px-4 py-3 rounded-lg bg-white/5 text-white">
                        <TrendingUp className="w-5 h-5" />
                        Dashboard
                    </Link>
                    <Link href="/experiment" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition">
                        <Plus className="w-5 h-5" />
                        New Experiment
                    </Link>
                    <Link href="/history" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition">
                        <History className="w-5 h-5" />
                        History
                    </Link>
                    <Link href="/protein" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition">
                        <FlaskConical className="w-5 h-5" />
                        Protein Analysis
                    </Link>
                    <Link href="/realtime" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition group border border-transparent hover:border-green-500/30">
                        <Activity className="w-5 h-5 group-hover:text-green-400" />
                        Real-Time API
                    </Link>
                </nav>

                <div className="pt-6 border-t border-white/10">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-blue-500 flex items-center justify-center font-bold">
                            {user.full_name.charAt(0)}
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="font-medium truncate">{user.full_name}</div>
                            <div className="text-xs text-gray-500 capitalize">{user.role}</div>
                        </div>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-2 text-gray-400 hover:text-red-400 transition text-sm"
                    >
                        <LogOut className="w-4 h-4" />
                        Sign Out
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 p-8">
                <div className="max-w-6xl mx-auto">
                    {/* Header */}
                    <div className="mb-8">
                        <h1 className="text-3xl font-bold mb-2">Welcome back, {user.full_name.split(" ")[0]}!</h1>
                        <p className="text-gray-400">Here&apos;s an overview of your fermentation research</p>
                    </div>

                    {/* Quick Actions */}
                    <div className="grid md:grid-cols-3 gap-6 mb-8">
                        <Link href="/experiment" className="card group cursor-pointer">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <Plus className="w-6 h-6 text-white" />
                            </div>
                            <h3 className="font-semibold mb-1">New Experiment</h3>
                            <p className="text-sm text-gray-400">Run a fermentation simulation</p>
                        </Link>

                        <Link href="/optimize" className="card group cursor-pointer">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <Zap className="w-6 h-6 text-white" />
                            </div>
                            <h3 className="font-semibold mb-1">Optimize</h3>
                            <p className="text-sm text-gray-400">AI-powered parameter optimization</p>
                        </Link>

                        <Link href="/protein" className="card group cursor-pointer">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <FlaskConical className="w-6 h-6 text-white" />
                            </div>
                            <h3 className="font-semibold mb-1">Protein Analysis</h3>
                            <p className="text-sm text-gray-400">Analyze protein sequences</p>
                        </Link>
                    </div>

                    <div className="grid lg:grid-cols-3 gap-8">
                        {/* Recent Experiments */}
                        <div className="lg:col-span-2">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-xl font-semibold">Recent Experiments</h2>
                                <Link href="/history" className="text-green-400 text-sm hover:underline">
                                    View all
                                </Link>
                            </div>

                            {loading ? (
                                <div className="card text-center py-12">
                                    <div className="animate-spin text-4xl mb-4">⏳</div>
                                    <p className="text-gray-400">Loading experiments...</p>
                                </div>
                            ) : recentExperiments.length === 0 ? (
                                <div className="card text-center py-12">
                                    <Beaker className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                                    <h3 className="font-semibold mb-2">No experiments yet</h3>
                                    <p className="text-gray-400 mb-4">Start your first simulation to see results here</p>
                                    <Link href="/experiment" className="btn-primary inline-flex items-center gap-2">
                                        <Plus className="w-4 h-4" /> New Experiment
                                    </Link>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {recentExperiments.map((item) => (
                                        <Link
                                            key={item.experiment.id}
                                            href={`/results?id=${item.experiment.id}`}
                                            className="card flex items-center justify-between group"
                                        >
                                            <div className="flex items-center gap-4">
                                                <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                                                    <Beaker className="w-5 h-5 text-green-400" />
                                                </div>
                                                <div>
                                                    <h3 className="font-medium">{item.experiment.name}</h3>
                                                    <p className="text-sm text-gray-400">
                                                        {item.experiment.microbe_type.replace("_", " ")} • {new Date(item.experiment.created_at).toLocaleDateString()}
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-4">
                                                {item.result && (
                                                    <div className="text-right">
                                                        <div className="text-sm font-medium">{item.result.predicted_yield} g/L</div>
                                                        <div className="text-xs text-gray-400">
                                                            Score: {item.result.sustainability_score}/100
                                                        </div>
                                                    </div>
                                                )}
                                                <ChevronRight className="w-5 h-5 text-gray-500 group-hover:text-white transition" />
                                            </div>
                                        </Link>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Sustainability Tips */}
                        <div>
                            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                                <Leaf className="w-5 h-5 text-green-400" />
                                Sustainability Tips
                            </h2>
                            <div className="space-y-4">
                                {tips.slice(0, 3).map((tip, i) => (
                                    <div key={i} className="card">
                                        <div className="text-xs text-green-400 font-medium mb-1">{tip.category}</div>
                                        <p className="text-sm text-gray-300">{tip.tip}</p>
                                    </div>
                                ))}
                                {tips.length === 0 && (
                                    <div className="card text-sm text-gray-400">
                                        Connect to the backend to see sustainability tips!
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
