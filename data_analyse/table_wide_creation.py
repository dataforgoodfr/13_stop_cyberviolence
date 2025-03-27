import pandas as pd

# Load csv files
dim_etablissement = pd.read_csv('data/DIM_ETABLISSEMENT.csv')
dim_commune = pd.read_csv('data/DIM_COMMUNE.csv')
dim_classe = pd.read_csv('data/DIM_CLASSE.csv')
dim_enseignant = pd.read_csv('data/DIM_ENSEIGNANT.csv')
dim_eleve = pd.read_csv('data/DIM_ELEVE.csv')
fact_reponse = pd.read_csv('data/FACT_REPONSE.csv')
dim_reponse = pd.read_csv('data/DIM_REPONSE.csv')
dim_score = pd.read_csv('data/DIM_SCORE.csv')
dim_question = pd.read_csv('data/DIM_QUESTION.csv')

df = fact_reponse.merge(dim_eleve, left_on='ID_REPONDANT',right_on='ID_ELEVE', how='inner').drop(columns=['ID_REPONDANT']) \
    .merge(dim_reponse, on='KEY_REPONSE', how='inner') \
    .merge(dim_question, on='KEY_QUESTION', how='inner') \
    .merge(dim_score, on='KEY_REPONSE', how='inner')