# Ticket Triage IA

Tri automatique de tickets de support IT : classification par catégorie, puis réponse
proposée à partir d'une base de connaissances. Le projet compare un modèle classique
(TF-IDF + régression logistique) et un LLM open source exécuté en local (Ollama).

> Projet personnel. Données publiques ou synthétiques uniquement : aucune donnée réelle
> d'entreprise ou de client.

## Architecture (cible)

```
jeu de données public ─┐
                       ├─► ingestion (Python) ─► PostgreSQL (raw)
tickets FR générés ────┘                              │
                                                       ▼
                                            dbt (staging → marts)
                                                       │
                     ┌─────────────────────────────────┼──────────────────────┐
                     ▼                                 ▼                      ▼
        baseline TF-IDF + LogReg          LLM local (Ollama)        RAG (embeddings)
                     └──────────────┬──────────────────┘                      │
                                    ▼                                         ▼
                         évaluation (F1, latence, taux de tri auto)   réponse proposée
                                    │
                                    ▼
                      API FastAPI ─► démo Streamlit ─► journal des prédictions (ops)
```

## Structure

| Dossier | Contenu | Semaine |
|---|---|---|
| `db/init/` | Schémas PostgreSQL créés au premier démarrage | 1 |
| `scripts/` | Utilitaires (vérification de l'environnement) | 1 |
| `ingestion/` | Chargement du jeu de données + génération de tickets FR | 2–3 |
| `dbt/` | Modèles dbt : `staging` (nettoyage) → `marts` (analyses) | 2–3 |
| `models/` | Baseline, classification LLM, évaluation | 4–6 |
| `rag/` | Base de connaissances, embeddings, réponse proposée | 7–8 |
| `api/` | API FastAPI | 9 |
| `app/` | Démo Streamlit | 9 |
| `tests/` | Tests (pytest), lancés par la CI | 10 |
| `docs/` | Plan (`plan.md`), journal de bord, fiche projet, bilan | tout du long |

Schémas PostgreSQL : `raw` (données brutes), `staging` et `marts` (dbt),
`ops` (journal des prédictions).

## Démarrage (semaine 1)

Prérequis : Docker Desktop, [uv](https://docs.astral.sh/uv/), [Ollama](https://ollama.com).

```powershell
# 1. Python via uv
winget install --id=astral-sh.uv -e
uv python install 3.12

# 2. Dépendances
uv sync

# 3. Base de données
copy .env.example .env
docker compose up -d

# 4. Modèles locaux, puis OLLAMA_CHAT_MODEL=ministral-3:8b dans .env
ollama pull ministral-3:8b
ollama pull qwen3.5:9b
ollama pull nomic-embed-text

# 5. Vérification
uv run python scripts/check_env.py
```

## Résultats

_À remplir au fil du projet (F1 par modèle, latence par ticket, taux de tri automatique)._

| Modèle | F1 macro | Latence / ticket | Tri auto (seuil) |
|---|---|---|---|
| TF-IDF + LogReg | | | |
| LLM local #1 | | | |
| LLM local #2 | | | |
