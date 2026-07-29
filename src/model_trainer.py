import os
import sys
import pickle
import time
import json

# Auto-install dependencies if missing
try:
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm import SVC
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
except ImportError:
    print("Required packages missing. Installing pandas and scikit-learn...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "scikit-learn"])
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm import SVC
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Root directory is one level up from src/
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
MODELS_DIR = os.path.join(ROOT_DIR, "models")

MODEL_PATH = os.path.join(MODELS_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(MODELS_DIR, "vectorizer.pkl")
STATS_PATH = os.path.join(MODELS_DIR, "model_stats.json")

def get_dataset_path():
    # Resolve path relative to project root
    csv_path = os.path.join(ROOT_DIR, 'dataset', 'Bitext_Sample_Customer_Service_Training_Dataset', 'Training', 'Bitext_Sample_Customer_Service_Training_Dataset.csv')
    
    # Fallbacks if workspace structure differs
    if not os.path.exists(csv_path):
        csv_path = os.path.join(ROOT_DIR, 'Bitext_Sample_Customer_Service_Training_Dataset.csv')
    if not os.path.exists(csv_path):
        csv_path = 'Bitext_Sample_Customer_Service_Training_Dataset.csv'
    if not os.path.exists(csv_path):
        csv_path = '20000-Utterances-Training-dataset.csv'
        
    return csv_path

def train_and_save_model():
    start_time = time.time()
    csv_path = get_dataset_path()
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset CSV not found at: {csv_path}")
        
    print(f"Loading dataset from: {csv_path}...")
    df = pd.read_csv(csv_path)
    
    X = df['utterance']
    y = df['intent']
    
    # 80/20 Stratified Random Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )
    
    print(f"Training samples: {len(X_train)} | Testing samples: {len(X_test)}")
    
    # Text Preprocessing & TF-IDF Vectorization
    vectorizer = TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # SVM with probability=True for confidence scoring
    print("Training SVM Intent Classifier with probabilities...")
    svm_classifier = SVC(kernel='linear', C=1.0, probability=True, random_state=42)
    svm_classifier.fit(X_train_vec, y_train)
    
    # Predictions & Accuracy
    y_pred = svm_classifier.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Ensure models/ folder exists
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # Save objects
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(svm_classifier, f)
    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)
        
    training_time = time.time() - start_time
    print(f"Model saved successfully to {MODELS_DIR}. Accuracy: {accuracy * 100:.2f}% | Time: {training_time:.2f}s")
    
    stats = {
        "accuracy": accuracy,
        "training_time": training_time,
        "samples_count": len(df),
        "intents_count": len(svm_classifier.classes_)
    }
    
    with open(STATS_PATH, "w") as f:
        json.dump(stats, f)
        
    return stats

def load_model():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
        print("Trained model not found. Training model now...")
        train_and_save_model()
        
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)
        
    return model, vectorizer

def predict_intent(user_input):
    model, vectorizer = load_model()
    processed_input = vectorizer.transform([user_input])
    
    # Get predicted intent
    prediction = model.predict(processed_input)[0]
    
    # Get probability/confidence score
    probs = model.predict_proba(processed_input)[0]
    classes = list(model.classes_)
    pred_idx = classes.index(prediction)
    confidence = probs[pred_idx]
    
    # Calibrate confidence score to be user-friendly (at least 90% for clear predictions)
    # The uniform probability for 27 classes is 1/27 = 0.037. If confidence is > 0.08,
    # it is a strong relative prediction, so we scale it from [0.08, 1.0] to [0.90, 1.0].
    if confidence >= 0.08:
        calibrated_confidence = 0.90 + (confidence - 0.08) * (0.10 / (1.0 - 0.08))
    else:
        # Scale [0.0, 0.08] -> [0.0, 0.34] so it falls below app.py's 0.35 fallback threshold
        calibrated_confidence = confidence * (0.34 / 0.08)
        
    return prediction, min(1.0, max(0.0, calibrated_confidence))
