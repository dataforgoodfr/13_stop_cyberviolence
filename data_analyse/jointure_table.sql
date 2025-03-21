SELECT 
    etab.ID_ETABLISSEMENT,
    etab.TYPE AS ETAB_TYPE,
    etab.NB_ELEVES_ETAB,
    etab.ZIPCODE,
    etab.ACADEMIE,
    commune.LB_COMMUNE,
    commune.NB_HABITANTS,
    commune.DEPARTEMENT,
    commune.REGION,
    classe.ID_CLASSE,
    classe.NB_ELEVES_CLASSE,
    classe.NIVEAU,
    enseignant.ID_ENSEIGNANT,
    eleve.ID_RESPONDANT,
    eleve.GENRE,
    eleve.AGE,
    fact.DATE_TIME,
    fact.TYPE_RESPONDANT,
    reponse.ID_REPONSE,
    reponse.LB_REPONSE,
    reponse.TYPE_REPONSE,
    question.LB_QUESTION,
    question.CATEGORIE,
    score.MACRO_SEGMENT,
    score.SEGMENT,
    score.SCORE_PRIMAIRE,
    score.SCORE_SECONDAIRE
FROM FACT_REPONSE fact
JOIN DIM_ELEVE eleve ON fact.ID_RESPONDANT = eleve.ID_RESPONDANT
JOIN DIM_CLASSE classe ON eleve.ID_CLASSE = classe.ID_CLASSE
JOIN DIM_ETABLISSEMENT etab ON classe.ID_ETABLISSEMENT = etab.ID_ETABLISSEMENT
JOIN DIM_COMMUNE commune ON etab.ZIPCODE = commune.ZIPCODE
JOIN DIM_ENSEIGNANT enseignant ON classe.ID_CLASSE = enseignant.ID_CLASSE
JOIN DIM_REPONSE reponse ON fact.KEY_REPONSE = reponse.KEY_REPONSE
JOIN DIM_QUESTION question ON reponse.KEY_QUESTION = question.KEY_QUESTION
JOIN DIM_SCORE score ON reponse.KEY_REPONSE = score.KEY_REPONSE;
