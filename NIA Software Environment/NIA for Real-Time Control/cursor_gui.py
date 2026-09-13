# Standard library
import os
import sys
import numpy as np

# PyQt5 for the control panel window
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QMessageBox, QInputDialog, QApplication
)
from PyQt5.QtCore import QTimer, Qt

# PyAutoGUI for controlling the real system mouse cursor
import pyautogui

# Local modules
from signal_visualisation import EEGAcquisition
from feature_extraction import compute_band_power, MU_BAND
from classifier import load_model

# Movement step in pixels per prediction
CURSOR_STEP = 50

# Analysis window duration in seconds (must match calibration)
WINDOW_SECONDS = 4

# Disabling pyautogui fail-safe (moving mouse to corner stops the program)
# Set to True if you want that safety feature enabled
pyautogui.FAILSAFE = True


class CursorWindow(QWidget):
    """
    Control panel for real-time BCI cursor control.
    When active, moves the real system mouse cursor based on
    the LDA classifier predictions from live EEG data.
    Mouse and trackpad remain fully available at all times.
    """

    def __init__(self, use_synthetic=True, serial_port=None):
        super().__init__()
        self.setWindowTitle("Cursor Control")
        self.setFixedSize(400, 300)

        # Asking which subject to load the model for
        subject_name, ok = QInputDialog.getText(
            self, "Subject Identification", "Enter subject name or ID:"
        )
        if not ok or not subject_name.strip():
            self.connection_failed = True
            return

        self.subject_name = subject_name.strip().replace(" ", "_")

        # Loading the most recent trained model for this subject
        model_path = self._find_model(self.subject_name)
        if model_path is None:
            QMessageBox.critical(
                self, "Model not found",
                f"No trained model found for subject '{self.subject_name}'.\n"
                "Please run a calibration session first."
            )
            self.connection_failed = True
            return

        # Loading classifier and label encoder
        self.clf, self.le = load_model(model_path)
        print(f"Model loaded from: {model_path}")

        # Setting up EEG acquisition
        self.acq = EEGAcquisition(use_synthetic=use_synthetic, serial_port=serial_port)
        try:
            self.acq.connect()
        except ConnectionError as e:
            QMessageBox.critical(self, "Board not available", str(e))
            self.connection_failed = True
            return

        self.connection_failed = False
        self.acq.start_stream()
        self.n_samples = int(self.acq.sampling_rate * WINDOW_SECONDS)

        # Timer for periodic predictions (not started yet — waits for Start button)
        self.timer = QTimer()
        self.timer.timeout.connect(self._predict_and_move)

        self._build_ui()

    def _find_model(self, subject_name):
        """
        Finds the most recent .joblib model file for the given subject.
        """
        folder = "calibration_data"
        if not os.path.exists(folder):
            return None

        model_files = [
            f for f in os.listdir(folder)
            if f.endswith("_model.joblib") and subject_name in f
        ]

        if not model_files:
            return None

        model_files.sort()
        return os.path.join(folder, model_files[-1])

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel(f"Subject: {self.subject_name}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Status label
        self.status_label = QLabel("System inactive")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 13px; color: gray;")
        layout.addWidget(self.status_label)

        # Prediction label
        self.prediction_label = QLabel("Prediction: —")
        self.prediction_label.setAlignment(Qt.AlignCenter)
        self.prediction_label.setStyleSheet("font-size: 13px;")
        layout.addWidget(self.prediction_label)

        # Start button
        self.start_button = QPushButton("Start")
        self.start_button.setMinimumHeight(50)
        self.start_button.setStyleSheet("background-color: #2ca02c; color: white; font-size: 14px;")
        self.start_button.clicked.connect(self._start_control)
        layout.addWidget(self.start_button)

        # Stop button (disabled at start)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setMinimumHeight(50)
        self.stop_button.setStyleSheet("background-color: #d62728; color: white; font-size: 14px;")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self._stop_control)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

    def _start_control(self):
        """
        Activates BCI cursor control: starts the prediction timer.
        """
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("System active — BCI controlling cursor")
        self.status_label.setStyleSheet("font-size: 13px; color: green;")
        self.timer.start(WINDOW_SECONDS * 1000)

    def _stop_control(self):
        """
        Deactivates BCI cursor control: stops the prediction timer.
        """
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("System inactive")
        self.status_label.setStyleSheet("font-size: 13px; color: gray;")
        self.prediction_label.setText("Prediction: —")

    def _predict_and_move(self):
        try:
            data = self.acq.get_latest_data(self.n_samples)
        except Exception:
            self.timer.stop()
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.status_label.setText("Connection lost")
            self.status_label.setStyleSheet("font-size: 13px; color: red;")
            QMessageBox.critical(
                self, "Connection lost",
                "Connection to the board was lost.\n"
                "Please check the board and restart the session."
            )
            return

        feature_vector = []
        for ch_index in self.acq.eeg_channels:
            signal = data[ch_index]
            mu_power = compute_band_power(signal, self.acq.sampling_rate, MU_BAND)
            feature_vector.append(mu_power)

        X = np.array(feature_vector).reshape(1, -1)
        y_pred_encoded = self.clf.predict(X)
        direction = self.le.inverse_transform(y_pred_encoded)[0]
        self.prediction_label.setText(f"Prediction: {direction}")

        if direction == "up":
            pyautogui.moveRel(0, -CURSOR_STEP)
        elif direction == "down":
            pyautogui.moveRel(0, CURSOR_STEP)
        elif direction == "left":
            pyautogui.moveRel(-CURSOR_STEP, 0)
        elif direction == "right":
            pyautogui.moveRel(CURSOR_STEP, 0)

    def closeEvent(self, event):
        self.timer.stop()
        if not self.connection_failed and self.acq.is_streaming:
            try:
                self.acq.stop_stream()
                self.acq.disconnect()
            except Exception:
                pass
        event.accept()


# Quick standalone test: python cursor_gui.py
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # For synthetic board testing:
    # window = CursorWindow(use_synthetic=True)
    window = CursorWindow(use_synthetic=False)

    if not window.connection_failed:
        window.show()
        sys.exit(app.exec_())