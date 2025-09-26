import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.datasets import fetch_20newsgroups

# Load dataset
data = fetch_20newsgroups(subset="train", categories=["sci.electronics", "comp.graphics"], remove=("headers", "footers", "quotes"))
X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.2, random_state=42)

# Train Naïve Bayes model
vectorizer = TfidfVectorizer()
nb_model = make_pipeline(vectorizer, MultinomialNB())
nb_model.fit(X_train, y_train)

# Save model
with open("nb_model.pkl", "wb") as f:
    pickle.dump(nb_model, f)

print("✅ New 'nb_model.pkl' saved successfully!")
