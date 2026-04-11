# FermaGen AI — Docker Commands Cheat Sheet

## Start the NEW API-Integrated Version
```bash
cd ~/Desktop/"AI for sustainable proteins"
docker compose -f docker-compose.api-integrated.yml up -d --build
```

## Stop the API-Integrated Version
```bash
docker compose -f docker-compose.api-integrated.yml down
```

## Switch Back to PREVIOUS (Baseline) Version
```bash
docker compose -f docker-compose.api-integrated.yml down
docker compose -f docker-compose.yml up -d --build
```

## Switch Back to API-Integrated Version
```bash
docker compose -f docker-compose.yml down
docker compose -f docker-compose.api-integrated.yml up -d --build
```

## Access Points
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
