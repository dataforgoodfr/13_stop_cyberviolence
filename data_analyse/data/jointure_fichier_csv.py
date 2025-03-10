import pandas as pd

# Chargement des données

dim_etablissement = pd.read_csv('DIM_ETABLISSEMENT.csv')
dim_commune = pd.read_csv('DIM_COMMUNE.csv')
dim_classe = pd.read_csv('DIM_CLASSE.csv')
dim_enseignant = pd.read_csv('DIM_ENSEIGNANT.csv')
dim_eleve = pd.read_csv('DIM_ELEVE.csv')
fact_reponse = pd.read_csv('FACT_REPONSE.csv')
dim_reponse = pd.read_csv('DIM_REPONSE.csv')
dim_score = pd.read_csv('DIM_SCORE.csv')
dim_question = pd.read_csv('DIM_QUESTION.csv')

# Jointures
df = fact_reponse.merge(dim_eleve, on='ID_RESPONDANT', how='inner') \
    .merge(dim_classe, on='ID_CLASSE', how='inner') \
    .merge(dim_etablissement, on='ID_ETABLISSEMENT', how='inner') \
    .merge(dim_commune, on='ZIPCODE', how='inner') \
    .merge(dim_enseignant, on='ID_CLASSE', how='inner') \
    .merge(dim_reponse, on='KEY_REPONSE', how='inner') \
    .merge(dim_question, on='KEY_QUESTION', how='inner') \
    .merge(dim_score, on='KEY_REPONSE', how='inner')

df.head()