"use client";

import { useState, useEffect, useRef, useCallback, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
    ArrowLeft, Beaker, Leaf, Zap, TrendingUp,
    Droplets, ThermometerSun, Clock, Sparkles, Download,
    AlertCircle, Settings, CheckCircle, RotateCcw, ArrowRight, Activity
} from "lucide-react";
import { experiments, ai } from "@/lib/api";
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    RadialBarChart, RadialBar, Legend, Cell
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
    recommendations: string | null;
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
    const [pdbData, setPdbData] = useState<string>("");
    const [cleanRecommendations, setCleanRecommendations] = useState<string>("");
    const viewerRef = useRef<HTMLDivElement>(null);
    const [viewer3dReady, setViewer3dReady] = useState(false);

    // Extract PDB data from recommendations field
    useEffect(() => {
        if (result?.recommendations) {
            const pdbMatch = result.recommendations.match(/__PDB_START__([\s\S]+?)__PDB_END__/);
            if (pdbMatch) {
                setPdbData(pdbMatch[1]);
                setCleanRecommendations(result.recommendations.replace(/__PDB_START__[\s\S]+?__PDB_END__/, '').trim());
            } else {
                setCleanRecommendations(result.recommendations);
            }
        }
    }, [result]);

    // Load 3Dmol.js from CDN when PDB data is available
    useEffect(() => {
        if (!pdbData) return;
        if ((window as any).$3Dmol) { setViewer3dReady(true); return; }
        const jq = document.createElement('script');
        jq.src = 'https://code.jquery.com/jquery-3.7.1.min.js';
        jq.onload = () => {
            const mol = document.createElement('script');
            mol.src = 'https://3Dmol.org/build/3Dmol-min.js';
            mol.onload = () => setViewer3dReady(true);
            document.head.appendChild(mol);
        };
        document.head.appendChild(jq);
    }, [pdbData]);

    // Render 3D structure
    useEffect(() => {
        if (!viewer3dReady || !pdbData || !viewerRef.current) return;
        const $3Dmol = (window as any).$3Dmol;
        if (!$3Dmol) return;
        viewerRef.current.innerHTML = '';
        const viewer = $3Dmol.createViewer(viewerRef.current, {
            backgroundColor: '#0a0a0f', antialias: true,
        });
        viewer.addModel(pdbData, 'pdb');
        viewer.setStyle({}, { cartoon: { color: 'spectrum', opacity: 0.95 } });
        viewer.addSurface($3Dmol.SurfaceType.VDW, { opacity: 0.12, color: 'white' });
        viewer.zoomTo();
        viewer.spin('y', 0.5);
        viewer.render();
    }, [viewer3dReady, pdbData]);

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

    // Yield quality thresholds - based on optimal vs non-optimal conditions
    const getYieldQuality = (yieldValue: number, isOptimized: boolean = false) => {
        if (isOptimized) {
            // After optimization - always show green
            return { label: "Excellent", color: "#22c55e", bgColor: "bg-green-500" };
        }
        // Before optimization - show yellow/red for poor conditions
        if (yieldValue >= 15) return { label: "Good", color: "#22c55e", bgColor: "bg-green-500" };
        if (yieldValue >= 8) return { label: "Moderate", color: "#f59e0b", bgColor: "bg-yellow-500" };
        return { label: "Needs Improvement", color: "#ef4444", bgColor: "bg-red-500" };
    };

    // Optimal parameters based on microbe type
    const getOptimalParams = (microbeType: string) => {
        const optimalParams: Record<string, { temp: number; ph: number; duration: number; agitation: number; oxygen: number }> = {
            "lactobacillus_casei": { temp: 30, ph: 5.5, duration: 48, agitation: 150, oxygen: 30 },
            "lactobacillus_plantarum": { temp: 30, ph: 5.5, duration: 36, agitation: 120, oxygen: 40 },
            "bacillus_subtilis": { temp: 37, ph: 7.0, duration: 24, agitation: 200, oxygen: 60 },
            "bacillus_licheniformis": { temp: 37, ph: 7.0, duration: 30, agitation: 180, oxygen: 50 },
            "streptococcus_thermophilus": { temp: 40, ph: 6.5, duration: 24, agitation: 100, oxygen: 20 },
            "propionibacterium_freudenreichii": { temp: 30, ph: 6.5, duration: 72, agitation: 80, oxygen: 25 },
            "pseudomonas_fluorescens": { temp: 25, ph: 7.0, duration: 36, agitation: 160, oxygen: 70 },
            "lactobacillus_rhamnosus": { temp: 30, ph: 5.5, duration: 48, agitation: 140, oxygen: 35 },
            "lactobacillus_acidophilus": { temp: 37, ph: 5.5, duration: 36, agitation: 130, oxygen: 30 },
            "bifidobacterium_bifidum": { temp: 37, ph: 6.0, duration: 48, agitation: 100, oxygen: 15 },
            "enterococcus_faecium": { temp: 30, ph: 6.5, duration: 36, agitation: 120, oxygen: 40 },
            "saccharomyces_cerevisiae": { temp: 30, ph: 5.0, duration: 24, agitation: 200, oxygen: 80 },
            "pichia_pastoris": { temp: 28, ph: 5.5, duration: 48, agitation: 180, oxygen: 100 },
            "escherichia_coli": { temp: 37, ph: 7.0, duration: 24, agitation: 200, oxygen: 60 },
            "aspergillus_niger": { temp: 30, ph: 5.5, duration: 72, agitation: 100, oxygen: 50 },
            "corynebacterium_glutamicum": { temp: 30, ph: 7.5, duration: 48, agitation: 150, oxygen: 40 },
            "clostridium_butyricum": { temp: 30, ph: 6.5, duration: 48, agitation: 50, oxygen: 5 },
            "pediococcus_acidilactici": { temp: 30, ph: 6.0, duration: 36, agitation: 120, oxygen: 35 },
        };
        return optimalParams[microbeType] || { temp: 30, ph: 6.0, duration: 36, agitation: 150, oxygen: 40 };
    };

    const optimalParams = getOptimalParams(experiment.microbe_type);

    // Get parameter difference for suggestions
    const getParamDiff = (current: number, optimal: number, isLowerBetter: boolean = false) => {
        const diff = current - optimal;
        if (isLowerBetter) {
            return diff > 0 ? { status: "high", text: `Reduce to ${optimal}`, needsChange: diff > 0 } : { status: "ok", text: "Optimal", needsChange: false };
        }
        return Math.abs(diff) > 2 ? { status: diff > 0 ? "high" : "low", text: diff > 0 ? `Reduce to ${optimal}` : `Increase to ${optimal}`, needsChange: true } : { status: "ok", text: "Optimal", needsChange: false };
    };

    const tempDiff = getParamDiff(experiment.temperature, optimalParams.temp);
    const phDiff = getParamDiff(experiment.ph, optimalParams.ph);
    const durationDiff = getParamDiff(experiment.duration, optimalParams.duration);
    const agitationDiff = getParamDiff(experiment.agitation_speed, optimalParams.agitation);
    const oxygenDiff = getParamDiff(experiment.oxygen_level, optimalParams.oxygen);

    // Check if parameters are optimized (close to optimal values)
    const isOptimized = !tempDiff.needsChange && !phDiff.needsChange;

    const yieldQuality = getYieldQuality(result.predicted_yield, isOptimized);

    const needsOptimization = yieldQuality.label === "Needs Improvement";

    // Color helper for Energy and CO2 (lower is better)
    const getMetricColor = (value: number, max: number) => {
        const percentage = (value / max) * 100;
        return percentage <= 50 ? "#22c55e" : percentage <= 75 ? "#f59e0b" : "#ef4444";
    };

    const metricsData = [
        { name: "Yield", value: result.predicted_yield, unit: "g/L", fill: yieldQuality.color },
        { name: "Energy", value: result.energy_usage, unit: "kWh", fill: getMetricColor(result.energy_usage, 5) },
        { name: "CO₂", value: result.co2_footprint, unit: "kg", fill: getMetricColor(result.co2_footprint, 2) },
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
                                    <Bar
                                        dataKey="value"
                                        radius={[0, 4, 4, 0]}
                                    >
                                        {metricsData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.fill} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-white/10">
                            <div className="text-center">
                                <div className="flex items-center justify-center gap-2">
                                    <div className="text-3xl font-bold" style={{ color: yieldQuality.color }}>{result.predicted_yield}</div>
                                </div>
                                <div className="text-sm text-gray-400">g/L Yield</div>
                                <div className={`mt-1 px-2 py-0.5 rounded text-xs font-medium ${yieldQuality.bgColor} bg-opacity-20 text-white`} style={{ color: yieldQuality.color }}>
                                    {yieldQuality.label}
                                </div>
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

                {/* 3D Protein Structure Viewer */}
                {pdbData && (
                    <div className="card mb-8 border border-purple-500/30 bg-gradient-to-r from-purple-900/20 to-indigo-900/10">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 text-purple-400">
                            🧬 3D Protein Structure (ESMFold Prediction)
                        </h2>
                        <div
                            ref={viewerRef}
                            style={{ width: '100%', height: '400px', borderRadius: '12px', overflow: 'hidden' }}
                            className="border border-purple-500/20"
                        />
                        <div className="mt-3 flex items-center gap-4 text-xs text-gray-400">
                            <span>🌈 Rainbow = N→C terminus</span>
                            <span>🔄 Auto-rotating — click &amp; drag to interact</span>
                            <span>🔬 Predicted by NVIDIA ESMFold API</span>
                        </div>
                    </div>
                )}

                {/* Real-Time API Data Insights */}
                {cleanRecommendations && (
                    <div className="card mb-8 border border-green-500/30 bg-gradient-to-r from-green-900/20 to-teal-900/10">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 text-green-400">
                            <Activity className="w-5 h-5" />
                            Live API Data Used in This Simulation
                        </h2>
                        <div className="space-y-3">
                            {cleanRecommendations.split(/(📦|🧬|🔬|💡|🗺️|📊|⚠️)/).filter(Boolean).reduce((acc: string[], curr, i, arr) => {
                                if (['📦', '🧬', '🔬', '💡', '🗺️', '📊', '⚠️'].includes(curr)) {
                                    acc.push(curr + (arr[i + 1] || ''));
                                } else if (i === 0 || !['📦', '🧬', '🔬', '💡', '🗺️', '📊', '⚠️'].includes(arr[i - 1])) {
                                    acc.push(curr);
                                }
                                return acc;
                            }, []).map((line, idx) => {
                                const trimmed = line.trim();
                                if (!trimmed) return null;

                                let borderColor = 'border-gray-700';
                                let bgColor = 'bg-gray-800/50';
                                let label = '';

                                if (trimmed.startsWith('📦')) {
                                    borderColor = 'border-blue-500/40';
                                    bgColor = 'bg-blue-900/20';
                                    label = 'PubChem';
                                } else if (trimmed.startsWith('🧬')) {
                                    borderColor = 'border-purple-500/40';
                                    bgColor = 'bg-purple-900/20';
                                    label = 'UniProt';
                                } else if (trimmed.startsWith('🔬')) {
                                    borderColor = 'border-cyan-500/40';
                                    bgColor = 'bg-cyan-900/20';
                                    label = 'ESMFold';
                                } else if (trimmed.startsWith('🗺️')) {
                                    borderColor = 'border-teal-500/40';
                                    bgColor = 'bg-teal-900/20';
                                    label = 'KEGG';
                                } else if (trimmed.startsWith('📊')) {
                                    borderColor = 'border-amber-500/40';
                                    bgColor = 'bg-amber-900/20';
                                    label = 'BioNumbers';
                                } else if (trimmed.startsWith('⚠️')) {
                                    borderColor = 'border-red-500/40';
                                    bgColor = 'bg-red-900/20';
                                    label = 'Optimization Warning';
                                } else if (trimmed.startsWith('💡')) {
                                    borderColor = 'border-yellow-500/40';
                                    bgColor = 'bg-yellow-900/20';
                                    label = 'Insight';
                                }

                                return (
                                    <div key={idx} className={`p-3 rounded-lg border ${borderColor} ${bgColor}`}>
                                        {label && (
                                            <span className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-1 block">
                                                {label}
                                            </span>
                                        )}
                                        <p className="text-gray-200 text-sm">{trimmed}</p>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}

                {/* Optimization Suggestions - Only show when yield is low */}
                {needsOptimization && (
                    <div className="card bg-gradient-to-r from-orange-900/30 to-red-900/20 border border-orange-500/30">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold flex items-center gap-2">
                                <AlertCircle className="w-5 h-5 text-orange-400" />
                                Optimization Suggestions
                            </h2>
                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${yieldQuality.label === "Poor" ? "bg-red-500/20 text-red-400" : "bg-yellow-500/20 text-yellow-400"
                                }`}>
                                {yieldQuality.label} Yield
                            </span>
                        </div>

                        <p className="text-gray-400 mb-6">
                            Your current yield can be improved by adjusting these parameters for optimal <span className="text-purple-400">{experiment.microbe_type.replace("_", " ")}</span> growth:
                        </p>

                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {/* Temperature */}
                            <div className={`p-4 rounded-lg border transition-all duration-300 ${tempDiff.needsChange ? "border-orange-500/50 bg-orange-500/10" : "border-green-500/30 bg-green-500/10"
                                }`}>
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                        <ThermometerSun className={`w-4 h-4 ${tempDiff.needsChange ? "text-orange-400" : "text-green-400"}`} />
                                        <span className="text-sm font-medium">Temperature</span>
                                    </div>
                                    {tempDiff.needsChange ? <ArrowRight className="w-4 h-4 text-orange-400" /> : <CheckCircle className="w-4 h-4 text-green-400" />}
                                </div>
                                <div className="text-xs text-gray-500 mb-1">Current: <span className="text-white">{experiment.temperature}°C</span></div>
                                <div className="text-xs text-gray-500">Optimal: <span className="text-green-400">{optimalParams.temp}°C</span></div>
                                {tempDiff.needsChange && (
                                    <div className="mt-2 text-xs text-orange-400 animate-pulse">{tempDiff.text}</div>
                                )}
                            </div>

                            {/* pH */}
                            <div className={`p-4 rounded-lg border transition-all duration-300 ${phDiff.needsChange ? "border-orange-500/50 bg-orange-500/10" : "border-green-500/30 bg-green-500/10"
                                }`}>
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                        <Droplets className={`w-4 h-4 ${phDiff.needsChange ? "text-orange-400" : "text-green-400"}`} />
                                        <span className="text-sm font-medium">pH Level</span>
                                    </div>
                                    {phDiff.needsChange ? <ArrowRight className="w-4 h-4 text-orange-400" /> : <CheckCircle className="w-4 h-4 text-green-400" />}
                                </div>
                                <div className="text-xs text-gray-500 mb-1">Current: <span className="text-white">{experiment.ph}</span></div>
                                <div className="text-xs text-gray-500">Optimal: <span className="text-green-400">{optimalParams.ph}</span></div>
                                {phDiff.needsChange && (
                                    <div className="mt-2 text-xs text-orange-400 animate-pulse">{phDiff.text}</div>
                                )}
                            </div>

                            {/* Duration */}
                            <div className={`p-4 rounded-lg border transition-all duration-300 ${durationDiff.needsChange ? "border-orange-500/50 bg-orange-500/10" : "border-green-500/30 bg-green-500/10"
                                }`}>
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                        <Clock className={`w-4 h-4 ${durationDiff.needsChange ? "text-orange-400" : "text-green-400"}`} />
                                        <span className="text-sm font-medium">Duration</span>
                                    </div>
                                    {durationDiff.needsChange ? <ArrowRight className="w-4 h-4 text-orange-400" /> : <CheckCircle className="w-4 h-4 text-green-400" />}
                                </div>
                                <div className="text-xs text-gray-500 mb-1">Current: <span className="text-white">{experiment.duration}h</span></div>
                                <div className="text-xs text-gray-500">Optimal: <span className="text-green-400">{optimalParams.duration}h</span></div>
                                {durationDiff.needsChange && (
                                    <div className="mt-2 text-xs text-orange-400 animate-pulse">{durationDiff.text}</div>
                                )}
                            </div>

                            {/* Agitation */}
                            <div className={`p-4 rounded-lg border transition-all duration-300 ${agitationDiff.needsChange ? "border-orange-500/50 bg-orange-500/10" : "border-green-500/30 bg-green-500/10"
                                }`}>
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                        <RotateCcw className={`w-4 h-4 ${agitationDiff.needsChange ? "text-orange-400" : "text-green-400"}`} />
                                        <span className="text-sm font-medium">Agitation</span>
                                    </div>
                                    {agitationDiff.needsChange ? <ArrowRight className="w-4 h-4 text-orange-400" /> : <CheckCircle className="w-4 h-4 text-green-400" />}
                                </div>
                                <div className="text-xs text-gray-500 mb-1">Current: <span className="text-white">{experiment.agitation_speed} RPM</span></div>
                                <div className="text-xs text-gray-500">Optimal: <span className="text-green-400">{optimalParams.agitation} RPM</span></div>
                                {agitationDiff.needsChange && (
                                    <div className="mt-2 text-xs text-orange-400 animate-pulse">{agitationDiff.text}</div>
                                )}
                            </div>

                            {/* Oxygen */}
                            <div className={`p-4 rounded-lg border transition-all duration-300 ${oxygenDiff.needsChange ? "border-orange-500/50 bg-orange-500/10" : "border-green-500/30 bg-green-500/10"
                                }`}>
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                        <Zap className={`w-4 h-4 ${oxygenDiff.needsChange ? "text-orange-400" : "text-green-400"}`} />
                                        <span className="text-sm font-medium">Oxygen Level</span>
                                    </div>
                                    {oxygenDiff.needsChange ? <ArrowRight className="w-4 h-4 text-orange-400" /> : <CheckCircle className="w-4 h-4 text-green-400" />}
                                </div>
                                <div className="text-xs text-gray-500 mb-1">Current: <span className="text-white">{experiment.oxygen_level}%</span></div>
                                <div className="text-xs text-gray-500">Optimal: <span className="text-green-400">{optimalParams.oxygen}%</span></div>
                                {oxygenDiff.needsChange && (
                                    <div className="mt-2 text-xs text-orange-400 animate-pulse">{oxygenDiff.text}</div>
                                )}
                            </div>
                        </div>

                        <div className="mt-6 pt-4 border-t border-orange-500/20">
                            <Link
                                href={`/experiment?microbe=${experiment.microbe_type}&substrate=${experiment.substrate}&temp=${optimalParams.temp}&ph=${optimalParams.ph}&duration=${optimalParams.duration}&agitation=${optimalParams.agitation}&oxygen=${optimalParams.oxygen}`}
                                className="btn-primary flex items-center justify-center gap-2"
                            >
                                <Settings className="w-4 h-4" />
                                Run Optimized Experiment
                            </Link>
                        </div>
                    </div>
                )}

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
