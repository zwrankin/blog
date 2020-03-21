# Fitbit Data
A investigation into my fitbit data. The initial impetus in March 2020 was to assess the impact of social distancing on my activities. Blog post forthcoming.


## Installation
Since the fitbit [client api](https://python-fitbit.readthedocs.io/en/latest/) isn't in the Kaggle default docker, for now I will make a local conda environment with the client and other dependencies for my analysis.  
The API library is not available on PyPI, so you'll have to manually install it locally. 
```
conda create -n fitbit python=3.7 pip
conda activate fitbit
cd ~/github
git clone https://github.com/orcasgit/python-fitbit.git
cd python-fitbit
pip install .
cd ~/github/blog/fitbit/
pip install -r requirements.txt
```
You can then confirm installation by running `pip list` and seeing `fitbit` and `pandas` (which as of 3/18/2020 is a dependency of this blog repo but not the fitbit client package). 


## Authentication
For a complete overview of the auth process see [Fitbit API docs](https://dev.fitbit.com/build/reference/web-api/oauth2/). This explains how to register your application and obtain your client id and secret. Or, refer to a recent [Medium article](https://towardsdatascience.com/using-the-fitbit-web-api-with-python-f29f119621ea) that goes through the process.   
These secrets are saved in a `SECRETS.env` file (that is suppressed from git as per the `.gitignore`). The contents are  
```
export FITBIT_CLIENT_ID="{YOUR SIX DIGIT ID}"
export FITBIT_CLIENT_SECRET="{YOURSECRET}"
```
Set your environment variables (`source SECRETS.env`) before running any scripts or notebooks. Within your python session, you'll need to get access tokens.  
For this project, I incuded the [gather_keys_oauth2.py](https://github.com/orcasgit/python-fitbit/blob/master/gather_keys_oauth2.py) module from the fitbit client repo (which, as of 3/18/2020, is not included in the package itself). The authentication process is then achieved as per the below Usage section. 


## Usage
Here is an exaple of authenticating and fetching data.   
```
import os
import sys
import pandas as pd
import fitbit
BASE_PATH = os.path.join(os.environ['HOME'], 'github/blog/fitbit')
sys.path.append(BASE_PATH)
import gather_keys_oauth2 as Oauth2

FITBIT_CLIENT_ID = os.environ['FITBIT_CLIENT_ID']
FITBIT_CLIENT_SECRET = os.environ['FITBIT_CLIENT_SECRET']

server=Oauth2.OAuth2Server(FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET)
server.browser_authorize()
ACCESS_TOKEN=str(server.fitbit.client.session.token['access_token'])
REFRESH_TOKEN=str(server.fitbit.client.session.token['refresh_token'])

client = fitbit.Fitbit(FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET,
                  oauth2=True,access_token=ACCESS_TOKEN,refresh_token=REFRESH_TOKEN)
data = client.intraday_time_series('activities/heart')
df = pd.DataFrame(data['activities-heart-intraday']['dataset'])
```

There may be a sleeker way achieve authentication using the [FitbitOauth2Client](https://github.com/orcasgit/python-fitbit/blob/master/fitbit/api.py#L20), but the [client docs](https://python-fitbit.readthedocs.io/en/latest/) are somewhat slim and mention the `gather_keys_oauth2.py` module to get the access_token. 
