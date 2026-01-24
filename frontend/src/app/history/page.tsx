"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
    Beaker, ArrowLeft, History, Trash2, ChevronRight,
    Calendar, TrendingUp, Leaf, Loader2
} from "lucide-react";
import { experiments } from "@/lib/api";

interface ExperimentSummary {
    experiment: {
        id: number;
        name: string;
        microbe_type: string;
        substrate: string;
        temperature: number;
        ph: number;
        duration: number;
        created_at: string;
        status: string;
    };
    result: {
        predicted_yield: number;
        sustainability_score: number;
        energy_usage: number;
        co2_footprint: number;
    } | null;
}

export default function HistoryPage() {
    const router = useRouter();
    const [experimentList, setExperimentList] = useState<ExperimentSummary[]>([]);
    const [loading, setLoading] = useState(true);
    const [deleting, setDeleting] = useState<number | null>(null);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);

    useEffect(() => {
        // Check auth
        const token = localStorage.getItem("token");
        if (!token) {
            router.push("/login");
            return;
        }
        loadExperiments();
    }, [router, page]);

    const loadExperiments = async () => {
        try {
            const data = await experiments.list(page, 10);
            setExperimentList(data.experiments || []);
            setHasMore((data.experiments || []).length === 10);
        } catch (err) {
            console.error("Failed to load experiments:", err);
            setExperimentList([]);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm("Are you sure you want to delete this experiment?")) return;

        setDeleting(id);
        try {
            await experiments.delete(id);
            setExperimentList(experimentList.filter(e => e.experiment.id !== id));
        } catch (err) {
            console.error("Failed to delete:", err);
        } finally {
            setDeleting(null);
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="min-h-screen p-8">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="flex items-center gap-4 mb-8">
                    <Link href="/dashboard" className="p-2 rounded-lg hover:bg-white/5 transition">
                        <ArrowLeft className="w-6 h-6" />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold flex items-center gap-2">
                            <History className="w-7 h-7 text-blue-400" />
                            Experiment History
                        </h1>
                        <p className="text-gray-400">View and manage your past experiments</p>
                    </div>
                </div>

                {loading ? (
                    <div className="card text-center py-16">
                        <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-green-400" />
                        <p className="text-gray-400">Loading experiments...</p>
                    </div>
                ) : experimentList.length === 0 ? (
                    <div className="card text-center py-16">
                        <Beaker className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                        <h3 className="text-xl font-semibold mb-2">No experiments yet</h3>
                        <p className="text-gray-400 mb-6">
                            Start your first simulation to see results here
                        </p>
                        <Link href="/experiment" className="btn-primary inline-flex items-center gap-2">
                            <Beaker className="w-5 h-5" /> Run New Experiment
                        </Link>
                    </div>
                ) : (
                    <>
                        <div className="space-y-4">
                            {experimentList.map((item) => (
                                <div
                                    key={item.experiment.id}
                                    className="card flex items-center justify-between group hover:border-green-500/30 transition"
                                >
                                    <Link
                                        href={`/results?id=${item.experiment.id}`}
                                        className="flex-1 flex items-center gap-4"
                                    >
                                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500/20 to-emerald-500/20 flex items-center justify-center">
                                            <Beaker className="w-6 h-6 text-green-400" />
                                        </div>
                                        <div className="flex-1">
                                            <h3 className="font-semibold group-hover:text-green-400 transition">
                                                {item.experiment.name}
                                            </h3>
                                            <div className="flex flex-wrap gap-4 text-sm text-gray-400 mt-1">
                                                <span className="capitalize">
                                                    {item.experiment.microbe_type.replace("_", " ")}
                                                </span>
                                                <span>{item.experiment.substrate}</span>
                                                <span className="flex items-center gap-1">
                                                    <Calendar className="w-3 h-3" />
                                                    {formatDate(item.experiment.created_at)}
                                                </span>
                                            </div>
                                        </div>
                                    </Link>

                                    {item.result && (
                                        <div className="flex items-center gap-6 mr-4">
                                            <div className="text-center">
                                                <div className="flex items-center gap-1 text-green-400">
                                                    <TrendingUp className="w-4 h-4" />
                                                    <span className="font-semibold">
                                                        {item.result.predicted_yield.toFixed(1)}
                                                    </span>
                                                </div>
                                                <div className="text-xs text-gray-500">g/L yield</div>
                                            </div>
                                            <div className="text-center">
                                                <div className="flex items-center gap-1 text-emerald-400">
                                                    <Leaf className="w-4 h-4" />
                                                    <span className="font-semibold">
                                                        {item.result.sustainability_score}
                                                    </span>
                                                </div>
                                                <div className="text-xs text-gray-500">eco-score</div>
                                            </div>
                                        </div>
                                    )}

                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={(e) => {
                                                e.preventDefault();
                                                handleDelete(item.experiment.id);
                                            }}
                                            disabled={deleting === item.experiment.id}
                                            className="p-2 rounded-lg hover:bg-red-500/10 text-gray-500 hover:text-red-400 transition"
                                        >
                                            {deleting === item.experiment.id ? (
                                                <Loader2 className="w-5 h-5 animate-spin" />
                                            ) : (
                                                <Trash2 className="w-5 h-5" />
                                            )}
                                        </button>
                                        <Link
                                            href={`/results?id=${item.experiment.id}`}
                                            className="p-2 rounded-lg hover:bg-white/5 transition"
                                        >
                                            <ChevronRight className="w-5 h-5 text-gray-500 group-hover:text-white" />
                                        </Link>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Pagination */}
                        <div className="flex justify-center gap-4 mt-8">
                            <button
                                onClick={() => setPage(p => Math.max(1, p - 1))}
                                disabled={page === 1}
                                className="btn-secondary disabled:opacity-50"
                            >
                                Previous
                            </button>
                            <span className="px-4 py-2 text-gray-400">Page {page}</span>
                            <button
                                onClick={() => setPage(p => p + 1)}
                                disabled={!hasMore}
                                className="btn-secondary disabled:opacity-50"
                            >
                                Next
                            </button>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
