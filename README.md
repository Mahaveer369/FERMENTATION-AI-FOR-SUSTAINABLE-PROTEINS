# FermaGen AI 🧬

**AI-powered fermentation simulation and optimization platform for sustainable alternative protein R&D.**

> ⚠️ **Note:** This platform simulates and optimizes fermentation processes using ML models. It does NOT create new protein molecules or replace animal proteins directly.

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Next.js](https://img.shields.io/badge/next.js-14+-black)
![PostgreSQL](https://img.shields.io/badge/postgresql-16+-336791)

## 🚀 Features

- **Real-time Data Pipeline** - Live API integration for substrate, protein, and structure data
- **Fermentation Simulation** - ML-powered predictions for yield, energy, and CO₂
- **Multi-Objective Optimization** - Genetic algorithm + Pareto front analysis
- **Protein Structure Prediction** - NVIDIA ESMFold for 3D protein structures
- **Protein Analysis** - BioPython-based sequence analysis with molecular weight, pI, stability
- **AI Explanations** - Perplexity API integration for scientific insights
- **Sustainability Scoring** - Real-time eco-impact metrics with trade-off analysis
- **Firebase Authentication** - Google Sign-In with OAuth 2.0
- **Modern Dashboard** - Beautiful dark-themed UI with React Flow pipeline visualization

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Next.js 14    │────▶│    FastAPI       │────▶│  PostgreSQL     │
│   (Frontend)    │     │  (Backend)       │     │   Database      │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
        │                        │
        │ Firebase Auth         │
        ▼                        ▼
┌─────────────────┐     ┌─────────────────────────────────────────┐
│  Google OAuth   │     │         External APIs (Real-time)       │
└─────────────────┘     │  PubChem │ UniProt │ KEGG │ NVIDIA ESM  │
                         └─────────────────────────────────────────┘
```

## 📡 Real-time External APIs

The platform integrates with multiple scientific APIs to fetch real-time data for fermentation simulations:

### 🔬 PubChem API
**Base:** `https://pubchem.ncbi.nlm.nih.gov/rest/pug`

Fetches molecular properties for fermentation substrates:
- Molecular formula and weight
- Compound CID (PubChem Identifier)
- Chemical synonyms

### 🧬 UniProt API
**Base:** `https://rest.uniprot.org`

Protein data retrieval:
- Protein sequence search by query
- FASTA sequence retrieval by accession
- Organism and annotation data

### 🧪 KEGG API
**Base:** `https://rest.kegg.jp`

Metabolic pathway data:
- Pathway search and details
- Compound ID lookup
- Microbe metabolic pathway mapping

### 🏛️ NVIDIA ESMFold API
**Base:** `https://health.api.nvidia.com/v1/biology/meta/esmfold`

AI-powered protein structure prediction:
- 3D structure prediction from sequence
- pLDDT confidence scores
- PDB format output

### 📊 BioNumbers Database
**Source:** Built-in curated constants

Published biological parameters:
- Growth rates for microorganisms
- Optimal temperature/pH ranges
- ATP yield and energy constants

## 📦 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (20+ recommended)
- PostgreSQL 14+
- npm or yarn

### 1. Clone & Setup

```bash
cd "AI for sustainable proteins"

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install --legacy-peer-deps
```

### 2. Configure Environment

```bash
# Backend - Copy and edit
cp backend/.env.example backend/.env

# Required variables:
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@127.0.0.1:5432/fermagen
NVIDIA_API_KEY=your-nvidia-api-key
PERPLEXITY_API_KEY=your-perplexity-key
SECRET_KEY=your-secret-key
```

### 3. Setup PostgreSQL Database

```bash
# Create database
psql -U postgres -c "CREATE DATABASE fermagen;"
```

### 4. Run Development Servers

**Backend (Terminal 1):**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```

### 5. Access the App

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 🔐 Authentication

### Firebase Google Sign-In
Users can sign in with their Google account via Firebase. The frontend handles the OAuth flow and sends the Firebase token to the backend for verification.

### Email/Password
Traditional email/password registration is also supported with bcrypt hashing and JWT tokens.

## 🐳 Docker Deployment

```bash
# Build and run both services
docker-compose up -d

# View logs
docker-compose logs -f
```

## 🌐 Production Deployment

### Frontend → Vercel

1. Push to GitHub
2. Connect repo to Vercel
3. Set environment variable: `NEXT_PUBLIC_API_URL=https://your-backend.onrender.com`
4. Deploy

### Backend → Render

1. Create new Web Service on Render
2. Connect GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (DATABASE_URL, NVIDIA_API_KEY, PERPLEXITY_API_KEY, SECRET_KEY)

## 🔑 API Endpoints

### Authentication (`/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | User registration |
| POST | `/auth/login` | User login (JWT) |
| POST | `/auth/firebase` | Firebase Google auth |
| GET | `/auth/profile` | Get user profile |
| PUT | `/auth/profile` | Update user profile |

### Experiments (`/experiment`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/experiment/run` | Run fermentation simulation |
| GET | `/experiment/{id}` | Get experiment by ID |
| GET | `/experiment/` | List experiments (paginated) |
| DELETE | `/experiment/{id}` | Delete experiment |
| GET | `/experiment/food-types` | List food type categories |
| GET | `/experiment/microbes/by-food/{food_type}` | Get microbes for food type |
| GET | `/experiment/substrates/by-food/{food_type}` | Get substrates for food type |
| GET | `/experiment/protein-suggestions/{food_type}` | KEGG/UniProt protein suggestions |

### Protein Analysis (`/protein`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/protein/analyze` | Analyze protein sequence |
| GET | `/protein/amino-acids` | List amino acids with properties |

### AI Optimization (`/ai`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ai/optimize` | Multi-objective parameter optimization |
| POST | `/ai/explain` | Generate AI explanation |
| POST | `/ai/quick-simulate` | Quick simulation (no auth) |
| GET | `/ai/sustainability-tips` | Get sustainability tips |

### Real-time External APIs (`/realtime`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/realtime/substrate/{name}` | Get PubChem substrate data |
| GET | `/realtime/protein/search` | Search UniProt proteins |
| GET | `/realtime/protein/sequence/{accession}` | Get protein FASTA sequence |
| POST | `/realtime/structure/predict` | NVIDIA ESMFold structure prediction |
| POST | `/realtime/pipeline` | Full fermentation pipeline |
| GET | `/realtime/verify` | Health check all external APIs |

### Static External APIs (`/external`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/external/uniprot/search?query=` | Search UniProt proteins |
| GET | `/external/uniprot/protein/{accession}` | Get UniProt protein details |
| GET | `/external/kegg/pathways?query=` | Search KEGG pathways |
| GET | `/external/kegg/pathway/{id}` | Get pathway details |
| GET | `/external/pubchem/search?name=` | Search PubChem compounds |
| GET | `/external/pubchem/compound/{cid}` | Get compound details |
| GET | `/external/nutrition/search?query=` | Search nutrition data |
| GET | `/external/substrate/{name}` | Get substrate info |
| GET | `/external/microbe/{organism}/pathways` | Get microbe pathways |

## 📊 ML Models

| Model | Purpose | Implementation |
|-------|---------|----------------|
| Yield Predictor | Predict yield (g/L), energy (kWh), CO₂ | Random Forest (50 estimators) |
| Gaussian Response | Temperature/pH optimum curves | Gaussian Process (RBF kernel) |
| Logistic Growth | Microbial growth saturation | SciPy curve_fit |
| Genetic Optimizer | Global hyperparameter optimization | NSGA-II evolutionary algorithm |
| Pareto Optimization | Multi-objective trade-off analysis | Non-dominated sorting |
| Explainer | Human-readable explanations | Perplexity API (fallback: rule-based) |

## 🧪 Supported Microorganisms

- **Saccharomyces cerevisiae** (Baker's yeast)
- **Escherichia coli**
- **Pichia pastoris**
- **Aspergillus niger**
- **Bacillus subtilis**

## 🔬 Supported Substrates

- Glucose, Sucrose, Maltose
- Glycerol, Methanol
- Lactose, Starch

## 🌱 Sustainability Features

- CO₂ footprint estimation per experiment
- Energy usage tracking
- Sustainability scoring (0-100)
- Eco-optimization recommendations
- Pareto trade-off visualization

## 📁 Project Structure

```
fermagen-ai/
├── backend/
│   ├── app/
│   │   ├── auth/              # JWT + Firebase authentication
│   │   ├── experiments/       # Simulation engine & routes
│   │   ├── protein/           # Protein analysis
│   │   ├── ai/               # ML models (optimization, explanation)
│   │   ├── database/          # SQLAlchemy + PostgreSQL
│   │   ├── realtime_pipeline.py   # Real-time API integration
│   │   ├── external_apis.py   # PubChem, UniProt, KEGG, NVIDIA clients
│   │   └── external_routes.py # External API endpoints
│   ├── ml_models/
│   │   ├── yield_predictor.py       # Random Forest predictor
│   │   ├── gaussian_response.py     # Gaussian Process
│   │   ├── logistic_growth.py        # Growth curves
│   │   ├── genetic_optimizer.py      # GA optimization
│   │   └── pareto_optimization.py   # Pareto front analysis
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js 14 pages
│   │   │   ├── experiment/   # Experiment page
│   │   │   ├── results/     # Results dashboard
│   │   │   ├── realtime/    # Real-time API runner
│   │   │   └── optimize/    # Optimization page
│   │   ├── lib/
│   │   │   ├── api.ts       # API client
│   │   │   └── firebase.ts  # Firebase config
│   │   └── components/
│   │       └── MLPipeline.tsx  # React Flow pipeline visualization
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built for sustainable alternative protein R&D
- Uses PubChem, UniProt, KEGG APIs for real-time scientific data
- NVIDIA ESMFold for protein structure prediction
- Firebase for secure authentication
- Designed for researchers, scientists, and students

---

**Made with 💚 for a sustainable future**