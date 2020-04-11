import json
import pandas as pd
from glob import glob

DATA_DIR = './data'


def load_json_data(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame({'date_time': data['data']['columns'][0][1:],  # first item in array is the title
                       'cases': data['data']['columns'][1][1:]})
    df['date_time'] = pd.to_datetime(df['date_time'])
    df['cases'] = df['cases'].astype('int')
    return df 


def load_cases_by_onset():
    dfs = []
    files = glob(DATA_DIR + '/raw/us-cases-epi-chart-*.json')
    for f in files: 
        df = load_json_data(f)
        # can get date from filepath or last date in data 
        df['report_date'] = df['date_time'].max()
        dfs += [df]

    return pd.concat(dfs)  


def process_data():
    df = load_cases_by_onset()
    df.to_csv(DATA_DIR + '/cases_by_onset.csv', index=False)


if __name__ == "__main__":
    process_data()
