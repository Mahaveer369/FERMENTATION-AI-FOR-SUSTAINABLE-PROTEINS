"use client";

import { useState } from "react";
import Link from "next/link";
import {
    FlaskConical, ArrowLeft, Play, Loader2, Dna,
    Scale, Droplets, Zap, Activity, ChevronDown, ChevronUp
} from "lucide-react";
import { protein } from "@/lib/api";

interface AnalysisResult {
    name: string;
    sequence_length: number;
    molecular_weight: number;
    molecular_weight_kda: number;
    isoelectric_point: number;
    hydrophobicity: number;
    instability_index: number;
    is_stable: boolean;
    aromaticity: number;
    charge_at_ph7: number;
    amino_acid_composition: Record<string, number>;
    secondary_structure_tendency: {
        helix: number;
        sheet: number;
        coil: number;
    };
    protein_type: string;
    stability_class: string;
    recommendations: string;
}

export default function ProteinAnalysisPage() {
    const [sequence, setSequence] = useState("");
    const [name, setName] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [result, setResult] = useState<AnalysisResult | null>(null);
    const [showComposition, setShowComposition] = useState(false);

    const exampleSequences = [
        {
            name: "Hemoglobin Beta",
            sequence: "MVHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRFFESFGDLSTPDAVMGNPKVKAHGKKVLGAFSDGLAHLDNLKGTFATLSELHCDKLHVDPENFRLLGNVLVCVLAHHFGKEFTPPVQAAYQKVVAGVANALAHKYH"
        },
        {
            name: "Insulin",
            sequence: "FVNQHLCGSHLVEALYLVCGERGFFYTPKT"
        },
        {
            name: "Green Fluorescent Protein (GFP)",
            sequence: "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK"
        }
    ];

    const handleAnalyze = async () => {
        if (!sequence.trim()) {
            setError("Please enter a protein sequence");
            return;
        }

        // Clean sequence - remove spaces, numbers, newlines
        const cleanSeq = sequence.replace(/[^A-Za-z]/g, '').toUpperCase();

        // Validate amino acids
        const validAA = "ACDEFGHIKLMNPQRSTVWY";
        for (const aa of cleanSeq) {
            if (!validAA.includes(aa)) {
                setError(`Invalid amino acid: ${aa}. Valid: ${validAA}`);
                return;
            }
        }

        setError("");
        setLoading(true);
        setResult(null);

        try {
            const data = await protein.analyze({
                sequence: cleanSeq,
                name: name || "Unnamed Protein"
            });
            setResult(data);
        } catch (err: any) {
            setError(err.message || "Analysis failed");
        } finally {
            setLoading(false);
        }
    };

    const loadExample = (example: typeof exampleSequences[0]) => {
        setName(example.name);
        setSequence(example.sequence);
        setResult(null);
        setError("");
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
                            <FlaskConical className="w-7 h-7 text-purple-400" />
                            Protein Analysis
                        </h1>
                        <p className="text-gray-400">Analyze protein sequences with BioPython</p>
                    </div>
                </div>

                <div className="grid lg:grid-cols-2 gap-8">
                    {/* Input Section */}
                    <div className="space-y-6">
                        <div className="card">
                            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                <Dna className="w-5 h-5 text-purple-400" />
                                Sequence Input
                            </h2>

                            <div className="mb-4">
                                <label className="label">Protein Name (optional)</label>
                                <input
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    className="input-field"
                                    placeholder="e.g., My Protein"
                                />
                            </div>

                            <div className="mb-4">
                                <label className="label">Amino Acid Sequence</label>
                                <textarea
                                    value={sequence}
                                    onChange={(e) => setSequence(e.target.value)}
                                    className="input-field min-h-[200px] font-mono text-sm"
                                    placeholder="Enter protein sequence (single letter codes)&#10;e.g., MVHLTPEEKSAVTALWGKVNVDEVGG..."
                                />
                                <p className="text-xs text-gray-500 mt-2">
                                    {sequence.replace(/[^A-Za-z]/g, '').length} amino acids
                                </p>
                            </div>

                            {error && (
                                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm mb-4">
                                    {error}
                                </div>
                            )}

                            <button
                                onClick={handleAnalyze}
                                disabled={loading}
                                className="btn-primary w-full flex items-center justify-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        Analyzing...
                                    </>
                                ) : (
                                    <>
                                        <Play className="w-5 h-5" />
                                        Analyze Sequence
                                    </>
                                )}
                            </button>
                        </div>

                        {/* Example Sequences */}
                        <div className="card">
                            <h3 className="text-sm font-semibold text-gray-400 mb-3">Example Sequences</h3>
                            <div className="space-y-2">
                                {exampleSequences.map((ex, i) => (
                                    <button
                                        key={i}
                                        onClick={() => loadExample(ex)}
                                        className="w-full text-left p-3 rounded-lg bg-white/5 hover:bg-white/10 transition"
                                    >
                                        <div className="font-medium">{ex.name}</div>
                                        <div className="text-xs text-gray-500">
                                            {ex.sequence.length} amino acids
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Results Section */}
                    <div>
                        {result ? (
                            <div className="space-y-6">
                                {/* Overview Card */}
                                <div className="card">
                                    <h2 className="text-lg font-semibold mb-4">{result.name}</h2>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="p-4 rounded-lg bg-purple-500/10 border border-purple-500/20">
                                            <div className="flex items-center gap-2 text-purple-400 mb-1">
                                                <Scale className="w-4 h-4" />
                                                Molecular Weight
                                            </div>
                                            <div className="text-2xl font-bold">{result.molecular_weight_kda.toFixed(2)}</div>
                                            <div className="text-xs text-gray-500">kDa</div>
                                        </div>
                                        <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
                                            <div className="flex items-center gap-2 text-blue-400 mb-1">
                                                <Droplets className="w-4 h-4" />
                                                Isoelectric Point
                                            </div>
                                            <div className="text-2xl font-bold">{result.isoelectric_point.toFixed(2)}</div>
                                            <div className="text-xs text-gray-500">pI</div>
                                        </div>
                                        <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
                                            <div className="flex items-center gap-2 text-green-400 mb-1">
                                                <Activity className="w-4 h-4" />
                                                Stability
                                            </div>
                                            <div className="text-2xl font-bold">{result.stability_class}</div>
                                            <div className="text-xs text-gray-500">
                                                Index: {result.instability_index.toFixed(1)}
                                            </div>
                                        </div>
                                        <div className="p-4 rounded-lg bg-orange-500/10 border border-orange-500/20">
                                            <div className="flex items-center gap-2 text-orange-400 mb-1">
                                                <Zap className="w-4 h-4" />
                                                Protein Type
                                            </div>
                                            <div className="text-lg font-bold">{result.protein_type}</div>
                                            <div className="text-xs text-gray-500">
                                                {result.sequence_length} residues
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Secondary Structure */}
                                <div className="card">
                                    <h3 className="font-semibold mb-4">Secondary Structure Tendency</h3>
                                    <div className="space-y-3">
                                        {[
                                            { name: "α-Helix", value: result.secondary_structure_tendency.helix, color: "bg-purple-500" },
                                            { name: "β-Sheet", value: result.secondary_structure_tendency.sheet, color: "bg-blue-500" },
                                            { name: "Random Coil", value: result.secondary_structure_tendency.coil, color: "bg-gray-500" },
                                        ].map((item) => (
                                            <div key={item.name}>
                                                <div className="flex justify-between text-sm mb-1">
                                                    <span>{item.name}</span>
                                                    <span>{item.value.toFixed(1)}%</span>
                                                </div>
                                                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full ${item.color} rounded-full transition-all`}
                                                        style={{ width: `${item.value}%` }}
                                                    />
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Properties */}
                                <div className="card">
                                    <h3 className="font-semibold mb-4">Additional Properties</h3>
                                    <div className="grid grid-cols-2 gap-4 text-sm">
                                        <div className="flex justify-between p-2 rounded bg-white/5">
                                            <span className="text-gray-400">Hydrophobicity</span>
                                            <span className="font-medium">{result.hydrophobicity.toFixed(3)}</span>
                                        </div>
                                        <div className="flex justify-between p-2 rounded bg-white/5">
                                            <span className="text-gray-400">Aromaticity</span>
                                            <span className="font-medium">{(result.aromaticity * 100).toFixed(1)}%</span>
                                        </div>
                                        <div className="flex justify-between p-2 rounded bg-white/5">
                                            <span className="text-gray-400">Charge at pH 7</span>
                                            <span className="font-medium">{result.charge_at_ph7.toFixed(1)}</span>
                                        </div>
                                        <div className="flex justify-between p-2 rounded bg-white/5">
                                            <span className="text-gray-400">MW (Da)</span>
                                            <span className="font-medium">{result.molecular_weight.toFixed(1)}</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Amino Acid Composition */}
                                <div className="card">
                                    <button
                                        onClick={() => setShowComposition(!showComposition)}
                                        className="w-full flex items-center justify-between"
                                    >
                                        <h3 className="font-semibold">Amino Acid Composition</h3>
                                        {showComposition ? (
                                            <ChevronUp className="w-5 h-5 text-gray-400" />
                                        ) : (
                                            <ChevronDown className="w-5 h-5 text-gray-400" />
                                        )}
                                    </button>
                                    {showComposition && (
                                        <div className="mt-4 grid grid-cols-4 gap-2 text-sm">
                                            {Object.entries(result.amino_acid_composition)
                                                .sort(([, a], [, b]) => b - a)
                                                .map(([aa, pct]) => (
                                                    <div
                                                        key={aa}
                                                        className="p-2 rounded bg-white/5 flex justify-between"
                                                    >
                                                        <span className="font-mono font-bold text-purple-400">{aa}</span>
                                                        <span>{pct.toFixed(1)}%</span>
                                                    </div>
                                                ))
                                            }
                                        </div>
                                    )}
                                </div>

                                {/* Recommendations */}
                                {result.recommendations && (
                                    <div className="card border-green-500/30">
                                        <h3 className="font-semibold mb-2 text-green-400">Recommendations</h3>
                                        <p className="text-gray-300">{result.recommendations}</p>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="card text-center py-16">
                                <FlaskConical className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                                <h3 className="text-xl font-semibold mb-2">Enter a Sequence</h3>
                                <p className="text-gray-400">
                                    Paste a protein sequence on the left or try one of the examples
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
