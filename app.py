"""
Plateforme Web-SIG - Susceptibilité aux inondations à Abomey-Calavi
Auteur : (à compléter)
"""

import json
import io
import zipfile
from pathlib import Path

import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd

# ----------------------------------------------------------------------
# Configuration générale
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Susceptibilité aux inondations - Abomey-Calavi",
    layout="wide",
)

DATA_PATH = Path(__file__).parent / "data" / "arrondissements.geojson"

COULEURS_RISQUE = {
    "Faible": "#2ecc71",
    "Moyen": "#f1c40f",
    "Élevé": "#e67e22",
    "Très élevé": "#e74c3c",
}

PRECAUTIONS = {
    "Faible": (
        "Surveiller les bulletins météo en saison pluvieuse. "
        "Maintenir les caniveaux et exutoires d'eau dégagés."
    ),
    "Moyen": (
        "Éviter les constructions en zone basse. Prévoir des dispositifs "
        "de drainage individuels. Suivre les alertes de la mairie."
    ),
    "Élevé": (
        "Renforcer les systèmes de drainage collectifs. Préparer un plan "
        "familial d'évacuation. Éviter tout stockage de biens au sol."
    ),
    "Très élevé": (
        "Envisager une évacuation préventive en cas d'alerte. Ne pas "
        "construire de nouveaux bâtiments d'habitation. Se conformer en "
        "priorité aux consignes des autorités locales."
    ),
}

# ----------------------------------------------------------------------
# Chargement des données
# ----------------------------------------------------------------------
@st.cache_data
def charger_donnees(path: Path) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(path)
    gdf["lat_centre"] = gdf.geometry.centroid.y.round(5)
    gdf["lon_centre"] = gdf.geometry.centroid.x.round(5)
    return gdf


gdf = charger_donnees(DATA_PATH)
liste_arrondissements = sorted(gdf["nom"].unique().tolist())

# ----------------------------------------------------------------------
# Barre latérale : contrôles utilisateur
# ----------------------------------------------------------------------
st.sidebar.title("Paramètres")

st.sidebar.subheader("Horizon temporel de la susceptibilité")
afficher_2025 = st.sidebar.checkbox("Actuelle (2025)", value=True)
afficher_2040 = st.sidebar.checkbox("Projetée (2040)", value=False)

if not afficher_2025 and not afficher_2040:
    st.sidebar.warning("Sélectionne au moins un horizon (2025 ou 2040).")
    afficher_2025 = True

st.sidebar.subheader("Filtre par arrondissement")
options_arrondissement = ["Tous les arrondissements"] + liste_arrondissements
choix_arrondissement = st.sidebar.selectbox(
    "Choisir un arrondissement", options_arrondissement
)

st.sidebar.markdown("---")
st.sidebar.subheader("Export des couches")
format_export = st.sidebar.radio("Format d'export", ["GeoJSON", "Shapefile (.zip)"])

# ----------------------------------------------------------------------
# Filtrage
# ----------------------------------------------------------------------
if choix_arrondissement == "Tous les arrondissements":
    gdf_filtre = gdf.copy()
else:
    gdf_filtre = gdf[gdf["nom"] == choix_arrondissement].copy()

# ----------------------------------------------------------------------
# Titre principal
# ----------------------------------------------------------------------
st.title("Cartographie de la susceptibilité aux inondations")

# ----------------------------------------------------------------------
# Carte Folium — un seul fond de carte : OpenStreetMap.
# ----------------------------------------------------------------------
centre = [6.4485, 2.3556]
carte = folium.Map(location=centre, zoom_start=12, tiles="OpenStreetMap")


def construire_message_html(row: gpd.GeoSeries, colonne_risque: str, annee_label: str) -> str:
    """Message affiché au survol d'un arrondissement (anciennement affiché
    au clic dans un popup)."""
    niveau = row[colonne_risque]
    precaution = PRECAUTIONS.get(niveau, "Aucune précaution renseignée.")
    return f"""
    <div style="font-size:13px; width:250px; white-space:normal; word-wrap:break-word;">
        <b>Arrondissement :</b> {row['nom']}<br>
        <b>Niveau de risque ({annee_label}) :</b> {niveau}<br>
        <b>Coordonnées géographiques :</b> {row['lat_centre']}, {row['lon_centre']}<br>
        <b>Consignes préventives :</b> {precaution}
    </div>
    """


def ajouter_couche(gdf_source: gpd.GeoDataFrame, colonne_risque: str, nom_couche: str, annee_label: str, afficher_par_defaut: bool):
    groupe = folium.FeatureGroup(name=nom_couche, show=afficher_par_defaut)
    for _, row in gdf_source.iterrows():
        niveau = row[colonne_risque]
        couleur = COULEURS_RISQUE.get(niveau, "#95a5a6")
        geojson_feature = json.loads(gpd.GeoSeries([row.geometry]).to_json())
        folium.GeoJson(
            geojson_feature,
            style_function=lambda x, couleur=couleur: {
                "fillColor": couleur,
                "color": "#333333",
                "weight": 1,
                "fillOpacity": 0.6,
            },
            highlight_function=lambda x: {"weight": 3, "color": "black"},
            tooltip=folium.Tooltip(construire_message_html(row, colonne_risque, annee_label), sticky=True),
        ).add_to(groupe)
    groupe.add_to(carte)


if afficher_2025:
    ajouter_couche(gdf_filtre, "risque_2025", "Susceptibilité 2025 (actuelle)", "2025 (actuelle)", True)
if afficher_2040:
    ajouter_couche(gdf_filtre, "risque_2040", "Susceptibilité 2040 (projetée)", "2040 (projetée)", not afficher_2025)

# Légende personnalisée
legende_html = """
<div style="position: fixed; bottom: 30px; left: 30px; z-index: 9999;
            background-color: white; padding: 10px 14px; border-radius: 6px;
            box-shadow: 0 0 6px rgba(0,0,0,0.3); font-size: 13px;">
<b>Niveau de risque</b><br>
"""
for niveau, couleur in COULEURS_RISQUE.items():
    legende_html += (
        f'<i style="background:{couleur};width:12px;height:12px;'
        f'display:inline-block;margin-right:6px;"></i>{niveau}<br>'
    )
legende_html += "</div>"
carte.get_root().html.add_child(folium.Element(legende_html))

# Le contrôle des couches ne gère ici QUE l'affichage/masquage des couches
# de susceptibilité (2025 / 2040) — plus aucun fond de carte n'y figure,
# ce qui évite tout changement de fond involontaire. Il est replié par
# défaut : on retrouve l'icône (logo en pile de calques) en haut à droite,
# qui s'ouvre au clic/survol.
folium.LayerControl(collapsed=True).add_to(carte)

# Correction de l'affichage du texte au survol : par défaut, un tooltip
# Leaflet ne retourne pas à la ligne (white-space: nowrap), ce qui faisait
# dépasser le texte des consignes préventives hors du fond blanc. On force
# le retour à la ligne et une largeur maximale cohérente avec le contenu.
carte.get_root().header.add_child(folium.Element("""
<style>
.leaflet-tooltip {
    white-space: normal !important;
    max-width: 280px !important;
    line-height: 1.4;
}
</style>
"""))

st_data = st_folium(carte, width=None, height=600)

# ----------------------------------------------------------------------
# Tableau récapitulatif
# ----------------------------------------------------------------------
st.subheader("Tableau récapitulatif")
st.dataframe(
    gdf_filtre[["nom", "risque_2025", "risque_2040", "lat_centre", "lon_centre"]].rename(
        columns={
            "nom": "Arrondissement",
            "risque_2025": "Risque 2025",
            "risque_2040": "Risque 2040",
            "lat_centre": "Latitude",
            "lon_centre": "Longitude",
        }
    ),
    use_container_width=True,
)

# ----------------------------------------------------------------------
# Export des couches
# ----------------------------------------------------------------------
st.subheader("Export des données")

if format_export == "GeoJSON":
    export_bytes = gdf_filtre.drop(columns=["lat_centre", "lon_centre"]).to_json().encode("utf-8")
    st.download_button(
        "Télécharger en GeoJSON",
        data=export_bytes,
        file_name="susceptibilite_abomey_calavi.geojson",
        mime="application/geo+json",
    )
else:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        tmp_dir = Path("/tmp/export_shp")
        tmp_dir.mkdir(exist_ok=True)
        shp_path = tmp_dir / "susceptibilite_abomey_calavi.shp"
        gdf_filtre.drop(columns=["lat_centre", "lon_centre"]).to_file(shp_path, driver="ESRI Shapefile")
        for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
            f = shp_path.with_suffix(ext)
            if f.exists():
                zf.write(f, arcname=f.name)
    st.download_button(
        "Télécharger en Shapefile (.zip)",
        data=buffer.getvalue(),
        file_name="susceptibilite_abomey_calavi_shp.zip",
        mime="application/zip",
    )
