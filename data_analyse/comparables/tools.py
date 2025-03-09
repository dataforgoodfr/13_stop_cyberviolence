from typing import List, Union
import pandas as pd
import numpy as np

def discretize_age(
    data: pd.DataFrame,
    date_col: str = 'DATE_TIME',
    bd_col: str = "DATE_NAISSANCE",
    bins: List[int] = [0, 11, 13, 15, 17, 99],
    labels: List[str] = ['0-11', '11-12', '13-14', '15-17', '>17'],
    no_days_year: float = 365.2425
) -> pd.Series:
    
    return pd.cut(
        # delta t annees
        (data[date_col] - data[bd_col]).dt.days // no_days_year,
        bins = bins,
        labels = labels,
        right = False
    )

def stratified_distribution(
    data: pd.DataFrame,
    *grouping_variables: str,
    unique_col: str = "ID_REPONDANT"
) -> pd.DataFrame:
    """
    Calculates the distribution of unique values from unique_col within each stratum 
    defined by the grouping variables.

    Args:
        data (pd.DataFrame): The input DataFrame.
        *grouping_variables (str): The names of the columns to group by.
        unique_col (str, optional): The name of the column containing unique respondent IDs.
            Defaults to "ID_REPONDANT".
    Returns:
        pd.DataFrame: A DataFrame with the distribution of unique respondent counts for each stratum.
    """
    return data \
            .groupby([*grouping_variables]) \
            .apply(lambda x: x[unique_col].unique().shape[0])

def stratified_response_distribution(
    data: pd.DataFrame,
    response_key: Union[str, List[str]],
    *grouping_variables: str,
    response_col: str = "KEY_REPONSE",
    unique_col: str = "ID_REPONDANT"
):
    """
    Calculates the distribution of a specific response (or responses) within each stratum
    defined by the grouping variables.  The count represents the number of unique respondents
    giving the specified response(s) within each group. The returned distribution corresponds to
    respondents who gave at least one of the specified responses.

    Args:
        data (pd.DataFrame): The input DataFrame.
        response_key (Union[str, List[str]]): The specific response value (or list of values) to filter for.
        *grouping_variables (str): The names of the columns to group by.
        response_col (str, optional): The name of the column containing the response values.
            Defaults to "KEY_REPONSE".
        unique_col (str, optional): The name of the column containing unique respondent IDs.
            Defaults to "ID_REPONDANT".

    Returns:
        pd.Series: A Series with counts of the specific response(s) for each stratum.  The index
            of the series corresponds to the grouping variables.
    """

    if not isinstance(response_key, List):
        response_key = [response_key,]

            # .loc[data[response_col] == response_key] \
    return data \
            .query(f"{response_col} in @response_key") \
            .loc[:,[unique_col, *grouping_variables]] \
            .drop_duplicates() \
            .groupby([*grouping_variables]) \
            .count().iloc[:,0]
            
def estimate_proportion(
    data: pd.DataFrame,
    response_key: Union[str, List[str]],
    grouping_variables: List[str] = None,
    scale_by: Union[float, int] = 1
) -> pd.DataFrame:
    """
    Estimates the proportion of a specific response within strata defined by the grouping variables.
    Also estimates the standard error and confidence intervals for the proportion.

    Args:
        data (pd.DataFrame): The input DataFrame.
        response_key (str): The specific response value to calculate the proportion for.
        grouping_variables (List[str], optional): A list of column names to group by.
            Defaults to None.
        scale_by (Union[float, int], optional): A scaling factor to apply to the proportion estimates.
            Defaults to 1.

    Returns:
        pd.DataFrame: A DataFrame containing the estimated proportion ('phat'), standard error ('std'),
            lower limit ('LL'), and upper limit ('UL') of the confidence interval for each stratum.
            All values are multiplied by 100 to represent percentages.

    Raises:
        KeyError: If any of the grouping variables are not found in the DataFrame.
    """

    for v in grouping_variables:
        if v not in data.columns:
            raise KeyError(f"{v} not found in {data.columns.to_list()}")

    response_dist = stratified_response_distribution(
        data, response_key, *grouping_variables
    )

    dist = stratified_distribution(
        data, *grouping_variables
    )

    #stratified esimation of proportion
    phat = (response_dist / dist).to_frame()
    phat.columns = ['phat']

    # variance/std esimation
    phat['std'] = np.sqrt((phat.phat * (1 - phat.phat)) / dist)

    # .95 CI, two-sided, CLT
    phat['LL'] = phat.phat - 1.96 * phat['std']
    phat['UL'] = phat.phat + 1.96 * phat['std']

    return phat.multiply(100).multiply(scale_by)