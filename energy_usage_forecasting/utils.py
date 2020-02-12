import pandas as pd
from pathlib import Path
import sys
import os 


REPO_DIR = os.path.join(os.environ['HOME'], 'github/blog/energy_usage_forecasting') 


def load_usage_data(timescale='daily'):
    assert timescale in ['daily', 'halfhourly']
    DIR = Path(REPO_DIR, f'data/raw/smart-meters-in-london/{timescale}_dataset/{timescale}_dataset')
    files = os.listdir(DIR)
    dfs = [pd.read_csv(Path(DIR, f)) for f in files]
    df = pd.concat(dfs)
    
    if timescale == 'daily':
        df['date_time'] = pd.to_datetime(df['day']).dt.tz_localize(tz="GMT")
        df['timestamp_day'] = df.date_time.dt.strftime('%Y-%m-%d')
        df_weather = pd.read_csv(Path(REPO_DIR, 'data/raw/smart-meters-in-london/weather_daily_darksky.csv'))
        df_weather['date_time'] = pd.to_datetime(df_weather['time']).dt.tz_localize(tz="GMT")
        df_weather['timestamp_day'] = df_weather.date_time.dt.strftime('%Y-%m-%d')
        # HACK
        df_weather['temperature'] = df_weather['temperatureMin']
        df = pd.merge(df, df_weather[['timestamp_day', 'temperature']])
        
    elif timescale == "halfhourly": 
        df['date_time'] = pd.to_datetime(df['tstp']).dt.tz_localize(tz="GMT")
        df['timestamp'] = df.date_time.dt.strftime('%Y-%m-%d %H:%M')
        df['timestamp_hour'] = df.date_time.dt.strftime('%Y-%m-%d %H')
        df_weather = pd.read_csv(Path(REPO_DIR, 'data/raw/smart-meters-in-london/weather_hourly_darksky.csv'))
        df_weather['date_time'] = pd.to_datetime(df_weather['time']).dt.tz_localize(tz="GMT")
        df_weather['timestamp_hour'] = df_weather.date_time.dt.strftime('%Y-%m-%d %H')

    df_hh = pd.read_csv(Path(REPO_DIR, 'data/raw/smart-meters-in-london/informations_households.csv'))
    df = pd.merge(df_hh, df, on='LCLid')
        
    return df
