"""
Analyse des réponses au questionnaire d'évaluation (System Usability Scale
et Technology Acceptance Model) à partir d'un fichier Excel.

Format attendu du fichier Excel (une ligne par répondant) :
    - Colonnes SUS : sus_1 à sus_10 (notes de 1 à 5, questions impaires
      formulées positivement, questions paires formulées négativement,
      conformément au questionnaire SUS standard)
    - Colonnes TAM (optionnel) : tam_1, tam_2, ... (notes de 1 à 5)

Usage :
    python analyse_sus_tam.py chemin/vers/reponses.xlsx
"""

import sys
from pathlib import Path

import pandas as pd

SEUIL_UTILISABILITE = 68
SEUIL_EXCELLENCE = 80


def calculer_score_sus(row: pd.Series) -> float:
    """Calcule le score SUS (0-100) pour une ligne de réponses sus_1..sus_10."""
    total = 0
    for i in range(1, 11):
        note = row[f"sus_{i}"]
        if i % 2 == 1:  # questions impaires : positives
            total += note - 1
        else:  # questions paires : négatives
            total += 5 - note
    return total * 2.5


def interpreter_score(score: float) -> str:
    if score >= SEUIL_EXCELLENCE:
        return "Excellent"
    if score >= SEUIL_UTILISABILITE:
        return "Acceptable"
    return "Insuffisant"


def analyser(fichier_excel: str) -> None:
    df = pd.read_excel(fichier_excel)

    colonnes_sus = [f"sus_{i}" for i in range(1, 11)]
    manquantes = [c for c in colonnes_sus if c not in df.columns]
    if manquantes:
        raise ValueError(f"Colonnes SUS manquantes dans le fichier : {manquantes}")

    df["score_sus"] = df.apply(calculer_score_sus, axis=1)
    df["interpretation"] = df["score_sus"].apply(interpreter_score)

    print("=== Résultats individuels ===")
    print(df[["score_sus", "interpretation"]].to_string(index=False))

    print("\n=== Synthèse SUS ===")
    print(f"Score moyen        : {df['score_sus'].mean():.1f} / 100")
    print(f"Écart-type         : {df['score_sus'].std():.1f}")
    print(f"Score min / max    : {df['score_sus'].min():.1f} / {df['score_sus'].max():.1f}")
    print(f"Seuil utilisabilité (68) : {(df['score_sus'] >= SEUIL_UTILISABILITE).mean() * 100:.0f}% des répondants au-dessus")
    print(f"Seuil excellence (80)    : {(df['score_sus'] >= SEUIL_EXCELLENCE).mean() * 100:.0f}% des répondants au-dessus")

    colonnes_tam = [c for c in df.columns if c.startswith("tam_")]
    if colonnes_tam:
        print("\n=== Synthèse TAM (moyenne par item) ===")
        print(df[colonnes_tam].mean().round(2).to_string())

    chemin_sortie = Path(fichier_excel).with_name("resultats_sus_tam.xlsx")
    df.to_excel(chemin_sortie, index=False)
    print(f"\nRésultats détaillés enregistrés dans : {chemin_sortie}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage : python analyse_sus_tam.py chemin/vers/reponses.xlsx")
        sys.exit(1)
    analyser(sys.argv[1])
