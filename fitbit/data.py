import pandas as pd
import numpy as np
from datetime import datetime

def add_date_vars(df):
    df['weekday_name'] = df['date_time'].dt.strftime('%A')
    df['is_weekend'] = df['weekday_name'].isin(['Saturday', 'Sunday'])
    df['weekend_dummy'] = (df['is_weekend']).astype(int)
    df.loc[df['is_weekend'], 'day_type'] = 'Weekend'
    df.loc[~df['is_weekend'], 'day_type'] = 'Weekday'
    df['date'] = df['date_time'].dt.strftime('%D')  # '%Y-%m-%d'
    df['date_desc'] = df['date_time'].dt.strftime('%A %B %d')  # '%A %D'
    return df 

def get_daily_summary_df(client, date_str: str):
    data = client.activities(date=date_str)
    keys_to_keep = ['activityCalories', 'fairlyActiveMinutes', 'lightlyActiveMinutes', 'restingHeartRate',
                    'sedentaryMinutes', 'steps', 'veryActiveMinutes']
    data_dict = {}
    for k in keys_to_keep:
        try: 
            data_dict[k] = data['summary'][k]
        except KeyError:  # some days missing certain metrics, incl restingHeartRate
            data_dict[k] = np.NaN

    df = pd.DataFrame(data_dict, index=[0])
    df['date_time'] = pd.to_datetime(date_str)

    df['distance'] = data['summary']['distances'][0]['distance']

    normal, fat_burn, cardio, peak = data['summary']['heartRateZones']
    # Ensure that the order is consistent
    assert normal['name'] == 'Out of Range'
    assert fat_burn['name'] == 'Fat Burn'
    assert cardio['name'] == 'Cardio'
    assert peak['name'] == 'Peak'
    df['hr_normal_duration_min'] = normal['minutes']
    df['hr_fat_burn_duration_min'] = fat_burn['minutes']
    df['hr_cardio_duration_min'] = cardio['minutes']
    df['hr_peak_duration_min'] = peak['minutes']

    data = client.sleep(date=date_str)
    # Note - more sleep data available for future analysis
    # data['summary'] has sleep cycle summary
    # data['sleep'][0]['minuteData'] has timeseries 
    keys = ['duration', 'efficiency', 'minutesAsleep', 'restlessDuration']
    df['sleepDuration'] = data['sleep'][0]['duration']
    df['sleepEfficiency'] = data['sleep'][0]['efficiency']
    df['sleepMinutes'] = data['sleep'][0]['minutesAsleep']
    df['restlessDuration'] = data['sleep'][0]['restlessDuration']
    
    return df


def get_intraday_heart_df(client, date_str: str):
    # Intraday heart rate timeseries
    data = client.intraday_time_series('activities/heart', base_date=date_str)
    df = pd.DataFrame(data['activities-heart-intraday']['dataset'])
    df['date_time'] = date_str + ' ' + df['time']  # time doesnt inlcude date
    df['date_time'] = pd.to_datetime(df['date_time'])
    df['metric'] = 'heart_rate'
    return df


def make_datasets(client, start_date: datetime, end_date: datetime):
    df_daily_list = []
    df_intraday_list = []
    
    for date in pd.date_range(start_date, end_date):
        date_str = date.date().strftime('%Y-%m-%d')
        
        # Daily Summary
        df = get_daily_summary_df(client, date_str)
        df_daily_list += [df]
        
        # Intraday heart rate timeseries
        df = get_intraday_heart_df(client, date_str)
        df_intraday_list += [df]
        
    df_daily = pd.concat(df_daily_list)
    # TODO - reshape df_daily wide? 
    df_daily = add_date_vars(df_daily)
    
    df_intraday = pd.concat(df_intraday_list)
    df_intraday = add_date_vars(df_intraday)
    
    return df_daily, df_intraday