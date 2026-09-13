# Importing numpy for loading the feature files
import numpy as np

# Importing scikit-learn components for classification and evaluation
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder

# Importing joblib for saving and loading the trained model
import joblib
import os

def load_features(base_path):
    X = np.load(base_path +  "_X.npy")
    y = np.load(base_path + "_y.npy")
    print(f"Loaded X: {X.shape}, y: {y.shape}")
    return X, y

def train_classifier(X, y):

    # LabelEncoder converts string labels to integers:
    # e.g. "down"->0, "left"->1, "right"->2, "up"->3
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # Training the LDA classifier on the full dataset
    clf = LinearDiscriminantAnalysis()
    clf.fit(X, y_encoded)

    print(f"Classifier trained on {X.shape[0]} trials, "
          f"{X.shape[1]} features, "
          f"{len(le.classes_)} classes: {list(le.classes_)}")
    
    return clf, le

def evaluate_classifier(X, y):
    from collections import Counter
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # Minimum trials per class needed for meaningful cross-validation
    min_samples_per_class = min(Counter(y_encoded).values())
    n_classes = len(set(y_encoded))

    # Need at least n_classes + 1 samples per class for LDA to work in each fold
    if min_samples_per_class <= n_classes:
        print("Not enough trials per class for cross-validation — skipping.")
        return None

    n_splits = min(5, min_samples_per_class)
    clf = LinearDiscriminantAnalysis()
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    scores = cross_val_score(clf, X, y_encoded, cv=cv, scoring="accuracy")

    print(f"\n--- Cross-validation results ({n_splits}-fold) ---")
    print(f"Accuracy per fold: {[f'{s:.2%}' for s in scores]}")
    print(f"Mean accuracy: {scores.mean():.2%}")
    print(f"Std deviation: {scores.std():.2%}")
    print(f"--------------------------------------------------\n")

    return scores

def save_model(clf, le, output_path):
    joblib.dump({"classifier": clf, "label_encoder": le}, output_path)
    print(f"Model saved to: {output_path}")

def load_model(model_path):
    model = joblib.load(model_path)
    return model["classifier"], model["label_encoder"]

# Quick standalone test: python classifier.py
if __name__ == "__main__":
    import sys

    calibration_folder = "calibration_data"

    if not os.path.exists(calibration_folder):
        print(f"Folder '{calibration_folder}' not found.")
        print("Please run a calibration session first.")
        sys.exit(1)

    # Asking which subject to process
    subject_name = input("Enter subject name or ID: ").strip().replace(" ", "_")

    if not subject_name:
        print("No subject name provided.")
        sys.exit(1)
    
    # Filtering only the _X.npy files belonging to this subject
    npy_files = [
        f for f in os.listdir(calibration_folder)
        if f.endswith("_X.npy") and subject_name in f
    ]

    if not npy_files:
        print(f"No feature files found for subject '{subject_name}'.")
        print("Please run feature_extraction.py first for this subject.")
        sys.exit(1)

    # Taking the most recent session for this subject
    npy_files.sort()
    latest = npy_files[-1]
    base_path = os.path.join(calibration_folder, latest.replace("_X.npy", ""))

    print(f"Using feature file: {latest}")

    X, y = load_features(base_path)
    evaluate_classifier(X, y)
    clf, le = train_classifier(X, y)

    model_path = base_path + "_model.joblib"
    save_model(clf, le, model_path)