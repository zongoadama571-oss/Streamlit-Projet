# ==============================
# IMPORTATIONS
# ==============================
import pandas as pd
import streamlit as st
import plotly.express as px

# ==============================
# CONFIGURATION DE LA PAGE
# ==============================
# Définit la mise en page en mode large et le titre de l'application 
st.set_page_config(layout="wide")
st.title("📊 Dashboard des ventes")

# ==============================
# STYLE GLOBAL (CSS)
# ==============================
# Injection de CSS pour personnaliser l'apparence sombre et moderne
st.markdown("""
<style>

/* Couleur de fond de la page entière */
body {
    background-color: #0e1117;
}

/* Style des cartes d'indicateurs (KPI) */
.metric-card {
    background: #1a1f2b;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    color: white;
    transition: all 0.3s ease;
}

/* Effet au survol des KPIs (soulèvement et ombre bleue) */
.metric-card:hover {
    transform: translateY(-5px) scale(1.03);
    box-shadow: 0px 10px 25px rgba(0, 200, 255, 0.4);
}

/* Style des conteneurs de graphiques (arrondis et ombres) */
.graph-card {
    background: #131720;
    padding: 0px; 
    border-radius: 15px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.6);
    overflow: hidden; 
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# TRAITEMENT DES DONNÉES (DATA)
# ==============================
# Chargement du fichier CSV avec gestion du séparateur européen
df = pd.read_csv("Sales-Export_2019-2020.csv", sep=";", engine="python", on_bad_lines="skip")

# Fonction pour nettoyer les colonnes monétaires (retrait du symbole €, gestion des espaces et virgules)
def clean_money(col):
    return (
        col.astype(str)
        .str.replace("€", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

# Conversion des colonnes en format numérique exploitable
df['order_value_EUR'] = pd.to_numeric(clean_money(df['order_value_EUR']), errors='coerce')
df['cost'] = pd.to_numeric(clean_money(df['cost']), errors='coerce')

# Nettoyage des lignes vides après conversion
df = df.dropna(subset=['order_value_EUR', 'cost'])

# Calcul du profit et conversion de la colonne date
df['profit'] = df['order_value_EUR'] - df['cost']
df['date'] = pd.to_datetime(df['date'], dayfirst=True)

# ==============================
# SECTION DES INDICATEURS (KPI)
# ==============================
# Création de 4 colonnes pour afficher les chiffres clés en haut
col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"<div class='metric-card'><h4>CA</h4><h2>{int(df['order_value_EUR'].sum())}</h2></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='metric-card'><h4>Coût</h4><h2>{int(df['cost'].sum())}</h2></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='metric-card'><h4>Profit</h4><h2>{int(df['profit'].sum())}</h2></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='metric-card'><h4>Commandes</h4><h2>{df.shape[0]}</h2></div>", unsafe_allow_html=True)

# ==============================
# GRAPHIQUE : COURBE D'ÉVOLUTION
# ==============================
# Agrégation des ventes et profits par mois
df['month'] = df['date'].dt.to_period('M').astype(str)
evolution = df.groupby('month')[['order_value_EUR', 'profit']].sum().reset_index()

# Création du graphique linéaire
fig_line = px.line(
    evolution, x='month', y=['order_value_EUR', 'profit'], markers=True
)

# Mise en forme visuelle (couleurs sombres et marges réduites)
fig_line.update_layout(
    template="plotly_dark",
    plot_bgcolor="#131720",
    paper_bgcolor="#131720",
    margin=dict(l=0, r=0, t=30, b=0)
)

# ==============================
# CARTE (INTÉGRATION MODERNE STYLE IMAGE)
# ==============================
# Groupement par pays pour la carte choroplèthe
country_sales = df.groupby('country')['order_value_EUR'].sum().reset_index()

fig_map = px.choropleth(
    country_sales,
    locations='country',
    locationmode='country names',
    color='order_value_EUR',
    # Dégradé "Néon" du bleu très sombre au cyan éclatant
    color_continuous_scale=['#1a1f2b', '#00c8ff']
)

# Configuration pour supprimer l'aspect "rectangle coincé"
fig_map.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),   
    paper_bgcolor='rgba(0,0,0,0)', # Rend le fond du graphique transparent
    plot_bgcolor='rgba(0,0,0,0)',     
    height=450,
    coloraxis_showscale=False # Masque la barre de légende pour un look plus propre
)

# Configuration de la géographie (Zoom Europe et style flottant)
fig_map.update_geos(
    scope='europe',
    projection_type='natural earth', # Courbure plus moderne que la projection standard
    fitbounds="locations", # Zoom auto sur les pays concernés

    showland=True,
    landcolor="#1a1f2b", # Couleur des pays sans données (proche du fond)

    showocean=True,
    oceancolor="#131720", # FUSION : même couleur que ton fond de carte .graph-card

    showcountries=True,
    countrycolor="#333", # Lignes de frontières très subtiles

    showframe=False, # Supprime le cadre rectangulaire extérieur
    bgcolor='rgba(0,0,0,0)' # Fond de carte transparent
)

# ==============================
# GRAPHIQUE : BARRES PAR CATÉGORIE
# ==============================
# Somme du CA et Profit par catégorie de produit
cat_data = df.groupby('category')[['order_value_EUR', 'profit']].sum().reset_index()

fig_bar = px.bar(
    cat_data, x='category', y=['order_value_EUR', 'profit'], barmode='group'
)

fig_bar.update_layout(
    template="plotly_dark",
    plot_bgcolor="#131720",
    paper_bgcolor="#131720",
    margin=dict(l=0, r=0, t=30, b=0)
)

# ==============================
# GRAPHIQUE : TOP 10 VENDEURS (DONUT)
# ==============================
# Extraction des 10 meilleurs commerciaux
top_sales = (
    df.groupby('sales_rep')['order_value_EUR']
    .sum()
    .reset_index()
    .sort_values(by='order_value_EUR', ascending=False)
    .head(10)
)

fig_pie = px.pie(
    top_sales, names='sales_rep', values='order_value_EUR', hole=0.5
)

fig_pie.update_layout(
    template="plotly_dark",
    paper_bgcolor="#131720"
)

# ==============================
# GRAPHIQUE : TREEMAP MANAGERS
# ==============================
# Visualisation de la hiérarchie et du volume par manager
manager_perf = df.groupby('sales_manager')['order_value_EUR'].sum().reset_index()

fig_tree = px.treemap(
    manager_perf, path=['sales_manager'], values='order_value_EUR'
)

fig_tree.update_layout(
    template="plotly_dark",
    paper_bgcolor="#131720"
)

# ==============================
# MISE EN PAGE FINALE (LAYOUT)
# ==============================
# Première ligne : Courbe d'évolution et Carte de l'Europe
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_line, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Deuxième ligne : Graphique en barres et Camembert
col3, col4 = st.columns(2)

with col3:
    st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Dernière ligne : Treemap pleine largeur
st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
st.plotly_chart(fig_tree, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

