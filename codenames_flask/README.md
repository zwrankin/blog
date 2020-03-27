# Flask

## Local testing
```
export FLASK_APP=app.py
export FLASK_DEBUG=1
flask run 
```
And navigate to http://127.0.0.1:5000/

## Notes
https://pypi.org/project/stop-words/ has about the same default English stop words as `nltk.corpus.stopwords`, however `nltk` requires additional post-pip downloads which is a complication for deployment.  

## Deployment
Generally follow the steps from the [Deploying a flask application to Elastic Beanstalk docs](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html).  
1) Create local environment, and save 
```
cd ~/github/blog/codenames_flask
conda create -n eb_flask python=3.6 pip
conda activate eb_flask
pip install flask==1.0.2
pip install nltk stop_words
pip freeze > requirements.txt
```
2) Ensure it works locally.  
Run `python application.py` and navigate to `http://127.0.0.1:5000/` in your browser.  


## Resources
https://www.gutenberg.org/
[Jinja templating docs](https://jinja.palletsprojects.com/en/2.11.x/templates/)
- https://towardsdatascience.com/develop-a-nlp-model-in-python-deploy-it-with-flask-step-by-step-744f3bdd7776
- https://realpython.com/flask-by-example-part-3-text-processing-with-requests-beautifulsoup-nltk/
- Deploying to AWS
    - https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/GettingStarted.html
    - https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html

## Next stpes: 
- Revise stripping of punctuation
- Use stemming to combine tenses & plurals (https://www.nltk.org/howto/stem.html)
- TFIDF?
- try deploying to amazon elastic beanstalk
    - may want to add tokenizers to repo as per (https://realpython.com/flask-by-example-part-3-text-processing-with-requests-beautifulsoup-nltk/)
- configurable n words to return?

## Warnings: 
likely will get error that nltk needs to download stuff once deployed... this is what you run locally I don't know what to do remotely. 
```
nltk.download('punkt')
nltk.download('stopwords')
```