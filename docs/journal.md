# Journal de bord

Une entrée par séance : ce que j'ai fait, ce qui a bloqué, la décision prise et pourquoi.
C'est la matière première du bilan final et des réponses d'entretien
(« un problème difficile », « un choix technique que tu as dû faire »).

| Date | Durée | Fait | Blocage / décision |
|---|---|---|---|
| 2026-10-18 | | Semaine 1 : structure du dépôt, PostgreSQL 16 sous Docker (schémas raw/staging/marts/ops), Python via uv, Ollama avec ministral-3:8b, qwen3.5:9b et nomic-embed-text. `check_env.py` : PostgreSQL et Ollama OK. | `ollama pull <modele>` refusé par PowerShell (`<` est un opérateur) : remplacer le texte d'exemple par un vrai nom de modèle. Choix de deux LLM de 8–9B pour tenir dans les 8 Go de VRAM de la RTX 4060 et pouvoir les comparer. |
