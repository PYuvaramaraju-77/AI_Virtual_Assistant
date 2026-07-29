import os
import sys
import json

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import model_trainer

print("Loading dataset & checking model status...")
try:
    model, vectorizer = model_trainer.load_model()
except Exception as e:
    print(f"Error loading model: {e}")
    sys.exit(1)

# Retrieve and display training statistics
stats_path = model_trainer.STATS_PATH
if os.path.exists(stats_path):
    with open(stats_path, 'r') as f:
        stats = json.load(f)
    print(f"\n--- PROTOTYPE RESULTS ---")
    print(f"Overall Model Accuracy: {stats['accuracy'] * 100:.2f}%")
    print(f"Total Dataset Samples: {stats['samples_count']}")
    print(f"Trained Intents count: {stats['intents_count']}")
    print(f"Last Training Time: {stats['training_time']:.2f}s\n")
else:
    print("Stats file not found. Run model retraining to update details.\n")

# Simulated User Test CLI loop
print("Enter a test query to classify its intent (Ctrl+C to quit).")
try:
    while True:
        test_query = input("\nEnter a test query: ").strip()
        if not test_query:
            continue
        intent, confidence = model_trainer.predict_intent(test_query)
        print(f"Predicted Intent: '{intent}' (Confidence: {confidence * 100:.2f}%)")
except KeyboardInterrupt:
    print("\nExiting CLI loop. Goodbye!")
except EOFError:
    pass
