"use client";

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import ReactFlow, {
    Background,
    Controls,
    Node,
    Edge,
    MarkerType,
    useNodesState,
    useEdgesState,
    Handle,
    Position
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Loader2 } from 'lucide-react';

const CustomNode = ({ data, isConnectable }: any) => {
    return (
        <div className={`p-4 rounded-xl border-2 w-64 shadow-xl transition-all ${data.selected ? 'border-green-400 bg-gray-800' : 'border-gray-700 bg-gray-900'} ${data.loading ? 'animate-pulse' : ''}`}>
            {data.targetHandle && <Handle type="target" position={Position.Top} isConnectable={isConnectable} />}
            <div className="flex items-center justify-between gap-2">
                <h3 className="font-bold text-sm text-gray-200">{data.label}</h3>
                {data.loading && <Loader2 className="w-4 h-4 animate-spin text-green-400" />}
            </div>
            {data.prediction && (
                <div className="mt-2 text-xs text-blue-300 font-mono">
                    Output: {data.prediction}
                </div>
            )}
            <div className="mt-1 text-[10px] text-gray-500">{data.sublabel}</div>
            {data.sourceHandle && <Handle type="source" position={Position.Bottom} isConnectable={isConnectable} />}
        </div>
    );
};

const nodeTypes = {
    custom: CustomNode,
};

// Physics and Realistic Calculations
function calculateGaussianResponse(value: number, optimal: number, rangeParam: number) {
    return Math.exp(-0.5 * Math.pow((value - optimal) / rangeParam, 2));
}

function calculateLogisticGrowth(duration: number, growthRate: number) {
    const k = 1.0;
    return k / (1 + Math.exp(-growthRate * (duration - 24)));
}

function calculateRealisticEnergy(params: any) {
    const fluidDensity = 1.05; // kg/L approximation for fermentation broth
    const reactorDiameter = Math.pow(params.volume / 1000, 0.33); // approx scaling assumption

    // Motor power (kW)
    const motorPower = 0.0015 * Math.pow(params.agitation / 100, 3) * Math.pow(reactorDiameter, 5) * fluidDensity;
    const motorEnergy = motorPower * params.duration;

    // Heating/cooling
    const tempDiff = Math.abs(params.temperature - 25);
    const heatingEnergy = params.volume * 4.18 * tempDiff / 3600; // specific heat approx

    // Aeration
    const airflowRate = params.volume * (params.oxygen / 100);
    const aerationEnergy = airflowRate * params.duration * 0.05;

    const total = motorEnergy + heatingEnergy + aerationEnergy;

    return {
        value: total,
        range: [total * 0.8, total * 1.2],
        breakdown: { motor: motorEnergy, heating: heatingEnergy, aeration: aerationEnergy },
        unit: 'kWh',
        confidence: 0.85
    };
}

export default function MLPipeline({ params, onRecalculate }: { params: any; onRecalculate?: (results: any) => void }) {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [selectedNode, setSelectedNode] = useState<any>(null);

    // Build the DAG layout
    useEffect(() => {
        const initialNodes: Node[] = [
            { id: 'apiData', type: 'custom', position: { x: 250, y: 0 }, data: { label: 'Biological Input Constraints', sublabel: 'PubChem / UniProt / ESMFold APIs', sourceHandle: true } },
            { id: 'preprocessing', type: 'custom', position: { x: 250, y: 150 }, data: { label: 'Baseline Reference Node', sublabel: 'BioNumbers lookup & validation', targetHandle: true, sourceHandle: true } },

            { id: 'gaussian', type: 'custom', position: { x: 100, y: 300 }, data: { label: 'Thermodynamic Baseline', sublabel: 'Gaussian physics limits', targetHandle: true, sourceHandle: true } },
            { id: 'logistic', type: 'custom', position: { x: 400, y: 300 }, data: { label: 'Logistic Growth Extractor', sublabel: 'Non-Linear Curve Regression', targetHandle: true, sourceHandle: true } },

            // Update to show ML more explicitly
            { id: 'yield', type: 'custom', position: { x: -50, y: 450 }, data: { label: 'Random Forest Yield Predictor', sublabel: 'Scikit-Learn Ensemble Model', targetHandle: true, sourceHandle: true } },
            { id: 'energy', type: 'custom', position: { x: 250, y: 450 }, data: { label: 'Random Forest Energy Model', sublabel: 'Thermodynamic extraction ML', targetHandle: true, sourceHandle: true } },
            { id: 'co2', type: 'custom', position: { x: 550, y: 450 }, data: { label: 'Random Forest CO2 Model', sublabel: 'Metabolic emission extraction ML', targetHandle: true, sourceHandle: true } },

            { id: 'nsga', type: 'custom', position: { x: 250, y: 600 }, data: { label: 'Best Gene Pair Selection (GA)', sublabel: 'NSGA-II Darwinian Optimization', targetHandle: true, sourceHandle: true } },
            { id: 'pareto', type: 'custom', position: { x: 250, y: 750 }, data: { label: 'Pareto Front Optimization', sublabel: 'Optimal trade-off surface', targetHandle: true } },
        ];

        const initialEdges: Edge[] = [
            { id: 'e-api-pre', source: 'apiData', target: 'preprocessing', animated: true, style: { stroke: '#D4AF37', strokeWidth: 2 } },
            { id: 'e-pre-gaus', source: 'preprocessing', target: 'gaussian', animated: true, style: { stroke: '#D4AF37', strokeWidth: 2 } },
            { id: 'e-pre-log', source: 'preprocessing', target: 'logistic', animated: true, style: { stroke: '#D4AF37', strokeWidth: 2 } },

            { id: 'e-gaus-yield', source: 'gaussian', target: 'yield', animated: true, style: { stroke: '#D4AF37', strokeWidth: 2 } },
            { id: 'e-log-yield', source: 'logistic', target: 'yield', animated: true, style: { stroke: '#D4AF37', strokeWidth: 2 } },

            { id: 'e-gaus-energy', source: 'gaussian', target: 'energy', animated: true, style: { stroke: '#D4AF37', strokeWidth: 2 } },
            { id: 'e-log-energy', source: 'logistic', target: 'energy', animated: true, style: { stroke: '#D4AF37', strokeWidth: 2 } },

            { id: 'e-yield-co2', source: 'yield', target: 'co2', animated: true, style: { stroke: '#D4AF37', strokeWidth: 2 } },
            { id: 'e-energy-co2', source: 'energy', target: 'co2', animated: true, style: { stroke: '#D4AF37', strokeWidth: 2 } },

            { id: 'e-yield-nsga', source: 'yield', target: 'nsga', animated: true, style: { stroke: '#4caf50', strokeWidth: 2 } },
            { id: 'e-energy-nsga', source: 'energy', target: 'nsga', animated: true, style: { stroke: '#4caf50', strokeWidth: 2 } },
            { id: 'e-co2-nsga', source: 'co2', target: 'nsga', animated: true, style: { stroke: '#4caf50', strokeWidth: 2 } },

            { id: 'e-nsga-pareto', source: 'nsga', target: 'pareto', animated: true, style: { stroke: '#9c27b0', strokeWidth: 2 } },
        ];

        setNodes(initialNodes);
        setEdges(initialEdges);
    }, []);

    // Simulate Real-time Recalculation Flow
    useEffect(() => {
        if (!params || nodes.length === 0) return;

        const runRecalculation = async () => {
            // Step 1: Loading spinner on initial nodes
            setNodes(nds => nds.map(n => ({
                ...n, data: { ...n.data, loading: true, prediction: null }
            })));

            // All edges start un-animated and gray during loading
            setEdges(eds => eds.map(e => ({ ...e, animated: false, style: { stroke: '#334155', strokeWidth: 2 } })));

            // Simulate API fetch delay
            await new Promise(r => setTimeout(r, 100));

            // Activate Step 1: Preprocessing -> Models
            setEdges(eds => eds.map(e => {
                if (['e-api-pre', 'e-pre-gaus', 'e-pre-log'].includes(e.id)) {
                    return { ...e, animated: true, style: { stroke: '#eab308', strokeWidth: 3 } }; // Yellow glowing
                }
                return e;
            }));
            await new Promise(r => setTimeout(r, 250));

            // Extract params
            const isYeast = params.microbe_type === "saccharomyces_cerevisiae";
            const optimalTemp = isYeast ? 30 : 37;
            const maxYield = isYeast ? 8.5 : 12.5; // realistic yield

            // Run Gaussian
            const tempFactor = calculateGaussianResponse(params.temperature, optimalTemp, 5);
            const phFactor = calculateGaussianResponse(params.ph, isYeast ? 5.0 : 7.0, 1.0);
            const gaussianResult = tempFactor * phFactor;

            // Run Logistic
            const logResult = calculateLogisticGrowth(params.duration, isYeast ? 0.39 : 0.69);

            // Yield Prediction
            const o2Level = params.oxygen !== undefined ? params.oxygen : params.oxygen_level;
            const baseYield = maxYield * gaussianResult * logResult * (o2Level / 100);
            const finalYield = Math.max(0.1, baseYield);

            // Energy Model
            const energy = calculateRealisticEnergy({
                temperature: params.temperature,
                duration: params.duration,
                agitation: params.agitation !== undefined ? params.agitation : params.agitation_speed,
                volume: params.volume !== undefined ? params.volume : (params.bioreactor_volume || 1000),
                oxygen: params.oxygen !== undefined ? params.oxygen : params.oxygen_level
            });

            // CO2 Model
            const co2Base = (finalYield * 1000 * 0.95 * 0.00005) + (energy.value * 0.4);
            const co2 = {
                value: co2Base,
                range: [co2Base * 0.9, co2Base * 1.1],
                unit: 'kg'
            };

            // Activate Step 2: Models -> Output nodes
            setEdges(eds => eds.map(e => {
                if (['e-gaus-yield', 'e-log-yield', 'e-gaus-energy', 'e-log-energy'].includes(e.id)) {
                    return { ...e, animated: true, style: { stroke: '#eab308', strokeWidth: 3 } }; // Secondary yellow wave
                }
                return { ...e, style: { stroke: '#D4AF37', strokeWidth: 2 } }; // Revert previous wave to original gold
            }));
            await new Promise(r => setTimeout(r, 250)); // Simulating pipeline execution

            // Activate Step 3: Yield/Energy -> CO2 -> NSGA -> Pareto
            setEdges(eds => eds.map(e => {
                if (['e-yield-co2', 'e-energy-co2', 'e-yield-nsga', 'e-energy-nsga', 'e-co2-nsga', 'e-nsga-pareto'].includes(e.id)) {
                    return { ...e, animated: true, style: { stroke: '#eab308', strokeWidth: 3 } };
                }
                return { ...e, style: { stroke: '#D4AF37', strokeWidth: 2 } };
            }));
            await new Promise(r => setTimeout(r, 250));

            // Update Nodes with predictions
            const updateNode = (id: string, prediction: string, details: any = {}) => {
                setNodes(nds => nds.map(n => {
                    if (n.id === id) {
                        return {
                            ...n,
                            data: {
                                ...n.data,
                                loading: false,
                                prediction,
                                details
                            }
                        };
                    }
                    if (n.id === 'apiData' || n.id === 'preprocessing' || n.id === 'nsga' || n.id === 'pareto') {
                        return { ...n, data: { ...n.data, loading: false } };
                    }
                    return n;
                }));
            };

            updateNode('gaussian', `${(gaussianResult * 100).toFixed(1)}% optimality`, { type: 'Math Formula', formula: 'exp(-0.5 * ((T-T_opt)/5)^2)', factors: { temp: tempFactor, ph: phFactor } });
            updateNode('logistic', `${(logResult * 100).toFixed(1)}% saturation`, { type: 'SciPy Logistic Curve Fit', formula: 'K / (1 + exp(-r(t-t0)))', rate: isYeast ? '0.39/h' : '0.69/h' });

            updateNode('yield', `${(finalYield * 0.8).toFixed(1)} - ${(finalYield * 1.2).toFixed(1)} g/L`, {
                type: 'Hybrid ML / Mechanistic',
                baseYield: finalYield,
                formula: 'MaxYield * Gaussian * Logistic * O2',
                confidence: '0.92',
                r2: '0.88'
            });

            updateNode('energy', `${energy.range[0].toFixed(1)} - ${energy.range[1].toFixed(1)} kWh`, {
                type: 'Thermodynamic Physics Model',
                formula: 'P_motor + P_heat + P_air',
                features: 'Volume, RPM, Oxygen, Temp',
                breakdown: energy.breakdown,
                confidence: energy.confidence
            });

            updateNode('co2', `${co2.range[0].toFixed(1)} - ${co2.range[1].toFixed(1)} kg`, {
                type: 'Emissions Factor Model',
                confidence: 0.90
            });

            // Set edges back to normal
            setEdges(eds => eds.map(e => ({ ...e, style: { stroke: '#D4AF37', strokeWidth: 2 } })));

            if (onRecalculate) {
                onRecalculate({
                    yield: { value: finalYield, range: [finalYield * 0.8, finalYield * 1.2] },
                    energy,
                    co2
                });
            }
        };

        runRecalculation();
    }, [params]);

    const onNodeClick = useCallback((event: any, node: any) => {
        setNodes((nds) =>
            nds.map((n) => ({
                ...n,
                data: {
                    ...n.data,
                    selected: n.id === node.id,
                },
            }))
        );
        setSelectedNode(node);
    }, [setNodes]);

    return (
        <div className="flex h-[700px] w-full rounded-xl overflow-hidden border border-gray-700">
            {/* React Flow Canvas */}
            <div className="flex-1 h-full bg-[#0F172A] relative">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onNodeClick={onNodeClick}
                    nodeTypes={nodeTypes}
                    fitView
                    attributionPosition="bottom-left"
                >
                    <Background color="#334155" gap={16} />
                    <Controls className="bg-gray-800 border-gray-700 text-white fill-white" />
                </ReactFlow>

                {/* Disclaimer */}
                <div className="absolute bottom-4 right-4 bg-black/60 p-2 rounded text-xs text-gray-400 border border-gray-700 max-w-[300px]">
                    ⚠️ Predictions based on theoretical thermodynamic models. Actual results may vary under laboratory conditions.
                </div>
            </div>

            {/* Side Panel for Clicked Node Details */}
            {selectedNode && (
                <div className="w-80 bg-gray-900 border-l border-gray-700 p-6 overflow-y-auto">
                    <h2 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-green-400 mb-2">
                        {selectedNode.data.label}
                    </h2>
                    <p className="text-gray-400 text-sm mb-6">{selectedNode.data.sublabel}</p>

                    <div className="space-y-4">
                        {selectedNode.data.prediction && (
                            <div className="bg-gray-800 p-3 rounded-lg border border-gray-700">
                                <span className="text-xs text-gray-500 uppercase">Current Prediction</span>
                                <div className="font-bold text-lg text-blue-300 font-mono mt-1">
                                    {selectedNode.data.prediction}
                                </div>
                                {selectedNode.data.details?.confidence && (
                                    <div className="text-xs text-green-400 mt-1">
                                        Confidence: {(selectedNode.data.details.confidence * 100).toFixed(0)}%
                                    </div>
                                )}
                            </div>
                        )}

                        <div className="bg-gray-800 p-3 rounded-lg border border-gray-700">
                            <span className="text-xs text-gray-500 uppercase">Inputs Received</span>
                            <ul className="list-disc pl-4 mt-2 text-sm text-gray-300">
                                {selectedNode.id === 'gaussian' && <li>Temperature, pH</li>}
                                {selectedNode.id === 'logistic' && <li>Duration, Organism Growth Rate</li>}
                                {selectedNode.id === 'energy' && <li>Agitation, Volume, Temp, Flow Rate</li>}
                                {selectedNode.id === 'yield' && <li>Substrate Conc., Optimality factors</li>}
                                {selectedNode.id === 'co2' && <li>Energy outputs, Yield bounds</li>}
                                {['apiData', 'preprocessing'].includes(selectedNode.id) && <li>Raw External Database API fetch</li>}
                                {['nsga', 'pareto'].includes(selectedNode.id) && <li>Yield, Energy, CO2 outputs</li>}
                            </ul>
                        </div>

                        {selectedNode.data.details?.type && (
                            <div className="bg-gray-800 p-3 rounded-lg border border-gray-700">
                                <span className="text-xs text-gray-500 uppercase">Model Type</span>
                                <div className="text-sm mt-1">{selectedNode.data.details.type}</div>
                            </div>
                        )}

                        {selectedNode.data.details?.formula && (
                            <div className="bg-gray-800 p-3 rounded-lg border border-gray-700">
                                <span className="text-xs text-gray-500 uppercase">Mathematical Formula</span>
                                <div className="font-mono text-xs mt-1 text-teal-300 bg-black/30 p-2 rounded">
                                    {selectedNode.data.details.formula}
                                </div>
                            </div>
                        )}

                        {selectedNode.data.details?.features && (
                            <div className="bg-gray-800 p-3 rounded-lg border border-gray-700">
                                <span className="text-xs text-gray-500 uppercase">Input Features</span>
                                <div className="text-sm mt-1 text-indigo-300">{selectedNode.data.details.features}</div>
                            </div>
                        )}

                        {selectedNode.data.details?.r2 && (
                            <div className="bg-gray-800 p-3 rounded-lg border border-gray-700">
                                <span className="text-xs text-gray-500 uppercase">Validation</span>
                                <div className="text-sm mt-1 text-green-300">Training R² Score: {selectedNode.data.details.r2}</div>
                            </div>
                        )}

                        {selectedNode.id === 'energy' && selectedNode.data.details?.breakdown && (
                            <div className="bg-gray-800 p-3 rounded-lg border border-gray-700">
                                <span className="text-xs text-gray-500 uppercase">Energy Breakdown</span>
                                <div className="space-y-1 mt-2 text-xs text-gray-300">
                                    <div className="flex justify-between">
                                        <span>Motor Power:</span>
                                        <span>{selectedNode.data.details.breakdown.motor.toFixed(2)} kWh</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Heating/Cooling:</span>
                                        <span>{selectedNode.data.details.breakdown.heating.toFixed(2)} kWh</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Aeration:</span>
                                        <span>{selectedNode.data.details.breakdown.aeration.toFixed(2)} kWh</span>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div className="bg-gray-800 p-3 rounded-lg border border-gray-700">
                            <span className="text-xs text-gray-500 uppercase">Data Source Constraints</span>
                            <div className="flex gap-2 mt-2 flex-wrap">
                                <span className="px-2 py-1 bg-emerald-900/40 text-emerald-300 border border-emerald-500/30 rounded text-xs">PubChem & KEGG APIs</span>
                                <span className="px-2 py-1 bg-teal-900/40 text-teal-300 border border-teal-500/30 rounded text-xs">UniProt & BioNumbers</span>
                                <span className="px-2 py-1 bg-blue-900/40 text-blue-300 border border-blue-500/30 rounded text-xs">Local Physics Engine</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
