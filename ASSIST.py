import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# 1. Load the Kaggle Bitext Customer Support Dataset
print("Loading dataset...")
script_dir = os.path.dirname(os.path.abspath(__file__))
# Try to resolve path relative to script directory first
csv_path = os.path.join(script_dir, 'dataset', 'Bitext_Sample_Customer_Service_Training_Dataset', 'Training', 'Bitext_Sample_Customer_Service_Training_Dataset.csv')

# Fallbacks if the workspace structure differs or the dataset is moved
if not os.path.exists(csv_path):
    csv_path = os.path.join(script_dir, 'Bitext_Sample_Customer_Service_Training_Dataset.csv')
if not os.path.exists(csv_path):
    csv_path = 'Bitext_Sample_Customer_Service_Training_Dataset.csv'
if not os.path.exists(csv_path):
    csv_path = '20000-Utterances-Training-dataset.csv'

df = pd.read_csv(csv_path)


# 2. Extract input features (utterances) and target labels (intents)
X = df['utterance']
y = df['intent']

# 3. Perform 80/20 Stratified Random Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, stratify=y, random_state=42
)
print(f"Training samples: {len(X_train)} | Testing samples: {len(X_test)}")

# 4. Text Preprocessing & TF-IDF Vectorization
# Converts raw text into a matrix of TF-IDF features, filtering out standard English stop words
vectorizer = TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(1, 2))
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# 5. Initialize and Train the Support Vector Machine (SVM)
print("Training the SVM Intent Classifier...")
svm_classifier = SVC(kernel='linear', C=1.0, random_state=42)
svm_classifier.fit(X_train_vec, y_train)

# 6. Execute Predictions on the hidden 20% testing split
y_pred = svm_classifier.predict(X_test_vec)

# 7. Output Prototype Results
accuracy = accuracy_score(y_test, y_pred)
print(f"\n--- PROTOTYPE RESULTS ---")
print(f"Overall Model Accuracy: {accuracy * 100:.2f}%\n")
print("Detailed Classification Report (Sample of Top Intents):")
print(classification_report(y_test, y_pred))

# Example Inference Function for Web App
def predict_intent(user_input):
    processed_input = vectorizer.transform([user_input])
    prediction = svm_classifier.predict(processed_input)
    return prediction[0]

# Simulated User Test
test_query = "where is my order?"
print(f"\nSimulated Query: '{test_query}'")
print(f"Predicted Intent: '{predict_intent(test_query)}'")
