# Plateforme Web-SIG — Susceptibilité aux inondations à Abomey-Calavi

Prototype en 3 phases :
1. Interface Web-SIG interactive (Streamlit + Folium)
2. Déploiement automatisé (GitHub → Streamlit Cloud, CI/CD)
3. Analyse des réponses du questionnaire d'utilisabilité (SUS + TAM, Excel)

---

## 0. Le prompt réutilisable

Si tu veux redemander ce type d'application à une IA (ou l'adapter à un autre sujet), voici un prompt prêt à l'emploi :

```
Développe une application Web-SIG interactive en Python avec Streamlit et Folium,
pour visualiser la susceptibilité aux inondations d'une commune. Elle doit inclure :

1. Une carte Folium centrée sur [NOM DE LA COMMUNE], fond de carte OpenStreetMap.
2. Un sélecteur permettant de basculer entre deux couches temporelles
   (situation actuelle [ANNÉE A] et situation projetée [ANNÉE B]), avec une
   légende de couleurs par niveau de risque (Faible/Moyen/Élevé/Très élevé).
3. Un filtre interactif par [UNITÉ ADMINISTRATIVE, ex : arrondissement] avec
   popups affichant le nom et le niveau de risque au clic.
4. Un module d'export des couches filtrées en GeoJSON et en Shapefile (.zip).
5. Un fichier requirements.txt complet et un README expliquant :
   - l'installation locale (venv + pip install)
   - le déploiement en continu via GitHub + Streamlit Cloud
   - la structure attendue des données GeoJSON en entrée
6. Fournis aussi un script séparé d'analyse Excel qui calcule le score SUS
   (System Usability Scale, seuils 68 = acceptable, 80 = excellent) et une
   synthèse descriptive TAM à partir des réponses d'un questionnaire.

Livre le code complet, prêt à exécuter, avec des données de démonstration
(GeoJSON placeholder) si je n'ai pas encore mes propres couches.
```

---

## 1. Contenu du dossier

```
webgis_app/
├── app.py                  # Application Streamlit principale
├── analyse_sus_tam.py      # Script d'analyse SUS/TAM à partir d'un Excel
├── requirements.txt        # Dépendances Python
├── data/
│   └── arrondissements.geojson   # Données DE DÉMONSTRATION (à remplacer)
└── README.md
```

⚠️ **Important** : `data/arrondissements.geojson` contient des polygones
schématiques (rectangles) juste pour que l'appli fonctionne tout de suite.
Remplace ce fichier par tes vraies couches de susceptibilité (export QGIS,
avec les champs `nom`, `risque_2025`, `risque_2040`) issues de ton OCS 2015
et de ton modèle de susceptibilité.

---

## 2. Installation et test en local

```bash
# 1. Se placer dans le dossier du projet
cd webgis_app

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate        # sous Windows : venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
streamlit run app.py
```

L'application s'ouvre automatiquement dans le navigateur (généralement sur
`http://localhost:8501`).

---

## 3. Déploiement automatisé (GitHub + Streamlit Cloud)

1. Crée un dépôt GitHub (public ou privé) et pousse tout le contenu du
   dossier `webgis_app/` :
   ```bash
   git init
   git add .
   git commit -m "Première version de la plateforme Web-SIG"
   git branch -M main
   git remote add origin https://github.com/<ton-utilisateur>/<ton-depot>.git
   git push -u origin main
   ```
2. Va sur [streamlit.io/cloud](https://streamlit.io/cloud) et connecte-toi
   avec ton compte GitHub.
3. Clique sur **New app**, sélectionne ton dépôt, la branche `main`, et
   indique `app.py` comme fichier principal.
4. Clique sur **Deploy**. À chaque `git push` sur `main`, l'application se
   met à jour automatiquement (CI/CD intégré à Streamlit Cloud).
5. L'interface est nativement responsive (elle s'adapte aux smartphones).

---

## 4. Analyse du questionnaire d'utilisabilité (SUS + TAM)

Ton fichier Excel de réponses doit contenir les colonnes `sus_1` à `sus_10`
(notes de 1 à 5, questionnaire SUS standard) et, si tu as un volet TAM,
des colonnes `tam_1`, `tam_2`, etc.

```bash
python analyse_sus_tam.py chemin/vers/reponses.xlsx
```

Le script affiche :
- le score SUS individuel de chaque répondant (0–100),
- la moyenne, l'écart-type, le min/max,
- la part de répondants au-dessus du seuil d'utilisabilité (68) et
  d'excellence (80),
- la moyenne par item TAM (s'il y en a),

et enregistre un fichier `resultats_sus_tam.xlsx` à côté du fichier source.

Utilise ensuite ces résultats pour identifier les faiblesses remontées
(ex. lenteur de chargement, clarté de la légende) et corriger l'application
en conséquence avant la livraison finale (itération sur `app.py`).

---

## 5. Prochaines étapes suggérées

- Remplacer `data/arrondissements.geojson` par les vraies limites
  administratives et les scores de susceptibilité issus de ton modèle.
- Ajouter d'éventuelles couches complémentaires (OCS 2015, hydrographie,
  zones inondables) en suivant le même principe (`folium.GeoJson`).
- Ajouter une authentification ou une page d'accueil si besoin, via les
  composants natifs de Streamlit.
