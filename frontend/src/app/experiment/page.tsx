"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
    Beaker, ArrowLeft, Play, Loader2, ThermometerSun,
    Clock, FlaskConical, Wind, Settings2, Leaf, ChevronDown, ChevronRight, Info, Sparkles, Droplets, Star, Activity
} from "lucide-react";
import { experiments } from "@/lib/api";

interface FoodType {
    name: string;
    display_name: string;
    description: string;
    icon: string;
    related_microbes: string[];
    related_substrates: string[];
}

interface Microbe {
    name: string;
    display_name: string;
    optimal_temp: number;
    optimal_ph: number;
    max_yield: number;
    description: string;
    role?: string;
    food_types?: string[];
}

interface Substrate {
    name: string;
    display_name: string;
    energy: number;
    description: string;
    food_types?: string[];
}

export default function ExperimentPage() {
    const router = useRouter();
    const [foodTypes, setFoodTypes] = useState<FoodType[]>([]);
    const [microbes, setMicrobes] = useState<Microbe[]>([]);
    const [substrates, setSubstrates] = useState<Substrate[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [selectedFoodType, setSelectedFoodType] = useState<string>("");
    const [loadingSelection, setLoadingSelection] = useState(false);
    const [showFallbackNotice, setShowFallbackNotice] = useState(false);
    const abortControllerRef = useRef<AbortController | null>(null);
    const [proteinSuggestions, setProteinSuggestions] = useState<any[]>([]);
    const [loadingProteins, setLoadingProteins] = useState(false);

    const [formData, setFormData] = useState({
        name: "",
        microbe_type: "saccharomyces_cerevisiae",
        substrate: "glucose",
        temperature: 30,
        ph: 5.5,
        duration: 48,
        oxygen_level: 21,
        agitation_speed: 200,
        use_realtime_data: false,
        protein_name: "",
        organism: "",
        predict_structure: false,
    });

    // Handle URL parameters for pre-filling form (from optimization suggestions)
    useEffect(() => {
        const searchParams = new URLSearchParams(window.location.search);
        const microbe = searchParams.get('microbe');
        const substrate = searchParams.get('substrate');
        const temp = searchParams.get('temp');
        const ph = searchParams.get('ph');
        const duration = searchParams.get('duration');
        const agitation = searchParams.get('agitation');
        const oxygen = searchParams.get('oxygen');

        if (microbe || substrate || temp || ph) {
            // Pre-fill form data from URL params
            setFormData(prev => ({
                ...prev,
                ...(microbe && { microbe_type: microbe }),
                ...(substrate && { substrate }),
                ...(temp && { temperature: parseFloat(temp) }),
                ...(ph && { ph: parseFloat(ph) }),
                ...(duration && { duration: parseFloat(duration) }),
                ...(agitation && { agitation_speed: parseFloat(agitation) }),
                ...(oxygen && { oxygen_level: parseFloat(oxygen) }),
            }));
        }
    }, []);

    useEffect(() => {
        // Check authentication
        const token = localStorage.getItem("token");
        if (!token) {
            router.push("/login");
            return;
        }
        setIsAuthenticated(true);
        loadFoodTypes();
    }, [router]);

    const loadFoodTypes = async () => {
        try {
            const foodData = await experiments.getFoodTypes();
            setFoodTypes(foodData);
            if (foodData.length > 0) {
                setSelectedFoodType(foodData[0].name);
            }
        } catch (err) {
            // Use defaults if API fails
            setFoodTypes([
                { name: "milk_products", display_name: "Milk & Dairy Products", description: "Milk, cheese, yogurt", icon: "🥛", related_microbes: [], related_substrates: [] },
                { name: "bread_grains", display_name: "Bread & Grains", description: "Wheat, rice, maize", icon: "🍞", related_microbes: [], related_substrates: [] },
                { name: "legumes", display_name: "Legumes & Pulses", description: "Soybean, lentils", icon: "🫘", related_microbes: [], related_substrates: [] },
            ]);
            setSelectedFoodType("milk_products");
        }
    };

    const loadMicrobesAndSubstrates = useCallback(async (foodType: string) => {
        // Cancel any pending request
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
        }
        abortControllerRef.current = new AbortController();

        setLoadingSelection(true);
        setShowFallbackNotice(false);
        try {
            const [microbeData, substrateData] = await Promise.all([
                experiments.getMicrobesByFood(foodType),
                experiments.getSubstratesByFood(foodType),
            ]);
            setMicrobes(microbeData);
            setSubstrates(substrateData);

            // Set default selections
            if (microbeData.length > 0) {
                setFormData(prev => ({ ...prev, microbe_type: microbeData[0].name }));
            }
            if (substrateData.length > 0) {
                setFormData(prev => ({ ...prev, substrate: substrateData[0].name }));
            }
        } catch (err: any) {
            // Ignore abort errors
            if (err.name === 'AbortError' || err.name === 'CanceledError') {
                return;
            }
            // Show fallback notice to user
            setShowFallbackNotice(true);
            // Use defaults if API fails
            setMicrobes([
                { name: "lactobacillus_casei", display_name: "Lactobacillus casei", optimal_temp: 30, optimal_ph: 5.5, max_yield: 22, description: "Probiotic bacterium", role: "Enhances protein digestion" },
            ]);
            setSubstrates([
                { name: "lactose", display_name: "Lactose", energy: 16.5, description: "Milk sugar" },
            ]);
        }
        setLoadingSelection(false);
    }, []);

    useEffect(() => {
        if (selectedFoodType) {
            loadMicrobesAndSubstrates(selectedFoodType);
        }
    }, [selectedFoodType, loadMicrobesAndSubstrates]);

    // Load protein suggestions whenever food type changes
    useEffect(() => {
        if (selectedFoodType) {
            setLoadingProteins(true);
            experiments.getProteinSuggestions(selectedFoodType)
                .then((data: any[]) => {
                    setProteinSuggestions(data);
                    // Auto-select first suggestion
                    if (data.length > 0) {
                        setFormData(prev => ({
                            ...prev,
                            protein_name: data[0].protein_name,
                            organism: data[0].organism,
                        }));
                    }
                })
                .catch(() => setProteinSuggestions([]))
                .finally(() => setLoadingProteins(false));
        }
    }, [selectedFoodType]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;
        const checked = (e.target as HTMLInputElement).checked;

        setFormData({
            ...formData,
            [name]: type === "checkbox" ? checked : type === "number" ? parseFloat(value) : value,
        });
    };

    const handleFoodTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedFoodType(e.target.value);
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
    const selectedFood = foodTypes.find(f => f.name === selectedFoodType);

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
            <div className="max-w-6xl mx-auto">
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

                    {/* Food Type Selection - Multi-Level Selection */}
                    <div className="card bg-gradient-to-br from-green-900/30 to-emerald-900/20 border border-green-500/30">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <Leaf className="w-5 h-5 text-green-400" />
                            Select Food Type
                            <span className="text-xs font-normal text-gray-400 ml-2">
                                (Microbes and substrates will be filtered based on your selection)
                            </span>
                        </h2>

                        <div className="mb-6">
                            <label htmlFor="food_type" className="label">Food Category</label>
                            <select
                                id="food_type"
                                name="food_type"
                                value={selectedFoodType}
                                onChange={handleFoodTypeChange}
                                className="input-field"
                            >
                                {foodTypes.map((ft) => (
                                    <option key={ft.name} value={ft.name}>
                                        {ft.icon} {ft.display_name}
                                    </option>
                                ))}
                            </select>
                            {selectedFood && (
                                <p className="text-sm text-gray-400 mt-2 flex items-center gap-2">
                                    <Info className="w-4 h-4" />
                                    {selectedFood.description}
                                </p>
                            )}
                        </div>

                        {/* Fallback Notice */}
                        {showFallbackNotice && (
                            <div className="mb-4 p-3 bg-yellow-900/30 border border-yellow-500/30 rounded-lg">
                                <p className="text-sm text-yellow-400 flex items-center gap-2">
                                    <Info className="w-4 h-4" />
                                    Could not load data from server. Showing default options.
                                </p>
                            </div>
                        )}

                        {/* Multi-Level Display */}
                        {loadingSelection ? (
                            <div className="flex items-center justify-center py-8">
                                <Loader2 className="w-6 h-6 animate-spin text-green-400" />
                                <span className="ml-2 text-gray-400">Loading compatible microbes & substrates...</span>
                            </div>
                        ) : (
                            <div className="grid md:grid-cols-2 gap-6">
                                {/* Microbes Column */}
                                <div className="space-y-3">
                                    <h3 className="font-medium text-purple-400 flex items-center gap-2">
                                        <ChevronRight className="w-4 h-4" />
                                        Recommended Microorganisms
                                    </h3>
                                    <div className="space-y-2 max-h-64 overflow-y-auto pr-2">
                                        {microbes.map((microbe) => (
                                            <div
                                                key={microbe.name}
                                                onClick={() => setFormData({
                                                    ...formData,
                                                    microbe_type: microbe.name,
                                                    temperature: microbe.optimal_temp || formData.temperature,
                                                    ph: microbe.optimal_ph || formData.ph
                                                })}
                                                className={`p-3 rounded-lg border cursor-pointer transition-all duration-200 ${formData.microbe_type === microbe.name
                                                    ? "bg-purple-500/20 border-purple-500/50 shadow-lg shadow-purple-500/20"
                                                    : "bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20"
                                                    }`}
                                            >
                                                <div className="flex items-center justify-between">
                                                    <span className="font-medium text-sm">{microbe.display_name}</span>
                                                    <div className="flex gap-1">
                                                        {selectedFoodType && (
                                                            <span className="text-xs bg-green-500/20 text-green-400 px-1.5 py-0.5 rounded flex items-center gap-1">
                                                                <Star className="w-3 h-3" /> Recommended
                                                            </span>
                                                        )}
                                                        {formData.microbe_type === microbe.name && (
                                                            <span className="text-xs bg-purple-500/30 px-2 py-0.5 rounded">Selected</span>
                                                        )}
                                                    </div>
                                                </div>
                                                <p className="text-xs text-gray-400 mt-1">{microbe.role || microbe.description}</p>
                                                <div className="flex gap-3 mt-2 text-xs text-gray-500">
                                                    <span>🌡️ {microbe.optimal_temp}°C</span>
                                                    <span>pH {microbe.optimal_ph}</span>
                                                    <span>📈 {microbe.max_yield} g/L</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Substrates Column */}
                                <div className="space-y-3">
                                    <h3 className="font-medium text-blue-400 flex items-center gap-2">
                                        <ChevronRight className="w-4 h-4" />
                                        Compatible Substrates
                                    </h3>
                                    <div className="space-y-2 max-h-64 overflow-y-auto pr-2">
                                        {substrates.map((substrate) => (
                                            <div
                                                key={substrate.name}
                                                onClick={() => setFormData({ ...formData, substrate: substrate.name })}
                                                className={`p-3 rounded-lg border cursor-pointer transition-all duration-200 ${formData.substrate === substrate.name
                                                    ? "bg-blue-500/20 border-blue-500/50 shadow-lg shadow-blue-500/20"
                                                    : "bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20"
                                                    }`}
                                            >
                                                <div className="flex items-center justify-between">
                                                    <span className="font-medium text-sm">{substrate.display_name}</span>
                                                    <div className="flex gap-1">
                                                        {selectedFoodType && (
                                                            <span className="text-xs bg-green-500/20 text-green-400 px-1.5 py-0.5 rounded flex items-center gap-1">
                                                                <Star className="w-3 h-3" /> Recommended
                                                            </span>
                                                        )}
                                                        {formData.substrate === substrate.name && (
                                                            <span className="text-xs bg-blue-500/30 px-2 py-0.5 rounded">Selected</span>
                                                        )}
                                                    </div>
                                                </div>
                                                <p className="text-xs text-gray-400 mt-1">{substrate.description}</p>
                                                <div className="flex gap-3 mt-2 text-xs text-gray-500">
                                                    <span>⚡ {substrate.energy} kJ/g</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Recommended Parameters for Selected Microbe */}
                    {selectedMicrobe && (
                        <div className="card bg-gradient-to-r from-purple-900/20 to-blue-900/20 border border-purple-500/30 animate-fade-in">
                            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                <Sparkles className="w-5 h-5 text-purple-400" />
                                Recommended Parameters for {selectedMicrobe.display_name}
                            </h2>
                            <p className="text-sm text-gray-400 mb-4">
                                Based on the selected microorganism, these are the optimal parameters for maximum yield:
                            </p>
                            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                                <div
                                    onClick={() => setFormData({ ...formData, temperature: selectedMicrobe.optimal_temp })}
                                    className="p-3 rounded-lg bg-orange-500/10 border border-orange-500/30 cursor-pointer hover:bg-orange-500/20 transition-all duration-300 hover:scale-105 group"
                                >
                                    <div className="flex items-center gap-2 mb-1">
                                        <ThermometerSun className="w-4 h-4 text-orange-400" />
                                        <span className="text-xs text-gray-400">Temperature</span>
                                    </div>
                                    <div className="text-lg font-bold text-orange-400 group-hover:scale-110 transition-transform">{selectedMicrobe.optimal_temp}°C</div>
                                    <div className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                                        <Settings2 className="w-3 h-3" /> Click to apply
                                    </div>
                                </div>
                                <div
                                    onClick={() => setFormData({ ...formData, ph: selectedMicrobe.optimal_ph })}
                                    className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/30 cursor-pointer hover:bg-blue-500/20 transition-all duration-300 hover:scale-105 group"
                                >
                                    <div className="flex items-center gap-2 mb-1">
                                        <Droplets className="w-4 h-4 text-blue-400" />
                                        <span className="text-xs text-gray-400">pH Level</span>
                                    </div>
                                    <div className="text-lg font-bold text-blue-400 group-hover:scale-110 transition-transform">{selectedMicrobe.optimal_ph}</div>
                                    <div className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                                        <Settings2 className="w-3 h-3" /> Click to apply
                                    </div>
                                </div>
                                <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/30">
                                    <div className="flex items-center gap-2 mb-1">
                                        <Clock className="w-4 h-4 text-green-400" />
                                        <span className="text-xs text-gray-400">Duration</span>
                                    </div>
                                    <div className="text-lg font-bold text-green-400">48h</div>
                                    <div className="text-xs text-gray-500 mt-1">Suggested</div>
                                </div>
                                <div className="p-3 rounded-lg bg-cyan-500/10 border border-cyan-500/30">
                                    <div className="flex items-center gap-2 mb-1">
                                        <Wind className="w-4 h-4 text-cyan-400" />
                                        <span className="text-xs text-gray-400">Oxygen</span>
                                    </div>
                                    <div className="text-lg font-bold text-cyan-400">40%</div>
                                    <div className="text-xs text-gray-500 mt-1">Suggested</div>
                                </div>
                                <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                                    <div className="flex items-center gap-2 mb-1">
                                        <Beaker className="w-4 h-4 text-yellow-400" />
                                        <span className="text-xs text-gray-400">Max Yield</span>
                                    </div>
                                    <div className="text-lg font-bold text-yellow-400">{selectedMicrobe.max_yield} g/L</div>
                                    <div className="text-xs text-gray-500 mt-1">Potential</div>
                                </div>
                            </div>
                        </div>
                    )}

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
                                {selectedMicrobe && (
                                    <p className="text-xs text-gray-500 mt-2">
                                        Optimal for {selectedMicrobe.display_name}: {selectedMicrobe.optimal_temp}°C
                                    </p>
                                )}
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
                                {selectedMicrobe && (
                                    <p className="text-xs text-gray-500 mt-2">
                                        Optimal for {selectedMicrobe.display_name}: pH {selectedMicrobe.optimal_ph}
                                    </p>
                                )}
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

                    {/* Real-Time API Integration Section */}
                    <div className="card border-green-500/30">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 text-green-400">
                            <Activity className="w-5 h-5" />
                            Live Scientific Data Integration
                        </h2>
                        <div className="flex flex-col gap-4">
                            <div className="flex items-center gap-3">
                                <input
                                    type="checkbox"
                                    id="use_realtime_data"
                                    name="use_realtime_data"
                                    checked={formData.use_realtime_data}
                                    onChange={handleChange}
                                    className="w-5 h-5 rounded border-gray-600 bg-gray-700 text-green-500 focus:ring-green-500"
                                />
                                <label htmlFor="use_realtime_data" className="font-medium text-gray-200">
                                    Fetch live attributes from PubChem, UniProt, KEGG, BioNumbers &amp; ESMFold
                                </label>
                            </div>

                            {formData.use_realtime_data && (
                                <div className="pl-4 space-y-4 pt-2 border-l-2 border-green-700/40 animate-in fade-in slide-in-from-top-2">
                                    {/* Protein Suggestion Cards */}
                                    <div>
                                        <label className="label text-sm text-green-300 flex items-center gap-2 mb-2">
                                            <Sparkles className="w-4 h-4" />
                                            Suggested Proteins for {foodTypes.find(f => f.name === selectedFoodType)?.display_name || selectedFoodType}
                                        </label>
                                        {loadingProteins ? (
                                            <div className="flex items-center gap-2 text-gray-400 text-sm py-4">
                                                <Loader2 className="w-4 h-4 animate-spin" />
                                                Loading protein suggestions from API...
                                            </div>
                                        ) : proteinSuggestions.length > 0 ? (
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                                {proteinSuggestions.map((s: any, idx: number) => (
                                                    <button
                                                        key={idx}
                                                        type="button"
                                                        onClick={() => setFormData(prev => ({
                                                            ...prev,
                                                            protein_name: s.protein_name,
                                                            organism: s.organism,
                                                        }))}
                                                        className={`text-left p-3 rounded-lg border transition-all ${formData.protein_name === s.protein_name && formData.organism === s.organism
                                                                ? 'border-green-500/60 bg-green-900/30 ring-1 ring-green-500/30'
                                                                : 'border-gray-700/60 bg-black/20 hover:border-green-500/30 hover:bg-green-900/10'
                                                            }`}
                                                    >
                                                        <div className="font-semibold text-sm text-gray-200">{s.protein_name}</div>
                                                        <div className="text-xs text-green-400 italic">{s.organism}</div>
                                                        <div className="text-xs text-gray-500 mt-1 line-clamp-2">{s.description}</div>
                                                        {s.kegg_pathway && (
                                                            <div className="text-xs text-teal-500 mt-1">🗺️ {s.kegg_pathway}</div>
                                                        )}
                                                    </button>
                                                ))}
                                            </div>
                                        ) : (
                                            <p className="text-xs text-gray-500">No suggestions — use custom inputs below.</p>
                                        )}
                                    </div>

                                    {/* Custom override inputs */}
                                    <div className="border-t border-gray-800 pt-3">
                                        <p className="text-xs text-gray-500 mb-2">Or enter custom protein details:</p>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                            <div>
                                                <label htmlFor="protein_name" className="label text-xs text-gray-400">Protein Name</label>
                                                <input
                                                    id="protein_name"
                                                    name="protein_name"
                                                    type="text"
                                                    value={formData.protein_name}
                                                    onChange={handleChange}
                                                    required={formData.use_realtime_data}
                                                    className="input-field bg-black/20 text-sm"
                                                    placeholder="e.g., Beta-lactoglobulin"
                                                />
                                            </div>
                                            <div>
                                                <label htmlFor="organism" className="label text-xs text-gray-400">Source Organism</label>
                                                <input
                                                    id="organism"
                                                    name="organism"
                                                    type="text"
                                                    value={formData.organism}
                                                    onChange={handleChange}
                                                    className="input-field bg-black/20 text-sm"
                                                    placeholder="e.g., Bos taurus"
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-2">
                                        <input
                                            type="checkbox"
                                            id="predict_structure"
                                            name="predict_structure"
                                            checked={formData.predict_structure}
                                            onChange={handleChange}
                                            className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-purple-500 focus:ring-purple-500"
                                        />
                                        <label htmlFor="predict_structure" className="text-sm text-gray-300">
                                            Run deep 3D structural prediction (adds 30-60s to simulation time)
                                        </label>
                                    </div>
                                </div>
                            )}
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
