# Importing numpy for matrix operations and file saving
import numpy as np

# Importing scipy for the Welch PSD estimation
from scipy.signal import welch

# Importing pickle and os for loading the calibration file
import pickle
import os

# Frequency band of interest for motor imagery ERD
MU_BAND = (8, 13)

def compute_band_power(signal, sampling_rate, band):
    # welch() splits the signal into overlapping segments, computes the FFT
    # of each, and averages them — more stable than a single FFT
    freqs, psd = welch(signal, fs=sampling_rate, nperseg=sampling_rate)

    # Selecting only the frequency bins that fall within our band of interest
    low, high = band
    band_mask = (freqs>=low) & (freqs <= high)

    # Averaging the PSD values within the band
    band_power = np.mean(psd[band_mask])
    return band_power

def extract_features_from_session(pkl_path):
    # Loading the session dictionary saved by calibration_gui.py
    with open(pkl_path, "rb") as f:
        session = pickle.load(f)
    
    trials = session["trials"]
    eeg_channels = session["eeg_channels"]
    sampling_rate = session["sampling_rate"]
    print(f"Loaded session: {len(trials)} trials. "
          f"{len(eeg_channels)} EEG channels, "
          f"{sampling_rate} Hz")
    
    X = [] # Will collect one feature vector per trial
    y = [] # Will collect one label per trial

    for trial in trials:
        label = trial["label"]
        data = trial["data"]

        # Building the feature vector for this trial:
        # for each EEG channel, compute mu band power only
        feature_vector = []
        for ch_index in eeg_channels:
            signal = data[ch_index]

            # Computing only mu band power for ERD detection
            mu_power = compute_band_power(signal, sampling_rate, MU_BAND)
            feature_vector.append(mu_power)
        
        X.append(feature_vector)
        y.append(label)
    
    # Converting to numpy arrays for scikit-learn compatibility
    X = np.array(X)
    y = np.array(y)

    print(f"feature matrix X shape: {X.shape}")
    print(f"Label vector y shape: {y.shape}")
    print(f"features per trial: {X.shape[1]} "
          f"({len(eeg_channels)} channels x 1 band)")
        
    return X, y

def save_features(X, y, output_path):

    np.save(output_path + "_X.npy", X)
    np.save(output_path + "_y.npy", y)
    print(f"features saved to: {output_path}_X.npy and {output_path}_y.npy")

# Quick standalone test: python feature_extraction.py
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
    
    # Filtering only the pkl files belonging to this subject
    pkl_files = [
        f for f in os.listdir(calibration_folder)
        if f.endswith(".pkl") and subject_name in f
    ]

    if not pkl_files:
        print(f"No calibration files found for subject '{subject_name}'.")
        sys.exit(1)

    # Taking the most recent session for this subject
    pkl_files.sort()
    latest_file = pkl_files[-1]
    pkl_path = os.path.join(calibration_folder, latest_file)

    print(f"Using calibration file: {latest_file}")

    X, y = extract_features_from_session(pkl_path)

    base_name = pkl_path.replace(".pkl", "")
    save_features(X, y, base_name)

    