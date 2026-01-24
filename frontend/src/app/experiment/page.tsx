"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
    Beaker, ArrowLeft, Play, Loader2, ThermometerSun,
    Clock, FlaskConical, Wind, Settings2
} from "lucide-react";
import { experiments } from "@/lib/api";

interface Microbe {
    name: string;
    display_name: string;
    optimal_temp: number;
    optimal_ph: number;
    max_yield: number;
    description: string;
}

interface Substrate {
    name: string;
    display_name: string;
    energy: number;
    description: string;
}

export default function ExperimentPage() {
    const router = useRouter();
    const [microbes, setMicrobes] = useState<Microbe[]>([]);
    const [substrates, setSubstrates] = useState<Substrate[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    const [formData, setFormData] = useState({
        name: "",
        microbe_type: "saccharomyces_cerevisiae",
        substrate: "glucose",
        temperature: 30,
        ph: 5.5,
        duration: 48,
        oxygen_level: 21,
        agitation_speed: 200,
    });

    useEffect(() => {
        // Check authentication
        const token = localStorage.getItem("token");
        if (!token) {
            router.push("/login");
            return;
        }
        setIsAuthenticated(true);
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
            // Use defaults if API fails
            setMicrobes([
                { name: "saccharomyces_cerevisiae", display_name: "Saccharomyces Cerevisiae", optimal_temp: 30, optimal_ph: 5, max_yield: 45, description: "Baker's yeast" },
                { name: "escherichia_coli", display_name: "Escherichia Coli", optimal_temp: 37, optimal_ph: 7, max_yield: 35, description: "Common bacterium" },
                { name: "pichia_pastoris", display_name: "Pichia Pastoris", optimal_temp: 28, optimal_ph: 5.5, max_yield: 55, description: "Methylotrophic yeast" },
            ]);
            setSubstrates([
                { name: "glucose", display_name: "Glucose", energy: 15.6, description: "Common carbon source" },
                { name: "glycerol", display_name: "Glycerol", energy: 17.6, description: "Biodiesel byproduct" },
                { name: "sucrose", display_name: "Sucrose", energy: 16.5, description: "Table sugar" },
            ]);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;
        setFormData({
            ...formData,
            [name]: type === "number" ? parseFloat(value) : value,
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            const result = await experiments.run(formData);
            router.push(`/results?id=${result.experiment.id}`);
        } catch (err: any) {
            // More helpful error message
            if (err.message?.includes("token") || err.message?.includes("401") || err.message?.includes("Unauthorized")) {
                setError("Session expired. Please log in again.");
                setTimeout(() => router.push("/login"), 2000);
            } else {
                setError(err.message || "Simulation failed");
            }
            setLoading(false);
        }
    };

    const selectedMicrobe = microbes.find(m => m.name === formData.microbe_type);

    // Show loading while checking auth
    if (!isAuthenticated) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin text-4xl mb-4">🧬</div>
                    <p className="text-gray-400">Loading...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen p-8">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="flex items-center gap-4 mb-8">
                    <Link href="/dashboard" className="p-2 rounded-lg hover:bg-white/5 transition">
                        <ArrowLeft className="w-6 h-6" />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold">New Experiment</h1>
                        <p className="text-gray-400">Configure fermentation parameters and run simulation</p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-8">
                    {/* Experiment Name */}
                    <div className="card">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <Beaker className="w-5 h-5 text-green-400" />
                            Experiment Details
                        </h2>
                        <div>
                            <label htmlFor="name" className="label">Experiment Name</label>
                            <input
                                id="name"
                                name="name"
                                type="text"
                                value={formData.name}
                                onChange={handleChange}
                                className="input-field"
                                placeholder="e.g., Yeast Protein Trial #1"
                                required
                            />
                        </div>
                    </div>

                    {/* Microbe & Substrate */}
                    <div className="card">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <FlaskConical className="w-5 h-5 text-purple-400" />
                            Organism & Substrate
                        </h2>
                        <div className="grid md:grid-cols-2 gap-6">
                            <div>
                                <label htmlFor="microbe_type" className="label">Microorganism</label>
                                <select
                                    id="microbe_type"
                                    name="microbe_type"
                                    value={formData.microbe_type}
                                    onChange={handleChange}
                                    className="input-field"
                                >
                                    {microbes.map((m) => (
                                        <option key={m.name} value={m.name}>{m.display_name}</option>
                                    ))}
                                </select>
                                {selectedMicrobe && (
                                    <p className="text-xs text-gray-500 mt-2">
                                        Optimal: {selectedMicrobe.optimal_temp}°C, pH {selectedMicrobe.optimal_ph} • Max yield: {selectedMicrobe.max_yield} g/L
                                    </p>
                                )}
                            </div>
                            <div>
                                <label htmlFor="substrate" className="label">Carbon Source</label>
                                <select
                                    id="substrate"
                                    name="substrate"
                                    value={formData.substrate}
                                    onChange={handleChange}
                                    className="input-field"
                                >
                                    {substrates.map((s) => (
                                        <option key={s.name} value={s.name}>{s.display_name}</option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    </div>

                    {/* Process Parameters */}
                    <div className="card">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <ThermometerSun className="w-5 h-5 text-orange-400" />
                            Process Parameters
                        </h2>
                        <div className="grid md:grid-cols-2 gap-6">
                            <div>
                                <label htmlFor="temperature" className="label">Temperature (°C)</label>
                                <input
                                    id="temperature"
                                    name="temperature"
                                    type="number"
                                    value={formData.temperature}
                                    onChange={handleChange}
                                    className="input-field"
                                    min={15}
                                    max={60}
                                    step={0.5}
                                    required
                                />
                                <input
                                    type="range"
                                    min={15}
                                    max={60}
                                    step={0.5}
                                    value={formData.temperature}
                                    onChange={(e) => setFormData({ ...formData, temperature: parseFloat(e.target.value) })}
                                    className="w-full mt-2 accent-green-500"
                                />
                            </div>
                            <div>
                                <label htmlFor="ph" className="label">pH Level</label>
                                <input
                                    id="ph"
                                    name="ph"
                                    type="number"
                                    value={formData.ph}
                                    onChange={handleChange}
                                    className="input-field"
                                    min={3}
                                    max={10}
                                    step={0.1}
                                    required
                                />
                                <input
                                    type="range"
                                    min={3}
                                    max={10}
                                    step={0.1}
                                    value={formData.ph}
                                    onChange={(e) => setFormData({ ...formData, ph: parseFloat(e.target.value) })}
                                    className="w-full mt-2 accent-green-500"
                                />
                            </div>
                            <div>
                                <label htmlFor="duration" className="label flex items-center gap-2">
                                    <Clock className="w-4 h-4" /> Duration (hours)
                                </label>
                                <input
                                    id="duration"
                                    name="duration"
                                    type="number"
                                    value={formData.duration}
                                    onChange={handleChange}
                                    className="input-field"
                                    min={1}
                                    max={168}
                                    required
                                />
                            </div>
                            <div>
                                <label htmlFor="oxygen_level" className="label flex items-center gap-2">
                                    <Wind className="w-4 h-4" /> Oxygen Level (%)
                                </label>
                                <input
                                    id="oxygen_level"
                                    name="oxygen_level"
                                    type="number"
                                    value={formData.oxygen_level}
                                    onChange={handleChange}
                                    className="input-field"
                                    min={0}
                                    max={100}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Advanced Settings */}
                    <div className="card">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <Settings2 className="w-5 h-5 text-blue-400" />
                            Advanced Settings
                        </h2>
                        <div>
                            <label htmlFor="agitation_speed" className="label">Agitation Speed (RPM)</label>
                            <input
                                id="agitation_speed"
                                name="agitation_speed"
                                type="number"
                                value={formData.agitation_speed}
                                onChange={handleChange}
                                className="input-field max-w-xs"
                                min={0}
                                max={500}
                            />
                        </div>
                    </div>

                    {/* Error */}
                    {error && (
                        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400">
                            {error}
                        </div>
                    )}

                    {/* Submit */}
                    <div className="flex gap-4">
                        <Link href="/dashboard" className="btn-secondary px-8">
                            Cancel
                        </Link>
                        <button
                            type="submit"
                            disabled={loading}
                            className="btn-primary flex-1 flex items-center justify-center gap-2 disabled:opacity-50"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Running Simulation...
                                </>
                            ) : (
                                <>
                                    <Play className="w-5 h-5" />
                                    Run Simulation
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
