import pandas as pd
from pathlib import Path
import sys
import os 
from datetime import timedelta
from fbprophet import Prophet


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


def load_prices():
    # TODO - rolling joins to usage
    df = pd.read_excel(Path(REPO_DIR, 'data/raw/Tariffs.xlsx'))
    return df 


def make_prediction_df(df_weather, start_time, prediction_window_minutes, minutes_between_predictions):
    assert prediction_window_minutes % minutes_between_predictions == 0 
    n_pred = int(prediction_window_minutes / minutes_between_predictions)
    times = [start_time + timedelta(minutes=i*minutes_between_predictions) for i in range(n_pred)]
    df = pd.DataFrame({'date_time': times})
    df['timestamp_hour'] = df.date_time.dt.strftime('%Y-%m-%d %H')
    df = pd.merge(df, df_weather, on='timestamp_hour')
    df['ds'] = df['date_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    return df
<span class="css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0">Valeria Cardenas</span>

def iteratively_forecast(df, df_weather, prediction_start, prediction_end, prediction_window_minutes=60*24*7, minutes_between_predictions=60):

    df_predictions = pd.DataFrame()
    timestamp = prediction_start

    # Split train
    while timestamp < prediction_end:
        print(f'Predicting from {timestamp}')
        df_train = df.loc[df.date_time < timestamp]
        m = Prophet()
        m.add_country_holidays(country_name = 'UK')
        m.add_regressor('temperature')
        m.fit(df_train)

        df_future = make_prediction_df(df_weather, timestamp, prediction_window_minutes, minutes_between_predictions)
        df_future = m.predict(df_future)
        df_predictions = pd.concat([df_predictions, df_future], ignore_index=True)

        timestamp += timedelta(minutes=prediction_window_minutes)

    df_predictions['date_time'] = pd.to_datetime(df_predictions['ds']).dt.tz_localize(tz="GMT")

    return df_predictions 




https://twitter.com/TheFlatballer/status/1227673375126048770
driver.get("https://twitter.com/TheFlatballer/status/1227673375126048770")

driver.find_elements_by_class_name('css-18t94o4 css-1dbjc4n r-1niwhzg r-p1n3y5 r-sdzlij r-1phboty r-rs99b7 r-16y2uox r-1w2pmg r-1vsu8ta r-aj3cln r-1fneopy r-o7ynqc r-6416eg r-lrvibr')

import time
from selenium import webdriver

for i in range(0, 2):
    print(i)
    driver = webdriver.Firefox()
    driver.get("https://ultiworld.com/2020/02/11/ultiworlds-2019-block-year-bracket-presented-ultimate/")

    button = driver.find_element_by_id('PDI_answer48598238')
    button.click()
    button = driver.find_element_by_id('pd-vote-button10506197')
    button.click()
    # driver.refresh()  # refresh doesn't reset the session_id, you must reinstantiate the driver


