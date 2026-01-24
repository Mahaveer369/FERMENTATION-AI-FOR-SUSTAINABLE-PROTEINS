"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
    ArrowLeft, Beaker, Leaf, Zap, TrendingUp,
    Droplets, ThermometerSun, Clock, Sparkles, Download
} from "lucide-react";
import { experiments, ai } from "@/lib/api";
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    RadialBarChart, RadialBar, Legend
} from "recharts";

interface Result {
    predicted_yield: number;
    energy_usage: number;
    co2_footprint: number;
    protein_score: number;
    purity: number;
    efficiency: number;
    sustainability_score: number;
    explanation: string | null;
}

interface Experiment {
    id: number;
    name: string;
    microbe_type: string;
    substrate: string;
    temperature: number;
    ph: number;
    duration: number;
    oxygen_level: number;
    agitation_speed: number;
}

function ResultsContent() {
    const searchParams = useSearchParams();
    const experimentId = searchParams.get("id");

    const [experiment, setExperiment] = useState<Experiment | null>(null);
    const [result, setResult] = useState<Result | null>(null);
    const [loading, setLoading] = useState(true);
    const [explanation, setExplanation] = useState<string>("");
    const [loadingExplanation, setLoadingExplanation] = useState(false);

    useEffect(() => {
        if (experimentId) {
            loadExperiment(parseInt(experimentId));
        }
    }, [experimentId]);

    const loadExperiment = async (id: number) => {
        try {
            const data = await experiments.get(id);
            setExperiment(data.experiment);
            setResult(data.result);
            if (data.result?.explanation) {
                setExplanation(data.result.explanation);
            }
        } catch (err) {
            console.error("Failed to load experiment:", err);
        } finally {
            setLoading(false);
        }
    };

    const generateExplanation = async () => {
        if (!experimentId) return;
        setLoadingExplanation(true);
        try {
            const data = await ai.explain(parseInt(experimentId));
            setExplanation(data.explanation);
        } catch (err) {
            console.error("Failed to generate explanation:", err);
        } finally {
            setLoadingExplanation(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin text-4xl mb-4">⏳</div>
                    <p className="text-gray-400">Loading results...</p>
                </div>
            </div>
        );
    }

    if (!experiment || !result) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <Beaker className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                    <h2 className="text-xl font-semibold mb-2">Experiment Not Found</h2>
                    <p className="text-gray-400 mb-4">The experiment you&apos;re looking for doesn&apos;t exist.</p>
                    <Link href="/dashboard" className="btn-primary">
                        Back to Dashboard
                    </Link>
                </div>
            </div>
        );
    }

    const metricsData = [
        { name: "Yield", value: result.predicted_yield, unit: "g/L", max: 60 },
        { name: "Energy", value: result.energy_usage, unit: "kWh", max: 5 },
        { name: "CO₂", value: result.co2_footprint, unit: "kg", max: 2 },
    ];

    const scoreData = [
        { name: "Sustainability", value: result.sustainability_score, fill: "#22c55e" },
        { name: "Protein Quality", value: result.protein_score, fill: "#3b82f6" },
        { name: "Efficiency", value: result.efficiency, fill: "#a855f7" },
        { name: "Purity", value: result.purity, fill: "#f59e0b" },
    ];

    return (
        <div className="min-h-screen p-8">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-4">
                        <Link href="/dashboard" className="p-2 rounded-lg hover:bg-white/5 transition">
                            <ArrowLeft className="w-6 h-6" />
                        </Link>
                        <div>
                            <h1 className="text-2xl font-bold">{experiment.name}</h1>
                            <p className="text-gray-400">Simulation Results</p>
                        </div>
                    </div>
                    <button className="btn-secondary flex items-center gap-2">
                        <Download className="w-4 h-4" /> Export
                    </button>
                </div>

                {/* Parameters Summary */}
                <div className="card mb-8">
                    <h2 className="text-lg font-semibold mb-4">Experiment Parameters</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
                        <div className="text-center">
                            <Beaker className="w-6 h-6 mx-auto mb-2 text-green-400" />
                            <div className="text-xs text-gray-400">Microbe</div>
                            <div className="font-medium text-sm">{experiment.microbe_type.replace("_", " ")}</div>
                        </div>
                        <div className="text-center">
                            <Droplets className="w-6 h-6 mx-auto mb-2 text-blue-400" />
                            <div className="text-xs text-gray-400">Substrate</div>
                            <div className="font-medium text-sm">{experiment.substrate}</div>
                        </div>
                        <div className="text-center">
                            <ThermometerSun className="w-6 h-6 mx-auto mb-2 text-orange-400" />
                            <div className="text-xs text-gray-400">Temperature</div>
                            <div className="font-medium">{experiment.temperature}°C</div>
                        </div>
                        <div className="text-center">
                            <div className="w-6 h-6 mx-auto mb-2 text-purple-400 font-bold">pH</div>
                            <div className="text-xs text-gray-400">pH Level</div>
                            <div className="font-medium">{experiment.ph}</div>
                        </div>
                        <div className="text-center">
                            <Clock className="w-6 h-6 mx-auto mb-2 text-cyan-400" />
                            <div className="text-xs text-gray-400">Duration</div>
                            <div className="font-medium">{experiment.duration}h</div>
                        </div>
                        <div className="text-center">
                            <div className="w-6 h-6 mx-auto mb-2 text-teal-400 text-lg">O₂</div>
                            <div className="text-xs text-gray-400">Oxygen</div>
                            <div className="font-medium">{experiment.oxygen_level}%</div>
                        </div>
                        <div className="text-center">
                            <Zap className="w-6 h-6 mx-auto mb-2 text-yellow-400" />
                            <div className="text-xs text-gray-400">Agitation</div>
                            <div className="font-medium">{experiment.agitation_speed} RPM</div>
                        </div>
                    </div>
                </div>

                {/* Main Results */}
                <div className="grid lg:grid-cols-2 gap-8 mb-8">
                    {/* Key Metrics */}
                    <div className="card">
                        <h2 className="text-lg font-semibold mb-6 flex items-center gap-2">
                            <TrendingUp className="w-5 h-5 text-green-400" />
                            Predicted Outcomes
                        </h2>
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={metricsData} layout="vertical">
                                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                    <XAxis type="number" stroke="#666" />
                                    <YAxis dataKey="name" type="category" stroke="#666" width={60} />
                                    <Tooltip
                                        contentStyle={{ background: "#1a1a1a", border: "1px solid #333" }}
                                    />
                                    <Bar dataKey="value" fill="#22c55e" radius={[0, 4, 4, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-white/10">
                            <div className="text-center">
                                <div className="text-3xl font-bold text-green-400">{result.predicted_yield}</div>
                                <div className="text-sm text-gray-400">g/L Yield</div>
                            </div>
                            <div className="text-center">
                                <div className="text-3xl font-bold text-blue-400">{result.energy_usage}</div>
                                <div className="text-sm text-gray-400">kWh Energy</div>
                            </div>
                            <div className="text-center">
                                <div className="text-3xl font-bold text-orange-400">{result.co2_footprint}</div>
                                <div className="text-sm text-gray-400">kg CO₂</div>
                            </div>
                        </div>
                    </div>

                    {/* Quality Scores */}
                    <div className="card">
                        <h2 className="text-lg font-semibold mb-6 flex items-center gap-2">
                            <Leaf className="w-5 h-5 text-green-400" />
                            Quality & Sustainability Scores
                        </h2>
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <RadialBarChart cx="50%" cy="50%" innerRadius="20%" outerRadius="90%" data={scoreData} startAngle={180} endAngle={0}>
                                    <RadialBar
                                        background
                                        dataKey="value"
                                    />
                                    <Tooltip contentStyle={{ background: "#1a1a1a", border: "1px solid #333" }} />
                                </RadialBarChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="grid grid-cols-2 gap-4 mt-4">
                            {scoreData.map((score) => (
                                <div key={score.name} className="flex items-center gap-3">
                                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: score.fill }}></div>
                                    <span className="text-sm text-gray-400">{score.name}</span>
                                    <span className="font-semibold ml-auto">{score.value}%</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* AI Explanation */}
                <div className="card">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold flex items-center gap-2">
                            <Sparkles className="w-5 h-5 text-purple-400" />
                            AI Analysis
                        </h2>
                        {!explanation && (
                            <button
                                onClick={generateExplanation}
                                disabled={loadingExplanation}
                                className="btn-secondary text-sm"
                            >
                                {loadingExplanation ? "Generating..." : "Generate Explanation"}
                            </button>
                        )}
                    </div>
                    {explanation ? (
                        <p className="text-gray-300 leading-relaxed">{explanation}</p>
                    ) : (
                        <p className="text-gray-500 italic">
                            Click &quot;Generate Explanation&quot; to get AI-powered insights about your results.
                        </p>
                    )}
                </div>

                {/* Actions */}
                <div className="flex gap-4 mt-8">
                    <Link href="/experiment" className="btn-primary flex items-center gap-2">
                        Run New Experiment
                    </Link>
                    <Link href="/dashboard" className="btn-secondary">
                        Back to Dashboard
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default function ResultsPage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin text-4xl">⏳</div>
            </div>
        }>
            <ResultsContent />
        </Suspense>
    );
}
