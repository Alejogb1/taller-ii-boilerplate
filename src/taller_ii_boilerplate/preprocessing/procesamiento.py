import re
import string
import nltk
import contractions
import emoji
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import pandas as pd
from pathlib import Path
import ssl


#https://stackoverflow.com/questions/38916452/nltk-download-ssl-certificate-verify-failed
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# descargamos NLTK 
nltk.download('punkt_tab')
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("omw-1.4")


lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

Topics = {
    "positive": ["good", "great", "love", "excellent", "amazing"],
    "negative": ["bad", "worst", "hate", "awful", "poor"],
    "service":  ["service", "staff", "support", "help"],
    "product":  ["product", "item", "quality", "price"]
}

def detect_topic(Tokens):
    """Detecta el tema más probable según palabras clave."""
    scores = {}
    for t, keywords in Topics.items():
        scores[t] = sum(token in keywords for token in Tokens)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "other"

def procesar_texto(text):
    if not isinstance(text, str):
        return []

    # tags html
    text = re.sub(r'<.*?>', '', text)

    # urls links
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

    #  contractions son un tipo de palabra
    text = contractions.fix(text)

    # emojis
    text = emoji.demojize(text)
    text = re.sub(r':\S+:', '', text) # Remove the colons around emoji text

    #  numeros
    text = re.sub(r'\d+', '', text)

    # puntuacion
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'[^\w\s]', '', text) # Remove any remaining non-alphanumeric, non-space characters

    # minusculas
    text = text.lower()

    # espacios extra
    text = re.sub(r'\s+', ' ', text).strip()

    # tokenizacion
    tokens = nltk.word_tokenize(text)

    # palabras stop
    tokens = [w for w in tokens if w not in stop_words]

    # lemmatization
    tokens = [lemmatizer.lemmatize(w) for w in tokens]

    return tokens


def lematizacion(text):
    tokens = nltk.word_tokenize(text)

    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]

    return lemmatized_tokens

def process_dataset(input_path="data/raw/revis.csv", 
                    output_path="data/processed/processed_reviews.csv"):

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    df = pd.read_csv(input_path)
    
    df["processed_text"] = df["Comentario"].apply(procesar_texto)
    df["lemmatized_text"] = df["Comentario"].apply(lematizacion)
    df["topic"] = df["lemmatized_text"].apply(detect_topic)
    
    df.to_csv(output_path, index=False)

if __name__ == "__main__":
    process_dataset()
