# NIA for Real-Time Control

Python application for real-time EEG-based cursor control, developed as part of the NIA (Non-Invasive and Adaptable BCI System) project. This module performs live acquisition, feature extraction, and motor imagery classification, translating the results into cursor movements on screen.

## Overview

The application uses EEG signals from the primary motor cortex to control a computer cursor via a four-class motor imagery paradigm (up / down / left / right), based on ERD/ERS analysis in the mu band (8–13 Hz).

## Hardware requirements

- **Board:** OpenBCI Ganglion (4 channels, 200 Hz), connected via Bluetooth native (`GANGLION_NATIVE_BOARD`), no BLED112 dongle required.
- **Electrode placement:** active electrodes at Cz, C1, C3, FC1 (primary motor cortex); REF and GND on the earlobes (bilateral), channel switches SW1–SW4 set to DOWN.

## Repository contents

| File | Purpose |
|---|---|
| `main.py` | Application entry point. |
| `signal_visualisation.py` | Defines `EEGAcquisition`, the shared acquisition class used by both the calibration and cursor-control modules. |
| `monitor_gui.py` | Live signal monitoring interface. |
| `calibration_gui.py` | Orchestrates a calibration session: feature extraction, LDA training, cross-validation, and model saving. |
| `feature_extraction.py` | Extracts mu-band features from EEG windows. |
| `classifier.py` | LDA classifier used for motor imagery prediction. |
| `cursor_gui.py` | Real-time classification and cursor control via `pyautogui`. |
| `main.spec` | PyInstaller specification used to build the standalone executable. |
| `requirements.txt` | Exact Python package versions required to reproduce the development environment. |

This repository intentionally does **not** include the Python virtual environment (`bci_env/`) or the PyInstaller build output (`build/`, `dist/`). These are regenerated locally, as described below, to keep the repository lightweight.

## Environment setup

Requires **Python 3.11.9**.

1. Create and activate a virtual environment:
   ```bash
   python -m venv bci_env
   # Windows
   bci_env\Scripts\activate
   # Git Bash on Windows
   source bci_env/Scripts/activate
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the application

With the virtual environment active:

```bash
python main.py
```

**Typical workflow:**

1. Run **calibration** first, providing a subject name. This records EEG data during motor imagery tasks and automatically trains and saves an LDA model (`<subject>_model.joblib`) in `calibration_data/`.
2. Run **cursor control** with the same subject name. The application loads the corresponding model and translates live EEG classification into cursor movements (`CURSOR_STEP = 50` px, `WINDOW_SECONDS = 4`).

`pyautogui.FAILSAFE` is enabled as a safety measure: moving the mouse to a screen corner immediately stops cursor control.

## Rebuilding the standalone executable

The executable is built with PyInstaller using the provided specification file:

```bash
pyinstaller main.spec
```

This regenerates the `build/` and `dist/` folders locally; the resulting `dist/main.exe` is not tracked in this repository.

## Known issues

- The Ganglion board does not support simultaneous Bluetooth sessions; connection status is handled reactively rather than through a background connection checker.
- Auricular reference/ground electrodes may introduce ECG contamination into the recorded signal.
