# Importing PyQt5 components for the window, layout, labels and timer
# Standard library
import datetime
import random
import pickle
import os

# PyQt5
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox, QInputDialog
from PyQt5.QtCore import QTimer, Qt

# Local modules
from signal_visualisation import EEGAcquisition
from feature_extraction import extract_features_from_session, save_features
from classifier import train_classifier, evaluate_classifier, save_model

# The four classes we want to discriminate, each mapped to a Unicode arrow for the cue
CLASSES = {
    "up": "\u2191",
    "down": "\u2193",
    "left": "\u2190",
    "right": "\u2192",
}

# Durations (in milliseconds) of each phase of a trial
FIXATION_DURATION_MSN = 2000
CUE_DURATION_MS = 4000

# Number of trials to collect for each class
TRIALS_PER_CLASS = 20

class CalibrationWindow(QWidget):
    def __init__(self, use_synthetic=True, serial_port=None):
        super().__init__()
        self.setWindowTitle("Calibration")
        self.setMinimumSize(500, 400)

        # Asking the subject's name before starting anything else
        subject_name, ok = QInputDialog.getText(
            self, "Subject Identification", "Enter subject name or ID:"
        )

        # If the user cancels or leaves it empty, we use a default placeholder
        if not ok or not subject_name.strip():
            subject_name = "unknown_subject"
        
        self.subject_name = subject_name.strip().replace(" ","_")

        # Creating the acquisition object, same logic as in monitor_gui.py
        self.acq = EEGAcquisition(use_synthetic=use_synthetic, serial_port=serial_port)

        try:
            self.acq.connect()
        except ConnectionError as e:
            QMessageBox.critical(self, "Board not available", str(e))
            self.connection_failed = True
            return
        
        self.connection_failed = False
        self.acq.start_stream()

        # Building the randomized trial sequence: each class repeated
        # TRIALS_PER_CLASS times, then shuffled so the order is unpredictable
        self.trial_sequence = list(CLASSES.keys()) * TRIALS_PER_CLASS
        random.shuffle(self.trial_sequence)
        self.current_trial_index = 0

        # This list will store one dictionary per trial: the label and the
        # corresponding EEG data collected during the cue phase
        self.collected_data = []

        # Number of samples corresponding to the cue duration, used to pull
        # the right amount of data from the buffer once the trial ends
        self.cue_n_samples = int(self.acq.sampling_rate * (CUE_DURATION_MS / 1000))
        
        self._build_ui()
        self._start_next_trial()

    def _build_ui(self):
        layout = QVBoxLayout()

        # Big central label, used both for the fixation cross and the cue arrow
        self.display_label = QLabel("+")
        self.display_label.setAlignment(Qt.AlignCenter)
        self.display_label.setStyleSheet("font-size: 80px;")
        layout.addWidget(self.display_label)

        # Small label showing progress through the session
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_label)

        self.setLayout(layout)

    def _start_next_trial(self):
        # If we have gone through all trials, end the session
        if self.current_trial_index >= len(self.trial_sequence):
            self._end_session()
            return
        
        self.progress_label.setText(
            f"Trial {self.current_trial_index + 1} / {len(self.trial_sequence)}"
        )

        # Phase 1: fixation cross, just a resting period before the cue appears
        self.display_label.setText("+")
        QTimer.singleShot(FIXATION_DURATION_MSN, self._start_cue_phase)
    
    def _start_cue_phase(self):
        # Determining which class this trial belongs to, and showing its arrow
        current_class = self.trial_sequence[self.current_trial_index]
        arrow = CLASSES[current_class]
        self.display_label.setText(arrow)

        # After the cue duration has elapsed, collect the data and move on
        QTimer.singleShot(CUE_DURATION_MS, lambda: self._collect_trial_data(current_class))

    def _collect_trial_data(self, current_class):
        try:
            data = self.acq.get_latest_data(self.cue_n_samples)
        except Exception:
            # Board disconnected during calibration — stop session gracefully
            self.display_label.setText("Connection lost")
            self.progress_label.setText("Board disconnected. Please restart the session.")
            if self.acq.is_streaming:
                self.acq.stop_stream()
                self.acq.disconnect()
            QMessageBox.critical(
                self, "Connection lost",
                "Connection to the board was lost during calibration.\n"
                "Please check the board and restart the session."
            )
            return

        self.collected_data.append({
            "label": current_class,
            "data": data
        })
        self.current_trial_index += 1
        self._start_next_trial()
        
    def _end_session(self):
        self.display_label.setText("Done!")
        self.progress_label.setText("Processing data, please wait...")

        self.acq.stop_stream()
        self.acq.disconnect()

        os.makedirs("calibration_data", exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"calibration_{self.subject_name}_{timestamp}.pkl"
        save_path = os.path.join("calibration_data", filename)

        session = {
            "trials": self.collected_data,
            "eeg_channels": self.acq.eeg_channels,
            "sampling_rate": self.acq.sampling_rate
        }

        with open(save_path, "wb") as f:
            pickle.dump(session, f)

        # Step 2: extracting features from the saved session
        base_name = save_path.replace(".pkl", "")
        X, y = extract_features_from_session(save_path)
        save_features(X, y, base_name)

        # Step 3: evaluating and training the classifier
        scores = evaluate_classifier(X, y)
        clf, le = train_classifier(X, y)

        # Step 4: saving the model
        model_path = base_name + "_model.joblib"
        save_model(clf, le, model_path)

        # Showing accuracy only if cross-validation was possible
        if scores is not None:
            accuracy_text = f"Cross-validation accuracy: {scores.mean():.2%}"
        else:
            accuracy_text = (
                "Not enough trials for cross-validation.\n"
                "Run 20 trials per class for a reliable estimate."
            )

        QMessageBox.information(
            self,
            "Calibration completed",
            f"Session completed for subject: {self.subject_name}\n\n"
            f"Files saved in: calibration_data/\n"
            f"{accuracy_text}\n\n"
            f"The system is now ready for cursor control."
        )
                
    def closeEvent(self, event):
        if not self.connection_failed and self.acq.is_streaming:
            try:
                self.acq.stop_stream()
                self.acq.disconnect()
            except Exception:
                pass
        event.accept()

# Quick standalone test: python calibration_gui.py
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # For synthetic board testing:
    # window = CalibrationWindow(use_synthetic=True)
    window = CalibrationWindow(use_synthetic=False)

    if not window.connection_failed:
        window.show()
        sys.exit(app.exec_())