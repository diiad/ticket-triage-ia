# Plan du projet

**Objectif :** démontrer, avec un projet complet et mesuré, les compétences attendues pour une
alternance Data / ML / MLOps : pipeline de données (dbt), modèle classique vs LLM, RAG, API,
CI/CD, suivi en production.

**Rythme :** ~6 h par semaine, 12 semaines, du 18 octobre 2026 à mi-janvier 2027
(avant l'ouverture des campagnes d'alternance 2027).

**Règle :** données publiques ou générées uniquement. Aucune donnée réelle d'entreprise ou de
client. Le projet s'inspire d'une expérience de support applicatif, il n'a jamais été déployé
chez un client.

## Environnement

| Élément | Choix |
|---|---|
| Base de données | PostgreSQL 16 sous Docker, port 5433, schémas `raw` / `staging` / `marts` / `ops` |
| Python | 3.12 via uv |
| LLM local (Ollama) | `ministral-3:8b` (principal), `qwen3.5:9b` (comparaison) |
| Embeddings (Ollama) | `nomic-embed-text` |
| Matériel de référence | RTX 4060 8 Go VRAM, 16 Go RAM |

Sur un nouveau PC : suivre « Démarrage » dans le README, puis
`ollama pull ministral-3:8b`, `ollama pull qwen3.5:9b`, `ollama pull nomic-embed-text`,
et renseigner `OLLAMA_CHAT_MODEL` dans `.env`.

## Semaines

| Semaines | Étape | Fin visée | Statut |
|---|---|---|---|
| 1 | Dépôt, Docker Compose + PostgreSQL, uv, modèles Ollama, `check_env.py` | 25 oct. 2026 | ✅ 18 oct. |
| 2–3 | Données : ingestion du jeu public dans `raw`, génération de tickets FR, modèles dbt | 8 nov. | |
| 4 | Baseline TF-IDF + régression logistique, premières mesures de F1 | 15 nov. | |
| 5–6 | Classification par LLM local (2 modèles), comparaison chiffrée avec la baseline | 29 nov. | |
| 7–8 | RAG : réponse proposée à partir d'une base de connaissances | 13 déc. | |
| 9 | API FastAPI + démo Streamlit | 20 déc. | |
| 10 | CI GitHub Actions, tests, journal des prédictions (`ops.predictions`) | 3 janv. 2027 | |
| 11–12 | README final (architecture, résultats), vidéo de démo de 2 min, bilan | 17 janv. 2027 | |

Déploiement cloud (ex. GCP Cloud Run) : hors plan principal, car un LLM local ne se déploie
pas facilement. Option si avance en janvier : déployer l'API avec la baseline seulement.

## Notes par étape

### Semaines 2–3 : données
- **Jeu public :** [Noise144/ticket_classification_IT_EN](https://huggingface.co/datasets/Noise144/ticket_classification_IT_EN)
  (~1 800 tickets IT en anglais, 18 catégories, généré par GPT-3.5). **Aucune licence déclarée** :
  usage local uniquement, ne jamais versionner ni republier ces données (`data/` est ignoré par Git).
- **Tickets FR générés** avec `ministral-3:8b`, sur les mêmes catégories : ce sont tes propres
  données, publiables librement.
  - Garder dans une colonne la catégorie *demandée* au modèle : c'est l'étiquette de vérité.
  - Contrôler à la main un échantillon de ~50 tickets générés et noter le taux d'erreur.
- **dbt :** `staging` (nettoyage, normalisation des catégories, union des deux sources) →
  `marts` (répartition par catégorie et par source).

### Semaines 4–6 : modèles
- Mesures pour chaque modèle : F1 macro et par catégorie, latence par ticket (sur la RTX 4060),
  taux de tri automatique au-dessus d'un seuil de confiance.
- Point de comparaison : un article récent rapporte un F1 de 38 à 55 % pour les modèles de type
  BERT sur des tickets ITSM réels ([arXiv 2512.17916](https://arxiv.org/html/2512.17916v1)).
  Expliquer pourquoi les scores sur données synthétiques sont plus hauts.
- Si un modèle « réfléchit » longuement avant de répondre (mode raisonnement), le désactiver ou
  changer de modèle : trop lent pour des centaines de tickets.

### Semaines 11–12 : livrables d'entretien
1. Fiche d'une page : problème, architecture, résultats, plan d'évaluation.
2. Démo : vidéo de 2 minutes.
3. Bilan : ce qui a marché, ce qui n'a pas marché, ce que je ferais autrement
   (s'appuyer sur `docs/journal.md`).
