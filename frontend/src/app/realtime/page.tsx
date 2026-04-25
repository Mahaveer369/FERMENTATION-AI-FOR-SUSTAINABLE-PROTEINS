"use client";

import { useState } from "react";
import Link from "next/link";
import {
    Activity, ArrowLeft, Play, Loader2, Database,
    Dna, FlaskConical, Server, CheckCircle2, XCircle,
    Route, BookOpen, Sliders
} from "lucide-react";
import { realtime } from "@/lib/api";
import MLPipeline from "@/components/MLPipeline";

interface PipelineResult {
    substrate?: {
        name: string;
        cid: number;
        formula: string;
        molecular_weight: number;
        data_source: string;
    };
    protein?: {
        accession: string;
        name: string;
        organism: string;
        sequence_length: number;
        sequence_preview: string;
        data_source: string;
        error?: string;
    };
    structure?: {
        mean_plddt: number;
        confidence_interpretation: string;
        residues_submitted: number;
        pdb_length_chars: number;
        data_source: string;
        skipped?: boolean;
        error?: string;
    };
    fermentation_insights?: string[];
    kegg?: {
        compound?: {
            kegg_id: string;
            name: string;
            formula: string;
            mol_weight: string;
        };
        pathways?: {
            pathway_id: string;
            name: string;
            description: string;
        }[];
        pathway_count?: number;
        error?: string;
    };
    bionumbers?: {
        organism_profiles?: Record<string, any>;
        fermentation_constants?: Record<string, any>;
    };
}

export default function RealTimePipelinePage() {
    const [formData, setFormData] = useState({
        substrate_name: "glucose",
        protein_name: "ovalbumin",
        organism: "Gallus gallus",
        predict_structure: true,
        temperature: 30,
        ph: 5.5,
        duration: 48,
        oxygen: 21,
        agitation: 200,
        volume: 1000,
        microbe_type: "saccharomyces_cerevisiae"
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [result, setResult] = useState<PipelineResult | null>(null);
    const [apiStatus, setApiStatus] = useState<any>(null);
    const [checkingStatus, setCheckingStatus] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, type, checked } = e.target;
        setFormData({
            ...formData,
            [name]: type === "checkbox" ? checked : value,
        });
    };

    const handleVerify = async () => {
        setCheckingStatus(true);
        try {
            const res = await realtime.verify();
            setApiStatus(res);
        } catch (err: any) {
            setApiStatus({ error: err.message || "Failed to reach backend." });
        } finally {
            setCheckingStatus(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);
        setResult(null);

        try {
            const pipelineData = await realtime.runPipeline(formData);
            setResult(pipelineData);
        } catch (err: any) {
            setError(err.message || "Pipeline execution failed");
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
                            <Activity className="w-7 h-7 text-green-400" />
                            Real-Time Biological API Pipeline
                        </h1>
                        <p className="text-gray-400">Fetch live data from PubChem, UniProt, NVIDIA ESMFold, KEGG, and BioNumbers</p>
                    </div>
                </div>

                <div className="grid lg:grid-cols-2 gap-8">
                    {/* Left Column = Forms and Status */}
                    <div className="space-y-6">
                        {/* API Health Check */}
                        <div className="card">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-lg font-semibold flex items-center gap-2">
                                    <Server className="w-5 h-5 text-blue-400" />
                                    API Health Check
                                </h2>
                                <button
                                    onClick={handleVerify}
                                    disabled={checkingStatus}
                                    className="btn-secondary text-sm px-3 py-1"
                                >
                                    {checkingStatus ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Run Check'}
                                </button>
                            </div>

                            {apiStatus && !apiStatus.error && (
                                <div className="space-y-2 text-sm bg-black/20 p-4 rounded-lg">
                                    <div className="flex justify-between items-center">
                                        <span>PubChem (Substrates):</span>
                                        {apiStatus.PubChem?.status?.includes('PASS') ? <CheckCircle2 className="w-4 h-4 text-green-400" /> : <XCircle className="w-4 h-4 text-red-400" />}
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span>UniProt (Proteins):</span>
                                        {apiStatus.UniProt?.status?.includes('PASS') ? <CheckCircle2 className="w-4 h-4 text-green-400" /> : <XCircle className="w-4 h-4 text-red-400" />}
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span>NVIDIA ESMFold (3D Struct):</span>
                                        {apiStatus.ESMFold?.status?.includes('PASS') ? <CheckCircle2 className="w-4 h-4 text-green-400" /> : <XCircle className="w-4 h-4 text-red-400" />}
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span>KEGG (Metabolic Pathways):</span>
                                        {apiStatus.KEGG?.status?.includes('PASS') ? <CheckCircle2 className="w-4 h-4 text-green-400" /> : <XCircle className="w-4 h-4 text-red-400" />}
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span>BioNumbers (Published Constants):</span>
                                        {apiStatus.BioNumbers?.status?.includes('PASS') ? <CheckCircle2 className="w-4 h-4 text-green-400" /> : <XCircle className="w-4 h-4 text-red-400" />}
                                    </div>
                                    {apiStatus._summary && (
                                        <div className="mt-2 pt-2 border-t border-white/10 text-center font-semibold">
                                            {apiStatus._summary.passed}/{apiStatus._summary.total} APIs Passed
                                        </div>
                                    )}
                                </div>
                            )}

                            {apiStatus?.error && (
                                <div className="text-red-400 text-sm mt-2">{apiStatus.error}</div>
                            )}
                        </div>

                        {/* Pipeline Input */}
                        <div className="card">
                            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                <FlaskConical className="w-5 h-5 text-purple-400" />
                                Configure Pipeline
                            </h2>

                            <form onSubmit={handleSubmit} className="space-y-4">
                                <div>
                                    <label className="label">Substrate Name (PubChem + KEGG)</label>
                                    <input
                                        type="text"
                                        name="substrate_name"
                                        value={formData.substrate_name}
                                        onChange={handleChange}
                                        className="input-field"
                                        placeholder="e.g., glucose, sucrose"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="label">Protein Name (UniProt Search)</label>
                                    <input
                                        type="text"
                                        name="protein_name"
                                        value={formData.protein_name}
                                        onChange={handleChange}
                                        className="input-field"
                                        placeholder="e.g., ovalbumin, casein"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="label">Organism Filter (UniProt Search)</label>
                                    <input
                                        type="text"
                                        name="organism"
                                        value={formData.organism}
                                        onChange={handleChange}
                                        className="input-field"
                                        placeholder="e.g., Gallus gallus"
                                        required
                                    />
                                </div>

                                <div className="flex items-center gap-2 py-2">
                                    <input
                                        type="checkbox"
                                        id="predict_structure"
                                        name="predict_structure"
                                        checked={formData.predict_structure}
                                        onChange={handleChange}
                                        className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-green-500 focus:ring-green-500"
                                    />
                                    <label htmlFor="predict_structure" className="text-sm font-medium text-gray-300">
                                        Run NVIDIA ESMFold Structure Prediction (adds ~30-60s)
                                    </label>
                                </div>

                                {error && (
                                    <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                                        {error}
                                    </div>
                                )}

                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="btn-primary w-full flex items-center justify-center gap-2 mt-4"
                                >
                                    {loading ? (
                                        <>
                                            <Loader2 className="w-5 h-5 animate-spin" />
                                            Running 5-API Pipeline...
                                        </>
                                    ) : (
                                        <>
                                            <Play className="w-5 h-5" />
                                            Start Pipeline
                                        </>
                                    )}
                                </button>
                            </form>
                        </div>

                        {/* Simulation Parameters */}
                        <div className="card border-blue-500/30">
                            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 text-blue-400">
                                <Sliders className="w-5 h-5" />
                                Interactive Simulation Parameters
                            </h2>
                            <div className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="label">Temperature (°C): {formData.temperature}</label>
                                        <input type="range" name="temperature" min="15" max="60" step="0.5" value={formData.temperature} onChange={handleChange} className="w-full accent-blue-500" />
                                    </div>
                                    <div>
                                        <label className="label">pH: {formData.ph}</label>
                                        <input type="range" name="ph" min="3" max="10" step="0.1" value={formData.ph} onChange={handleChange} className="w-full accent-blue-500" />
                                    </div>
                                    <div>
                                        <label className="label">Duration (h): {formData.duration}</label>
                                        <input type="range" name="duration" min="1" max="168" value={formData.duration} onChange={handleChange} className="w-full accent-blue-500" />
                                    </div>
                                    <div>
                                        <label className="label">Oxygen (%): {formData.oxygen}</label>
                                        <input type="range" name="oxygen" min="0" max="100" value={formData.oxygen} onChange={handleChange} className="w-full accent-blue-500" />
                                    </div>
                                    <div>
                                        <label className="label">Agitation (RPM): {formData.agitation}</label>
                                        <input type="range" name="agitation" min="0" max="500" value={formData.agitation} onChange={handleChange} className="w-full accent-blue-500" />
                                    </div>
                                    <div>
                                        <label className="label">Volume (L): {formData.volume}</label>
                                        <input type="number" name="volume" min="1" value={formData.volume} onChange={handleChange} className="input-field" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Right Column = Results */}
                    <div>
                        {result ? (
                            <div className="space-y-6">
                                {/* Substrate Data */}
                                {result.substrate && !('error' in result.substrate) && (
                                    <div className="card border-blue-500/30">
                                        <h3 className="font-bold flex items-center gap-2 mb-4 text-blue-400">
                                            <Database className="w-5 h-5" />
                                            PubChem Insights: {result.substrate.name}
                                        </h3>
                                        <div className="grid grid-cols-2 gap-4 text-sm bg-black/20 p-4 rounded-lg">
                                            <div>
                                                <div className="text-gray-400">Formula</div>
                                                <div className="font-bold font-mono">{result.substrate.formula}</div>
                                            </div>
                                            <div>
                                                <div className="text-gray-400">Mol Weight</div>
                                                <div className="font-bold">{result.substrate.molecular_weight} g/mol</div>
                                            </div>
                                            <div className="col-span-2">
                                                <div className="text-gray-400">PubChem CID</div>
                                                <div>{result.substrate.cid}</div>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* Protein Data */}
                                {result.protein && !result.protein.error && (
                                    <div className="card border-purple-500/30">
                                        <h3 className="font-bold flex items-center gap-2 mb-4 text-purple-400">
                                            <Dna className="w-5 h-5" />
                                            UniProt Insights: {result.protein.name}
                                        </h3>
                                        <div className="grid grid-cols-2 gap-4 text-sm bg-black/20 p-4 rounded-lg">
                                            <div>
                                                <div className="text-gray-400">Accession</div>
                                                <div className="font-bold">{result.protein.accession}</div>
                                            </div>
                                            <div>
                                                <div className="text-gray-400">Length</div>
                                                <div className="font-bold">{result.protein.sequence_length} aa</div>
                                            </div>
                                            <div className="col-span-2">
                                                <div className="text-gray-400">Sequence Preview</div>
                                                <div className="font-mono text-xs break-all opacity-80 mt-1 line-clamp-3">
                                                    {result.protein.sequence_preview}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* Structural Data */}
                                {result.structure && !result.structure.error && !result.structure.skipped && (
                                    <div className="card border-green-500/30">
                                        <h3 className="font-bold flex items-center gap-2 mb-4 text-green-400">
                                            <Activity className="w-5 h-5" />
                                            NVIDIA ESMFold Predictions
                                        </h3>
                                        <div className="bg-black/20 p-4 rounded-lg">
                                            <div className="flex justify-between items-center mb-2">
                                                <span className="text-sm text-gray-400">Confidence Score (pLDDT)</span>
                                                <span className="font-bold text-lg text-green-400">
                                                    {result.structure.mean_plddt?.toFixed(1)} / 100
                                                </span>
                                            </div>
                                            <div className="w-full bg-gray-700 rounded-full h-2.5">
                                                <div className="bg-green-500 h-2.5 rounded-full" style={{ width: `${result.structure.mean_plddt}%` }}></div>
                                            </div>
                                            <div className="mt-3 text-sm text-gray-400">
                                                {result.structure.confidence_interpretation}
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* KEGG Metabolic Pathways */}
                                {result.kegg && !result.kegg.error && result.kegg.pathways && result.kegg.pathways.length > 0 && (
                                    <div className="card border-teal-500/30">
                                        <h3 className="font-bold flex items-center gap-2 mb-4 text-teal-400">
                                            <Route className="w-5 h-5" />
                                            KEGG Metabolic Pathways
                                        </h3>
                                        {result.kegg.compound && (
                                            <div className="bg-black/20 p-3 rounded-lg mb-3 text-sm">
                                                <span className="text-gray-400">Compound: </span>
                                                <span className="font-bold">{result.kegg.compound.name}</span>
                                                <span className="text-gray-500"> ({result.kegg.compound.kegg_id})</span>
                                                <span className="text-gray-400 ml-2">{result.kegg.compound.formula}</span>
                                            </div>
                                        )}
                                        <div className="space-y-2">
                                            {result.kegg.pathways.map((pw, idx) => (
                                                <div key={idx} className="bg-black/20 p-3 rounded-lg border-l-4 border-l-teal-500 text-sm">
                                                    <div className="flex items-center gap-2">
                                                        <span className="text-teal-300 font-mono text-xs">{pw.pathway_id}</span>
                                                        <span className="font-medium text-gray-200">{pw.name}</span>
                                                    </div>
                                                    {pw.description && (
                                                        <p className="text-gray-400 text-xs mt-1 line-clamp-2">{pw.description}</p>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* BioNumbers Published Constants */}
                                {result.bionumbers && result.bionumbers.organism_profiles && (
                                    <div className="card border-amber-500/30">
                                        <h3 className="font-bold flex items-center gap-2 mb-4 text-amber-400">
                                            <BookOpen className="w-5 h-5" />
                                            BioNumbers — Published Growth Constants
                                        </h3>
                                        <div className="space-y-2 text-sm">
                                            {Object.entries(result.bionumbers.organism_profiles)
                                                .filter(([key]) => !key.includes('energy'))
                                                .slice(0, 4)
                                                .map(([key, val]: [string, any]) => (
                                                    <div key={key} className="bg-black/20 p-3 rounded-lg border-l-4 border-l-amber-500">
                                                        <span className="font-medium text-amber-300 capitalize">{key.replace(/_/g, ' ')}</span>
                                                        <div className="grid grid-cols-3 gap-2 mt-1 text-gray-400">
                                                            <div>Growth: <span className="text-white">{val.growth_rate} /h</span></div>
                                                            <div>Doubling: <span className="text-white">{val.doubling_time_min} min</span></div>
                                                            <div>Yield: <span className="text-white">{val.max_yield_g_per_g} g/g</span></div>
                                                        </div>
                                                        <div className="text-xs text-gray-500 mt-1">BNID: {val.bnid}</div>
                                                    </div>
                                                ))}
                                        </div>
                                    </div>
                                )}

                                {/* Fermentation Insights */}
                                {result.fermentation_insights && result.fermentation_insights.length > 0 && (
                                    <div className="card border-orange-500/30">
                                        <h3 className="font-bold flex items-center gap-2 mb-4 text-orange-400">
                                            <FlaskConical className="w-5 h-5" />
                                            Fermentation Implications
                                        </h3>
                                        <div className="space-y-3 text-sm">
                                            {result.fermentation_insights.map((insight, idx) => (
                                                <div key={idx} className="bg-black/20 p-3 rounded-lg border-l-4 border-l-orange-500">
                                                    <span className="font-medium text-gray-200">{insight}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="card text-center py-16 h-full flex flex-col items-center justify-center">
                                {loading ? (
                                    <>
                                        <Loader2 className="w-16 h-16 text-green-500 animate-spin mb-4" />
                                        <h3 className="text-xl font-semibold mb-2">Connecting to 5 Scientific Databases</h3>
                                        <p className="text-gray-400 max-w-sm">
                                            Fetching from PubChem, UniProt, ESMFold, KEGG metabolic pathways, and BioNumbers published constants...
                                        </p>
                                    </>
                                ) : (
                                    <>
                                        <Activity className="w-16 h-16 text-gray-600 mb-4" />
                                        <h3 className="text-xl font-semibold mb-2">Ready to Run</h3>
                                        <p className="text-gray-400 max-w-sm">
                                            Click Start Pipeline to orchestrate data collection across all 5 scientific API endpoints.
                                        </p>
                                    </>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                {/* ML Pipeline Visualization */}
                <div className="mt-8">
                    <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                        <Activity className="w-6 h-6 text-green-400" />
                        Interactive ML Pipeline
                    </h2>
                    <p className="text-gray-400 mb-6">
                        Watch parameters flow through the system. Adjust sliders above to see real-time recalculations instantly over the graph.
                    </p>
                    <MLPipeline params={formData} />
                </div>
            </div>
        </div>
    );
}
