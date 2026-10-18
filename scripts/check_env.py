"""Week-1 smoke check: PostgreSQL schemas and Ollama models are reachable."""

import os
import sys

import httpx
import psycopg
from dotenv import load_dotenv

load_dotenv()

EXPECTED_SCHEMAS = {"raw", "staging", "marts", "ops"}


def check_postgres() -> bool:
    dsn = (
        f"host={os.getenv('POSTGRES_HOST', 'localhost')} "
        f"port={os.getenv('POSTGRES_PORT', '5433')} "
        f"dbname={os.getenv('POSTGRES_DB')} "
        f"user={os.getenv('POSTGRES_USER')} "
        f"password={os.getenv('POSTGRES_PASSWORD')}"
    )
    try:
        with psycopg.connect(dsn, connect_timeout=5) as conn:
            rows = conn.execute(
                "SELECT schema_name FROM information_schema.schemata"
            ).fetchall()
    except psycopg.OperationalError as exc:
        print(f"[KO] PostgreSQL : {exc}")
        return False
    missing = EXPECTED_SCHEMAS - {r[0] for r in rows}
    if missing:
        print(f"[KO] PostgreSQL : schémas manquants {sorted(missing)}")
        return False
    print("[OK] PostgreSQL : schémas raw/staging/marts/ops présents")
    return True


def check_ollama() -> bool:
    url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    try:
        models = httpx.get(f"{url}/api/tags", timeout=5).json().get("models", [])
    except httpx.HTTPError as exc:
        print(f"[KO] Ollama ({url}) : {exc}")
        return False
    names = {m["name"].split(":")[0] for m in models}
    ok = True
    for var in ("OLLAMA_CHAT_MODEL", "OLLAMA_EMBED_MODEL"):
        wanted = os.getenv(var, "").split(":")[0]
        if not wanted:
            print(f"[KO] Ollama : {var} vide dans .env")
            ok = False
        elif wanted not in names:
            print(f"[KO] Ollama : {wanted} non téléchargé (ollama pull {wanted})")
            ok = False
    if ok:
        print(f"[OK] Ollama : {len(models)} modèle(s) disponible(s)")
    return ok


if __name__ == "__main__":
    results = [check_postgres(), check_ollama()]
    sys.exit(0 if all(results) else 1)
