from flask import Flask
from flask import request
from flask import render_template
application = Flask(__name__)


# NLTK requires nltk.download('stopwords') which may complicate deployment - easier to add another pip dep
# from nltk.corpus import stopwords 
# stopwords = [s.upper() for s in stopwords.words('english')]
from stop_words import get_stop_words
stopwords = get_stop_words('english')
from nltk.tokenize import word_tokenize 
from nltk.probability import FreqDist
import re 

# words in nltk stopwords but not stop-words package 
nltk_stopwords = ['I', 'ME', 'MY', 'MYSELF', 'WE', 'OUR', 'OURS', 'OURSELVES', 'YOU', "YOU'RE", "YOU'VE", "YOU'LL", "YOU'D", 'YOUR', 'YOURS', 'YOURSELF', 'YOURSELVES', 'HE', 'HIM', 'HIS', 'HIMSELF', 'SHE', "SHE'S", 'HER', 'HERS', 'HERSELF', 'IT', "IT'S", 'ITS', 'ITSELF', 'THEY', 'THEM', 'THEIR', 'THEIRS', 'THEMSELVES', 'WHAT', 'WHICH', 'WHO', 'WHOM', 'THIS', 'THAT', "THAT'LL", 'THESE', 'THOSE', 'AM', 'IS', 'ARE', 'WAS', 'WERE', 'BE', 'BEEN', 'BEING', 'HAVE', 'HAS', 'HAD', 'HAVING', 'DO', 'DOES', 'DID', 'DOING', 'A', 'AN', 'THE', 'AND', 'BUT', 'IF', 'OR', 'BECAUSE', 'AS', 'UNTIL', 'WHILE', 'OF', 'AT', 'BY', 'FOR', 'WITH', 'ABOUT', 'AGAINST', 'BETWEEN', 'INTO', 'THROUGH', 'DURING', 'BEFORE', 'AFTER', 'ABOVE', 'BELOW', 'TO', 'FROM', 'UP', 'DOWN', 'IN', 'OUT', 'ON', 'OFF', 'OVER', 'UNDER', 'AGAIN', 'FURTHER', 'THEN', 'ONCE', 'HERE', 'THERE', 'WHEN', 'WHERE', 'WHY', 'HOW', 'ALL', 'ANY', 'BOTH', 'EACH', 'FEW', 'MORE', 'MOST', 'OTHER', 'SOME', 'SUCH', 'NO', 'NOR', 'NOT', 'ONLY', 'OWN', 'SAME', 'SO', 'THAN', 'TOO', 'VERY', 'S', 'T', 'CAN', 'WILL', 'JUST', 'DON', "DON'T", 'SHOULD', "SHOULD'VE", 'NOW', 'D', 'LL', 'M', 'O', 'RE', 'VE', 'Y', 'AIN', 'AREN', "AREN'T", 'COULDN', "COULDN'T", 'DIDN', "DIDN'T", 'DOESN', "DOESN'T", 'HADN', "HADN'T", 'HASN', "HASN'T", 'HAVEN', "HAVEN'T", 'ISN', "ISN'T", 'MA', 'MIGHTN', "MIGHTN'T", 'MUSTN', "MUSTN'T", 'NEEDN', "NEEDN'T", 'SHAN', "SHAN'T", 'SHOULDN', "SHOULDN'T", 'WASN', "WASN'T", 'WEREN', "WEREN'T", 'WON', "WON'T", 'WOULDN', "WOULDN'T"]
stopwords += nltk_stopwords
custom_stopwords = ['COULD', 'USE', "'S", "E.G."]
stopwords += custom_stopwords

def corpus_to_word_list(corpus, n=200):
	corpus = corpus.upper()
	word_list = word_tokenize(corpus)
	# Remove punctuation and numbers
	no_punct = re.compile('.*[A-Za-z].*')
	word_list = [w for w in word_list if w not in stopwords and no_punct.match(w)]
	f = FreqDist(word_list)
	f_list = [i[0] for i in f.most_common(n)]
	return ', '.join(f_list)

@application.route('/')
def home():
	return render_template('index.html')


@application.route('/predict',methods=['POST'])
def predict():
	if request.method == 'POST':
		message = request.form['message']
		out = corpus_to_word_list(message)
	return render_template('output.html', prediction = out) 


if __name__ == '__main__':
	# app.run(debug=True)
	application.run(host="0.0.0.0")
