import os
import sys

# Ensure current folder is in Python path to import model_trainer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import model_trainer

def run_training():
    print("Initiating classification model training workflow...")
    try:
        stats = model_trainer.train_and_save_model()
        print(f"\n--- SUCCESS ---")
        print(f"Model saved successfully to models/ folder.")
        print(f"Accuracy: {stats['accuracy'] * 100:.2f}%")
        print(f"Samples count: {stats['samples_count']}")
        print(f"Total intents: {stats['intents_count']}")
        print(f"Training time: {stats['training_time']:.2f}s")
    except Exception as e:
        print(f"\n--- TRAINING FAILED ---")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_training()
