import json
import os
import random
import httpx

from ingestion.db import connect

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_CHAT_MODEL", "ministral-3:8b")
PROMPT_VERSION = "v2"

PER_SUBCATEGORY = 50
BATCH = 5

SUBCATEGORIES = {
    "Hardware": ["CPU", "Disk", "Keyboard", "Memory", "Monitor", "Mouse"],
    "Network": ["DHCP", "DNS", "IP Address", "VPN", "Wireless"],
    "Database": ["DB2", "MS SQL Server", "Oracle"],
    "Inquiry/Help": ["Antivirus", "Internal Application"],
    "Software": ["Email", "Operating System"],
}
ANGLES = [
    "un utilisateur pressé qui écrit court",
    "un utilisateur débutant qui décrit les symptômes sans jargon",
    "un technicien qui donne des détails précis",
    "un manager dont l'équipe est bloquée",
    "un utilisateur qui pose une question plutôt qu'il ne signale une panne",
]

DDL = """
CREATE TABLE IF NOT EXISTS raw.tickets_generated (
    id                     BIGSERIAL PRIMARY KEY,
    requested_category     TEXT NOT NULL,
    requested_subcategory  TEXT NOT NULL,
    text                   TEXT NOT NULL,
    lang                   TEXT NOT NULL DEFAULT 'fr',
    angle                  TEXT NOT NULL,
    model                  TEXT NOT NULL,
    prompt_version         TEXT NOT NULL,
    generated_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""

SCHEMA = {
    "type": "object",
    "properties": {
        "tickets": {
            "type": "array",
            # One object per ticket with a length range stops the model from
            # splitting a ticket into fragments.
            "items": {
                "type": "object",
                "properties": {"texte": {"type": "string", "minLength": 40, "maxLength": 500}},
                "required": ["texte"],
            },
            "minItems": BATCH,
            "maxItems": BATCH,
        }
    },
    "required": ["tickets"],
}

def prompt(category: str, subcategory: str, angle: str) ->str:
    """
        Construit le prompt pour la génération de tickets synthétiques.

        Args:
            category: Catégorie principale du ticket.
            subcategory: Sous-catégorie du ticket.
            angle: Angle ou perspective à appliquer au prompt.

        Returns:
            Chaîne de caractères formatée prête à être envoyée au modèle de génération.
        """
    return (
        f"Écris {BATCH} tickets de support informatique différents, en français, "
        f"tels qu'un employé les enverrait au service IT. "
        f"Sujet : {category} > {subcategory}. Auteur : {angle}.\n"
        "Règles :\n"
        "- chaque ticket fait 1 à 3 phrases, en texte brut ;\n"
        "- pas de titre, pas de numéro, pas de markdown, pas de date, pas de priorité ;\n"
        f"- n'écris jamais le mot « {subcategory} » ni le nom de la catégorie ;\n"
        "- aucun nom de personne, e-mail ou téléphone.\n"
        'Réponds en JSON : {"tickets": [{"texte": "..."}, ...]}'
    )

def generate(category: str, subcategory: str, angle: str) -> list[str]:
    """
        Génère une liste de textes de tickets à partir des critères spécifiés.

        Args:
            category: Catégorie principale du ticket.
            subcategory: Sous-catégorie du ticket.
            angle: Angle ou perspective à utiliser pour la génération.

        Returns:
            Liste de textes de tickets générés.
        """
    resp = httpx.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt(category, subcategory, angle)}],
            "format": SCHEMA,
            "stream": False,
            "think":False,
            "options": {"temperature": 0.9, "num_predict": 1000},
        },
        timeout=120,
    )
    resp.raise_for_status()
    reponse_ollama = resp.json()
    texte_du_modele = reponse_ollama["message"]["content"]
    donnees = json.loads(texte_du_modele)
    tickets = donnees["tickets"]
    return [t["texte"].strip() for t in tickets if t["texte"].strip()]

def main() -> None:
    with connect() as conn:
        conn.execute(DDL)
        conn.commit()
        for category, subs in SUBCATEGORIES.items():
            for sub in subs:
                done = conn.execute(
                    "SELECT count(*) FROM raw.tickets_generated WHERE requested_subcategory = %s",
                    (sub,)
                ).fetchone()[0]
                while done < PER_SUBCATEGORY:
                    angle = random.choice(ANGLES)
                    try:
                        tickets = generate(category, sub, angle)[: PER_SUBCATEGORY - done]
                    except (httpx.TimeoutException, httpx.HTTPStatusError, json.JSONDecodeError) as exc:
                        print(f"  appel raté ({type(exc).__name__}), on réessaie")
                        continue
                    with conn.cursor() as cur:
                        cur.executemany(
                            "INSERT INTO raw.tickets_generated (requested_category,"
                            " requested_subcategory, text, angle, model, prompt_version)"
                            " VALUES (%s, %s, %s, %s, %s, %s)",
                            [(category, sub, t, angle, MODEL, PROMPT_VERSION) for t in tickets],
                        )
                    conn.commit()
                    done += len(tickets)
                print(f"{category} > {sub} : {done}")

if __name__ == "__main__":
    main()