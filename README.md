# FermaGen AI 🧬

**AI-powered fermentation simulation and optimization platform for sustainable alternative protein R&D.**

> ⚠️ **Note:** This platform simulates and optimizes fermentation processes. It does NOT create new protein molecules or replace animal proteins directly. See [PROJECT_CLARIFICATION.txt](PROJECT_CLARIFICATION.txt) for details.

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Next.js](https://img.shields.io/badge/next.js-14+-black)
![PostgreSQL](https://img.shields.io/badge/postgresql-16+-336791)

## 🚀 Features

- **Fermentation Simulation** - ML-powered predictions for yield, energy, and CO₂
- **Multi-Objective Optimization** - Genetic algorithm to maximize yield while minimizing time & carbon
- **Protein Analysis** - BioPython-based sequence analysis with molecular weight, pI, stability
- **AI Explanations** - Perplexity API integration for scientific insights
- **Sustainability Scoring** - Real-time eco-impact metrics
- **Firebase Authentication** - Google Sign-In with OAuth 2.0
- **External API Integrations** - UniProt, KEGG, PubChem, Open Food Facts
- **Modern Dashboard** - Beautiful dark-themed UI with glassmorphism

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Next.js 14    │────▶│    FastAPI       │────▶│  PostgreSQL     │
│   (Vercel)      │     │  (Render/Docker) │     │   Database      │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
        │                        │
        │ Firebase Auth          │
        ▼                        ▼
┌─────────────────┐     ┌─────────────────────────────────────────┐
│  Google OAuth   │     │           External APIs                 │
└─────────────────┘     │  UniProt │ KEGG │ PubChem │ Food Facts  │
                        └─────────────────────────────────────────┘
```

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
PERPLEXITY_API_KEY=your-api-key
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

## � Authentication

### Firebase Google Sign-In
Users can sign in with their Google account via Firebase. The frontend handles the OAuth flow and sends the Firebase token to the backend for verification.

### Email/Password
Traditional email/password registration is also supported with bcrypt hashing and JWT tokens.

## �🐳 Docker Deployment

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
5. Add environment variables (DATABASE_URL, PERPLEXITY_API_KEY, SECRET_KEY)

## 🔑 API Endpoints

### Core APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | User registration |
| POST | `/auth/login` | User login (JWT) |
| POST | `/auth/firebase` | Firebase Google auth |
| GET | `/auth/profile` | Get user profile |
| POST | `/experiment/run` | Run simulation |
| GET | `/experiment/{id}` | Get experiment |
| GET | `/experiment/` | List experiments |
| POST | `/protein/analyze` | Analyze protein sequence |
| POST | `/ai/optimize` | Multi-objective optimization |
| POST | `/ai/explain` | Generate AI explanation |
| POST | `/ai/quick-simulate` | Quick simulation (no auth) |

### External APIs (New!)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/external/uniprot/search?query=` | Search UniProt proteins |
| GET | `/external/uniprot/protein/{accession}` | Get protein details |
| GET | `/external/kegg/pathways?query=` | Search KEGG pathways |
| GET | `/external/kegg/pathway/{id}` | Get pathway details |
| GET | `/external/pubchem/search?name=` | Search PubChem compounds |
| GET | `/external/pubchem/compound/{cid}` | Get compound details |
| GET | `/external/nutrition/search?query=` | Search nutrition data |
| GET | `/external/substrate/{name}` | Get substrate info |
| GET | `/external/microbe/{organism}/pathways` | Get microbe pathways |

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

## 📊 ML Models

| Model | Purpose |
|-------|---------|
| Gaussian Response | Temperature/pH optimum curves |
| Logistic Growth | Microbial growth saturation |
| Genetic Algorithm | Multi-objective optimization |
| Rule-based + Perplexity | AI explanations |

## 🌱 Sustainability Features

- CO₂ footprint estimation per experiment
- Energy usage tracking
- Sustainability scoring (0-100)
- Eco-optimization recommendations

## 📁 Project Structure

```
fermagen-ai/
├── backend/
│   ├── app/
│   │   ├── auth/          # JWT + Firebase authentication
│   │   ├── experiments/   # Simulation engine
│   │   ├── protein/       # Protein analysis
│   │   ├── ai/            # Optimization & explanations
│   │   ├── database/      # SQLAlchemy + PostgreSQL
│   │   ├── external_apis.py   # UniProt, KEGG, PubChem clients
│   │   └── external_routes.py # External API endpoints
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js pages
│   │   ├── lib/
│   │   │   ├── api.ts     # API client
│   │   │   └── firebase.ts # Firebase config
│   │   └── components/    # UI components
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
- Uses UniProt, KEGG, PubChem APIs for scientific data
- Firebase for secure authentication
- Designed for researchers, scientists, and students

---

**Made with 💚 for a sustainable future**
