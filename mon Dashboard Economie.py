import streamlit as st
import pandas as pd
import plotly.express as px

# CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="Dashboard économique - Burkina Faso",
    layout="wide",
    page_icon="📊"
)

# STYLE de l'app web
st.markdown(""" 
<style>
    /* 1. TOUT LE FOND DU SITE */
    .stApp {
        background-color: #121026; /* On met le fond en noir très sombre */
        color: #FFFFFF;           /* On écrit tous les textes en blanc pour qu'ils se voient */
    }

    /* 2. LA BARRE DE GAUCHE (MENU) */
    [data-testid="stSidebar"] {
        background-color: #161B22 !important; /* On met le menu de gauche en gris-noir */
        border-right: 2px solid #009E60;      /* On dessine une ligne verte à droite du menu */
    }

    /* 3. LE GROS TITRE EN HAUT */
    h1 {
        /* On crée un mélange de Rouge, Jaune et Vert */
        background: linear-gradient(90deg, #EF2B2D, #FCD116, #009E60); 
        -webkit-background-clip: text;       /* On dit au mélange de rester DANS les lettres */
        -webkit-text-fill-color: transparent; /* On vide l'intérieur des lettres pour voir le mélange */
        text-align: center;                  /* On place le titre bien au milieu */
        font-weight: 800;                    /* On écrit le titre en très très gras */
        font-size: 3rem;                     /* On écrit le titre en très gros */
        padding-bottom: 20px;                /* On laisse un peu de place sous le titre */
    }

    /* 4. LES PETITS CADRES AVEC DES CHIFFRES (MÉTRIQUES) */
    div[data-testid="stMetric"] {
        background-color: #1F2937;           /* On met un fond gris foncé dans chaque cadre */
        border: 1px solid #374151;           /* On dessine une petite bordure grise tout autour */
        padding: 20px;                       /* On laisse de l'espace pour que le chiffre ne touche pas les bords */
        border-radius: 15px;                 /* On arrondit les coins pour que ce soit joli */
        box-shadow: 0 4px 15px rgba(0,0,0,0.3); /* On ajoute une petite ombre pour faire "voler" le cadre */
        transition: transform 0.3s;          /* On dit au cadre de bouger doucement si on le touche */
    }
            div[data-testid="stMetric"]:hover {
        transform: scale(1.02);
        border-color: #FCD116; /* Bordure jaune au survol */
    }

    /* 5. COULEUR DES CHIFFRES ET DES TEXTES */
    [data-testid="stMetricValue"] {
        color: #FCD116 !important;           /* On force le chiffre important à devenir JAUNE */
    }
    [data-testid="stMetricLabel"] {
        color: #9CA3AF !important;           /* On met le nom du chiffre en gris clair */
    }

    /* 6. NETTOYAGE DU SITE */
    #MainMenu {visibility: hidden;}          /* On cache le petit menu moche en haut à droite */
    footer {visibility: hidden;}             /* On cache le texte "Made with Streamlit" tout en bas */
</style>
""", unsafe_allow_html=True) # On autorise Streamlit à lire tout ce code CSS

# --- CONTENU DU DASHBOARD ---

st.title("Prévision Données Macroéconomique (2026)")

# Organisation en colonnes pour les chiffres clés
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Population", "24.6 M", "Indice 2026")

with col2:
    st.metric("Croissance PIB", "4.8%", "+0.8%")

with col3:
    st.metric("Taux d'inflation", "1.5%", "-0.3%")
# Espace pour tes futurs graphiques
st.write("---")
st.subheader("Analyses sectorielles 2010-2025")
# Ici on ajoute les graphiques

# TITRE
st.title("📊 Dashboard des indicateurs économiques du Burkina Faso")

# CHARGEMENT DES DONNÉES
@st.cache_data
def load_data():
    population = pd.read_csv("population_bf.csv", sep=";", encoding='latin1', decimal=",")
    pib = pd.read_csv("pib_bf.csv", sep=";", encoding='latin1', decimal=",")
    exportation_importation = pd.read_csv("exportation_importation_bf.csv", sep=";", encoding='latin1', decimal=",")
    inflation = pd.read_csv("inflation_bf.csv", sep=";", encoding='latin1', decimal=",")
    
    return {
        "Population": population,
        "PIB": pib,
        "exportation_importation": exportation_importation,
        "Inflation": inflation
    }

tables = load_data() # On lance la fonction qui va chercher tous tes fichiers CSV

# --- SIDEBAR - CHOIX DE LA TABLE ---
st.sidebar.title("🧭 Navigation") # On affiche un titre "Navigation" dans le menu de gauche
# On crée une liste déroulante pour choisir un fichier
table_choisie = st.sidebar.selectbox( 
    "Choisir une table", # Le texte affiché au-dessus de la liste
    list(tables.keys()) # On met les noms de tes fichiers dans la liste
)

df = tables[table_choisie] # On met les données du fichier choisi dans la variable "df"

# --- FILTRE PAR ANNEES ---
if "Annees" in df.columns:  # Si la colonne "Annee" existe dans le fichier CSV
    Annees_min = int(df["Annees"].min()) # On cherche l'année la plus ancienne (le début) et on la transforme en nombre
    Annees_max = int(df["Annees"].max())     # On cherche l'année la plus récente (la fin) et on la transforme en nombre

    # On crée la barre coulissante (slider) dans le menu de gauche
    Annees_range = st.sidebar.slider(
        "📅 choisir une période",  # Le petit texte au-dessus de la barre
        min_value=Annees_min,     # La valeur tout à gauche de la barre
        max_value=Annees_max,     # La valeur tout à droite de la barre
        value=(Annees_min, Annees_max) # Au début, on sélectionne toute la période
    )

    # On crée une copie du tableau pour filtrer les données
    df = df[
        # On garde les années supérieures ou égales au début du slider
        (df["Annees"] >= Annees_range[0]) & 
        # On garde les années inférieures ou égales à la fin du slider
        (df["Annees"] <= Annees_range[1])
    ]

# --- AFFICHAGE DES DONNEES ---
# On écrit un titre pour dire quel fichier est affiché
st.subheader(f"📊 Table : {table_choisie}")

# On affiche le tableau de données (le contenu du fichier CSV)
st.dataframe(df, use_container_width=True) # On lui dit de prendre toute la largeur de l'écran

# --- SECTION VISUALISATION ---
# On affiche un sous-titre pour la partie des graphiques
st.subheader("📊 Visualisation")

# AXE X AUTOMATIQUE (ANNÉE)
# On regarde si la colonne "Annees" existe dans le fichier
if "Annees" in df.columns:
    col_x = "Annees" # Si oui, on choisit automatiquement l'Annees pour l'axe horizontal
else:
    # Sinon, on laisse l'utilisateur choisir une autre colonne dans une liste
    col_x = st.selectbox("Variable x", df.columns)

# AXE Y
# On permet de choisir PLUSIEURS colonnes pour l'axe vertical
cols_y = st.multiselect(
    "Variables sur l'axe Y", # Le titre
    options=df.columns, # Toutes les colonnes disponibles
    default=[df.columns[1]] # On en met une par défaut pour ne pas avoir d'erreur
)

# TYPE DE GRAPHIQUE
# On crée une liste pour que l'utilisateur choisisse la forme du graphique
type_graph = st.selectbox(
    "Type de graphique", # Le texte au-dessus du choix
    ["Ligne", "Scatter"] # Les 2 options disponibles
)

# --- BOUTON D'AFFICHAGE ---
if st.button("📊 Afficher le graphique"):

    # on cree un nouveau tableau a partir de df(passe du format large à long)
    df_long = df.melt(
        id_vars=[col_x], #c'est la colonne pilier qui ne bouge pas (Annees)
        value_vars=cols_y, #ce sont les colonnes qu'on veut demontrer
        var_name="Variable", #ce sont les titre des nouvelles colonnes qui vas lister les anciens colonnes
        value_name="Valeur"  #c'est le titre de la colonne qui contiendra les valeur de ces colonnes
    )

    # --- CHOIX DU TYPE DE GRAPHIQUE ---
    if type_graph == "Ligne":
        fig = px.line(
            df_long,
            x=col_x,
            y="Valeur",
            color="Variable", # couleurs différentes
            markers=True
        )
    else:
        fig = px.scatter(
            df_long,
            x=col_x,
            y="Valeur",
            color="Variable"
        )
    # --- STYLE DU GRAPHIQUE ---
    fig.update_layout(
        title=f"📈 Évolution des indicateurs au Burkina Faso",
        template="plotly_dark",
        legend_title="Indicateurs",
        hovermode="x unified", #le mode survol:quand la souris passe sur le graph, ca affiche les infos
        margin=dict(t=50, b=50, l=50, r=50) #les marges: on laisse de laiss autour du graph
    )

    # --- AFFICHAGE DU GRAPHIQUE---
    st.plotly_chart(fig, use_container_width=True)


# --- CALCUL DE LA PROGRESSION POUR TOUTES LES VARIABLES ---
# On vérifie qu'on a choisi au moins une variable et qu'on a assez de données
if len(cols_y) > 0 and len(df) > 1:

    colonnes_metriques = st.columns(len(cols_y))

    for i, col in enumerate(cols_y):

        #Récupération des valeurs
        valeur_debut = df.iloc[0][col]
        valeur_fin = df.iloc[-1][col]

        #Conversion PROPRE en float (solution clé)
        try:
            valeur_debut = float(str(valeur_debut).replace(",", ".").replace("%", "").strip())
            valeur_fin = float(str(valeur_fin).replace(",", ".").replace("%", "").strip())

            #Calcul sécurisé
            if valeur_debut != 0:
                croissance = ((valeur_fin - valeur_debut) / abs(valeur_debut)) * 100
                variation = valeur_fin - valeur_debut
            else:
                croissance = 0
                variation = 0

        except:
            croissance = 0
            variation = 0

        #Affichage
        with colonnes_metriques[i]:
            st.metric(
                label=f"Evolution {col}",
                value=f"{round(croissance, 2)} %",
                delta=f"{round(variation, 2)}"
            )
