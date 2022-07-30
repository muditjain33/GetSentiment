import re
import os
import nltk
import numpy as np
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from . import dictionary 
import joblib
import os
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "Gaussmodel.pkl"
abs_file_path = os.path.join(script_dir, rel_path)
with open(abs_file_path, 'rb') as fo:  # doctest: +ELLIPSIS
    model_from_joblib = joblib.load(fo)
def preprocessing(ytlist):
    yt1=[]
    for i in range(0, len(ytlist)):
        review = re.sub('[^a-zA-Z]', ' ', ytlist[i])
        review = review.lower()
        review = review.split()
        ps = PorterStemmer()
        review = [ps.stem(word) for word in review if not word in set(stopwords.words('english'))]
        review = ' '.join(review)
        yt1.append(review)
    return yt1

def changetonum(word):
    try:
        return dictionary.dictionary[word]
    except:
        return -1

def preprocessing2(yt1):
    yt_corpus1=[]
    for i in yt1:
        lq=[]
        for j in i.split():
            if(changetonum(j)!=-1):
                lq.append(changetonum(j))
        yt_corpus1.append(lq)
    return yt_corpus1

def preprocessing3(yt_corpus1,dim=10000):
    outputs = np.zeros((len(yt_corpus1),dim))
    for i,j in enumerate(yt_corpus1):
        for k in j:
            outputs[i,k] = 1
    return outputs

def predictionfrommodel(outputs):
    return model_from_joblib.predict(outputs)