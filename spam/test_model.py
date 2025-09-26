import pickle

with open("nb_model.pkl", "rb") as f:
    try:
        nb_model = pickle.load(f)
        print("✅ Model loaded successfully!")
    except Exception as e:
        print("❌ Error loading model:", e)
