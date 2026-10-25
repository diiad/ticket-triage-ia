from pathlib import Path
import pandas as pd
from huggingface_hub import hf_hub_download
from ingestion.db import connect

REPO_ID = "Noise144/ticket_classification_IT_EN"
REVISION = "bcde65b6f193b660301270ebb313a01443029062"

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

def download() -> pd.DataFrame:
    """
        Télécharge le dataset de tickets depuis Hugging Face Hub et le charge en DataFrame.

        Récupère le fichier Excel 'Dataset_ticket.xlsx' depuis le dépôt spécifié,
        ajoute une colonne 'lang' (alternance italien/anglais) et une colonne 'source_row'
        pour tracer l'index d'origine.

        Returns:
            pd.DataFrame: DataFrame contenant les tickets avec les colonnes ajoutées.
        """
    path = hf_hub_download(
        repo_id=REPO_ID,
        filename="Dataset_ticket.xlsx",
        repo_type="dataset",
        revision=REVISION,
        local_dir=DATA_DIR,
    )
    df = pd.read_excel(path)
    df["lang"] = ["it" if i%100 < 50 else "en" for i in range(len(df))]
    df["source_row"] = df.index
    return df

DDL = """
CREATE TABLE IF NOT EXISTS raw.tickets_public (
    source_row   INTEGER PRIMARY KEY,
    category     TEXT NOT NULL,
    subcategory  TEXT NOT NULL,
    text         TEXT NOT NULL,
    lang         TEXT NOT NULL,
    loaded_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""

def load(df: pd.DataFrame) -> None:
    """
        Charge un DataFrame de tickets dans la table PostgreSQL raw.tickets_public.

        Crée la table si elle n'existe pas, la vide (TRUNCATE), puis insère les données
        via COPY pour des performances optimales.

        Args:
            df: DataFrame contenant les colonnes source_row, Category, Subcategory, Text et lang.
        """
    rows = df[["source_row", "Category", "Subcategory", "Text", "lang"]].itertuples(index=False)
    with connect() as conn:
        conn.execute(DDL)
        conn.execute("TRUNCATE raw.tickets_public")
        with conn.cursor().copy(
            "COPY raw.tickets_public (source_row, category, subcategory, text, lang) FROM STDIN"
        ) as copy:
            for row in rows:
                copy.write_row(row)
        n = conn.execute("SELECT count(*) FROM raw.tickets_public").fetchone()[0]
    print(f"raw.tickets_public : {n} lignes")


if __name__ == "__main__":
    load(download())