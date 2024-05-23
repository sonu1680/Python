import pandas as pd
import numpy as np
import math
import json
from urllib.error import HTTPError

def main(params):
    url = "https://drive.google.com/uc?id=1Moy7gFri9FPmDspWyK2rJWU4n7AJP18R"

    try:
        df = pd.read_csv(url)
    except HTTPError as e:
        return json.dumps({"error": f"Failed to download the file: {e}"})

    df.drop("Unnamed: 0", axis=1, inplace=True)
    df.set_index(pd.DatetimeIndex(df.Date.values), inplace=True)
    df.drop("Date", axis=1, inplace=True)

    yr = int(params.get('year', 1))

    if yr == 1:
        df = df['2023-05-22':'2024-05-22']
    elif yr == 3:
        df = df['2021-05-22':'2024-05-22']

    daily_simple_returns = df.pct_change(1)
    annual_returns = daily_simple_returns.mean() * 252
    annual_risks = daily_simple_returns.std() * math.sqrt(252)

    df2 = pd.DataFrame()
    df2['Expected Annual Returns'] = annual_returns
    df2['Expected Annual Risks'] = annual_risks
    df2['Company Symbol'] = df2.index
    df2['Ratio'] = df2['Expected Annual Returns'] / df2['Expected Annual Risks']
    df2.sort_values(by="Ratio", axis=0, ascending=False, inplace=True)

    remove_list = []
    for ticker in df2['Company Symbol'].values:
        no_better_asset = df2.loc[
            (df2['Expected Annual Returns'] > df2['Expected Annual Returns'][ticker]) &
            (df2['Expected Annual Risks'] < df2['Expected Annual Risks'][ticker])
        ].empty
        if not no_better_asset:
            remove_list.append(ticker)

    findf = df2.drop(remove_list)

    output_ticker = list(findf['Company Symbol'])
    output_returns = list(findf['Expected Annual Returns'] * 100)

    assets = findf.index
    num_assets = len(assets)
    n = 1.0 / float(num_assets)
    weights = [n] * num_assets
    weights = np.array(weights)

    output_port_ar = round(np.sum(weights * output_returns), 2)

    result = {
        "Companies": output_ticker,
        "Returns": output_returns,
        "Total Portfolio return": output_port_ar
    }

    return json.dumps(result)

def handler(event, context):
    params = event.get('queryStringParameters', {})
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': main(params)
    }
