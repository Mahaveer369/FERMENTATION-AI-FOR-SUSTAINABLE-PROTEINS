# FermaGen AI - System Documentation

> **AI-powered fermentation simulation and optimization platform for sustainable alternative protein R&D**

---

## 📌 Executive Summary

FermaGen AI is a machine learning-powered platform that **simulates and optimizes microbial fermentation processes** for alternative protein production. It helps researchers and food technologists make data-driven decisions about sustainable protein production by predicting yield, energy consumption, and environmental impact.

### What This System Does

| Feature | Description |
|---------|-------------|
| **Fermentation Simulation** | Predicts yield, energy, and CO₂ using ML models |
| **Parameter Optimization** | Uses genetic algorithms to find optimal conditions |
| **Protein Analysis** | Analyzes existing protein sequences |
| **Sustainability Scoring** | Provides eco-impact metrics (0-100 score) |

### What This System Does NOT Do

- ❌ Create new protein molecules or amino acid sequences
- ❌ Replace animal proteins directly
- ❌ Manufacture or synthesize proteins
- ❌ Evaluate plant-based protein alternatives (focuses on fermentation)
- ❌ Compare against animal protein benchmarks

---

## 🔬 Core Functionality

### 1. Fermentation Simulation Engine

The simulation engine uses scientifically-grounded ML models to predict fermentation outcomes.

**Input Parameters:**
- Microorganism type (yeast, bacteria, fungi)
- Substrate (carbon source)
- Temperature (°C)
- pH level
- Duration (hours)
- Oxygen level (%)
- Agitation speed (RPM)

**Output Predictions:**
- Predicted yield (g/L)
- Energy usage (kWh)
- CO₂ footprint (kg)
- Protein quality score (0-100)
- Purity percentage
- Efficiency percentage
- Sustainability score (0-100)
- Model confidence (0-1)

**Scientific Models Used:**
| Model | Purpose |
|-------|---------|
| Gaussian Response | Temperature/pH optimum curves |
| Logistic Growth | Microbial growth saturation |
| Linear/Non-linear | Energy and CO₂ calculations |

### 2. Multi-Objective Optimizer

Uses genetic algorithms to find optimal fermentation parameters.

**Optimization Objectives:**
1. Maximize yield
2. Minimize duration (time)
3. Minimize CO₂ footprint

**Algorithm Features:**
- Population-based search (50 individuals)
- 30 generations of evolution
- Crossover and mutation operators
- Pareto front extraction
- Weighted compromise solution selection

**Output:**
- Optimal parameters
- Pareto-optimal solutions (trade-off analysis)
- Improvement over baseline
- Actionable recommendations

### 3. Protein Sequence Analyzer

Analyzes existing protein sequences using BioPython-inspired calculations.

**Analyses Performed:**
- Molecular weight (Daltons)
- Isoelectric point (pI)
- Amino acid composition
- Hydrophobicity (GRAVY score)
- Instability index
- Aromaticity
- Net charge at pH 7
- Secondary structure tendency

---

## 🧬 Supported Organisms & Substrates

### Microorganisms

| Organism | Optimal Temp | Optimal pH | Max Yield |
|----------|-------------|------------|-----------|
| Saccharomyces cerevisiae | 30°C | 5.0 | 45 g/L |
| Escherichia coli | 37°C | 7.0 | 35 g/L |
| Pichia pastoris | 28°C | 5.5 | 55 g/L |
| Aspergillus niger | 30°C | 4.5 | 40 g/L |
| Bacillus subtilis | 37°C | 7.0 | 30 g/L |

### Substrates

| Substrate | Energy (kJ/g) | Conversion Factor | CO₂ Factor |
|-----------|--------------|------------------|------------|
| Glucose | 15.6 | 0.50 | 0.95 |
| Sucrose | 16.5 | 0.48 | 0.92 |
| Glycerol | 17.6 | 0.55 | 0.75 |
| Methanol | 22.7 | 0.40 | 1.10 |
| Starch | 17.0 | 0.35 | 0.82 |

---

## 📊 Sustainability Metrics

### Sustainability Score Calculation

The sustainability score (0-100) is calculated from three components:

1. **Yield Score (30% weight):** Higher yield = better score
2. **Energy Efficiency (35% weight):** Lower kWh per gram = better
3. **CO₂ Efficiency (35% weight):** Lower kg CO₂ per gram = better

### CO₂ Footprint Components

1. **Metabolic CO₂:** Direct emissions from fermentation
2. **Energy CO₂:** Emissions from power consumption (0.4 kg CO₂/kWh)
3. **Processing CO₂:** Overhead from downstream processing

---

## 🔌 API Endpoints

### Core Simulation APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/experiment/run` | Run fermentation simulation |
| GET | `/experiment/{id}` | Get experiment results |
| GET | `/experiment/` | List all experiments |
| POST | `/ai/optimize` | Run multi-objective optimization |
| POST | `/ai/explain` | Generate AI explanation |
| POST | `/ai/quick-simulate` | Quick simulation (no auth) |
| POST | `/protein/analyze` | Analyze protein sequence |

### External Data APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/external/uniprot/search` | Search UniProt proteins |
| GET | `/external/kegg/pathways` | Search KEGG pathways |
| GET | `/external/pubchem/search` | Search PubChem compounds |
| GET | `/external/nutrition/search` | Search nutrition data |

---

## 🏗️ Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Next.js 14    │────▶│    FastAPI       │────▶│  PostgreSQL     │
│   Frontend      │     │    Backend       │     │   Database      │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
          ┌─────────────────┐       ┌─────────────────┐
          │   ML Models     │       │  External APIs  │
          │ - Simulation    │       │ - UniProt       │
          │ - Optimization  │       │ - KEGG          │
          │ - Analysis      │       │ - PubChem       │
          └─────────────────┘       └─────────────────┘
```

---

## 👥 Target Users

1. **Researchers** - Studying fermentation processes
2. **Food Technologists** - Developing alternative proteins
3. **Students** - Learning about sustainable food production
4. **Process Engineers** - Optimizing fermentation conditions

---

## 📝 Accurate Project Positioning

### ✅ Recommended Description

> "FermaGen AI is an ML-powered platform that simulates and optimizes microbial fermentation processes for alternative protein production. It predicts yield, energy consumption, and CO₂ footprint while recommending optimal conditions for sustainable fermentation."

### ⚠️ Avoid These Claims

- "Creates new proteins" → Use "optimizes protein production"
- "Replaces animal proteins" → Use "supports alternative protein R&D"
- "Tests plant-based alternatives" → Use "simulates fermentation-based production"

---

## 📅 Document Information

- **Created:** January 21, 2026
- **Project:** FermaGen AI
- **Version:** 1.0
