"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
    Zap, ArrowLeft, Play, Loader2, TrendingUp,
    Leaf, Clock, ThermometerSun, FlaskConical
} from "lucide-react";
import { ai, experiments } from "@/lib/api";

interface OptimizationResult {
    best_solution: {
        temperature: number;
        ph: number;
        duration: number;
    };
    predicted_metrics: {
        yield: number;
        energy: number;
        co2: number;
        time: number;
    };
    pareto_front: Array<{
        temperature: number;
        ph: number;
        duration: number;
        fitness: number[];
    }>;
    improvements: {
        yield_improvement: number;
        time_reduction: number;
        co2_reduction: number;
    };
}

interface Microbe {
    name: string;
    display_name: string;
    optimal_temp: number;
    optimal_ph: number;
}

interface Substrate {
    name: string;
    display_name: string;
}

export default function OptimizePage() {
    const router = useRouter();
    const [microbes, setMicrobes] = useState<Microbe[]>([]);
    const [substrates, setSubstrates] = useState<Substrate[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [result, setResult] = useState<OptimizationResult | null>(null);

    const [formData, setFormData] = useState({
        microbe: "saccharomyces_cerevisiae",
        substrate: "glucose",
        baseline_temperature: 30,
        baseline_ph: 5.5,
        baseline_duration: 48,
    });

    useEffect(() => {
        // Check auth
        const token = localStorage.getItem("token");
        if (!token) {
            router.push("/login");
            return;
        }
        loadOptions();
    }, [router]);

    const loadOptions = async () => {
        try {
            const [microbeData, substrateData] = await Promise.all([
                experiments.getMicrobes(),
                experiments.getSubstrates(),
            ]);
            setMicrobes(microbeData);
            setSubstrates(substrateData);
        } catch (err) {
            console.error("Failed to load options:", err);
        }
    };

    const handleOptimize = async () => {
        setError("");
        setLoading(true);
        setResult(null);

        try {
            const data = await ai.optimize(formData);
            setResult(data);
        } catch (err: any) {
            setError(err.message || "Optimization failed");
        } finally {
            setLoading(false);
        }
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
                            <Zap className="w-7 h-7 text-yellow-400" />
                            AI Optimization
                        </h1>
                        <p className="text-gray-400">Multi-objective optimization using genetic algorithms</p>
                    </div>
                </div>

                <div className="grid lg:grid-cols-2 gap-8">
                    {/* Input Form */}
                    <div className="card">
                        <h2 className="text-lg font-semibold mb-6">Optimization Parameters</h2>

                        <div className="space-y-6">
                            {/* Microbe Selection */}
                            <div>
                                <label className="label flex items-center gap-2">
                                    <FlaskConical className="w-4 h-4" />
                                    Microorganism
                                </label>
                                <select
                                    value={formData.microbe}
                                    onChange={(e) => setFormData({ ...formData, microbe: e.target.value })}
                                    className="input-field"
                                >
                                    {microbes.map((m) => (
                                        <option key={m.name} value={m.name}>{m.display_name}</option>
                                    ))}
                                </select>
                            </div>

                            {/* Substrate Selection */}
                            <div>
                                <label className="label">Carbon Source</label>
                                <select
                                    value={formData.substrate}
                                    onChange={(e) => setFormData({ ...formData, substrate: e.target.value })}
                                    className="input-field"
                                >
                                    {substrates.map((s) => (
                                        <option key={s.name} value={s.name}>{s.display_name}</option>
                                    ))}
                                </select>
                            </div>

                            {/* Baseline Parameters */}
                            <div className="p-4 rounded-lg bg-white/5 border border-white/10">
                                <h3 className="text-sm font-medium text-gray-400 mb-4">Baseline Parameters (to improve upon)</h3>

                                <div className="grid grid-cols-3 gap-4">
                                    <div>
                                        <label className="label text-xs flex items-center gap-1">
                                            <ThermometerSun className="w-3 h-3" /> Temp (°C)
                                        </label>
                                        <input
                                            type="number"
                                            value={formData.baseline_temperature}
                                            onChange={(e) => setFormData({ ...formData, baseline_temperature: parseFloat(e.target.value) })}
                                            className="input-field"
                                            min={15}
                                            max={60}
                                        />
                                    </div>
                                    <div>
                                        <label className="label text-xs">pH Level</label>
                                        <input
                                            type="number"
                                            value={formData.baseline_ph}
                                            onChange={(e) => setFormData({ ...formData, baseline_ph: parseFloat(e.target.value) })}
                                            className="input-field"
                                            min={3}
                                            max={10}
                                            step={0.1}
                                        />
                                    </div>
                                    <div>
                                        <label className="label text-xs flex items-center gap-1">
                                            <Clock className="w-3 h-3" /> Duration (h)
                                        </label>
                                        <input
                                            type="number"
                                            value={formData.baseline_duration}
                                            onChange={(e) => setFormData({ ...formData, baseline_duration: parseFloat(e.target.value) })}
                                            className="input-field"
                                            min={1}
                                            max={168}
                                        />
                                    </div>
                                </div>
                            </div>

                            {error && (
                                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                                    {error}
                                </div>
                            )}

                            <button
                                onClick={handleOptimize}
                                disabled={loading}
                                className="btn-primary w-full flex items-center justify-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        Running Genetic Algorithm...
                                    </>
                                ) : (
                                    <>
                                        <Zap className="w-5 h-5" />
                                        Optimize Parameters
                                    </>
                                )}
                            </button>
                        </div>
                    </div>

                    {/* Results */}
                    <div>
                        {result ? (
                            <div className="space-y-6">
                                {/* Best Solution */}
                                <div className="card border-yellow-500/30">
                                    <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                        <Zap className="w-5 h-5 text-yellow-400" />
                                        Optimal Parameters Found
                                    </h2>
                                    <div className="grid grid-cols-3 gap-4">
                                        <div className="text-center p-4 rounded-lg bg-yellow-500/10">
                                            <div className="text-3xl font-bold text-yellow-400">
                                                {result.best_solution.temperature.toFixed(1)}
                                            </div>
                                            <div className="text-sm text-gray-400">°C Temperature</div>
                                        </div>
                                        <div className="text-center p-4 rounded-lg bg-yellow-500/10">
                                            <div className="text-3xl font-bold text-yellow-400">
                                                {result.best_solution.ph.toFixed(1)}
                                            </div>
                                            <div className="text-sm text-gray-400">pH Level</div>
                                        </div>
                                        <div className="text-center p-4 rounded-lg bg-yellow-500/10">
                                            <div className="text-3xl font-bold text-yellow-400">
                                                {result.best_solution.duration.toFixed(0)}
                                            </div>
                                            <div className="text-sm text-gray-400">Hours</div>
                                        </div>
                                    </div>
                                </div>

                                {/* Predicted Metrics */}
                                <div className="card">
                                    <h3 className="font-semibold mb-4">Predicted Performance</h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
                                            <div className="flex items-center gap-2 text-green-400 mb-1">
                                                <TrendingUp className="w-4 h-4" />
                                                Predicted Yield
                                            </div>
                                            <div className="text-2xl font-bold">
                                                {result.predicted_metrics.yield.toFixed(1)}
                                            </div>
                                            <div className="text-xs text-gray-500">g/L</div>
                                        </div>
                                        <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                                            <div className="flex items-center gap-2 text-emerald-400 mb-1">
                                                <Leaf className="w-4 h-4" />
                                                CO₂ Footprint
                                            </div>
                                            <div className="text-2xl font-bold">
                                                {result.predicted_metrics.co2.toFixed(2)}
                                            </div>
                                            <div className="text-xs text-gray-500">kg CO₂</div>
                                        </div>
                                    </div>
                                </div>

                                {/* Improvements */}
                                <div className="card">
                                    <h3 className="font-semibold mb-4">Improvements vs Baseline</h3>
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between p-3 rounded-lg bg-white/5">
                                            <span className="text-gray-400">Yield Improvement</span>
                                            <span className="text-green-400 font-bold">
                                                +{result.improvements.yield_improvement.toFixed(1)}%
                                            </span>
                                        </div>
                                        <div className="flex items-center justify-between p-3 rounded-lg bg-white/5">
                                            <span className="text-gray-400">Time Reduction</span>
                                            <span className="text-blue-400 font-bold">
                                                -{result.improvements.time_reduction.toFixed(1)}%
                                            </span>
                                        </div>
                                        <div className="flex items-center justify-between p-3 rounded-lg bg-white/5">
                                            <span className="text-gray-400">CO₂ Reduction</span>
                                            <span className="text-emerald-400 font-bold">
                                                -{result.improvements.co2_reduction.toFixed(1)}%
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* Use These Parameters */}
                                <Link
                                    href={`/experiment?temp=${result.best_solution.temperature}&ph=${result.best_solution.ph}&duration=${result.best_solution.duration}&microbe=${formData.microbe}&substrate=${formData.substrate}`}
                                    className="btn-primary w-full flex items-center justify-center gap-2"
                                >
                                    Use These Parameters in New Experiment
                                </Link>
                            </div>
                        ) : (
                            <div className="card text-center py-16">
                                <Zap className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                                <h3 className="text-xl font-semibold mb-2">AI Optimization</h3>
                                <p className="text-gray-400 mb-4">
                                    Select your microorganism and substrate, then run the genetic algorithm
                                    to find optimal fermentation parameters.
                                </p>
                                <div className="text-sm text-gray-500">
                                    <p>The optimizer will maximize:</p>
                                    <p className="text-green-400">✓ Protein yield</p>
                                    <p className="text-blue-400">✓ Process efficiency</p>
                                    <p className="text-emerald-400">✓ Sustainability score</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
