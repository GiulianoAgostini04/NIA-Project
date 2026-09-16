# NIA for Real-Time Control

Python application for real-time EEG-based cursor control, developed as part of the NIA (Non-Invasive and Adaptable BCI System) project. This module performs live acquisition, feature extraction, and motor imagery classification, translating the results into cursor movements on screen.

## Overview

The application uses EEG signals from the primary motor cortex to control a computer cursor via a four-class motor imagery paradigm (up / down / left / right), based on ERD/ERS analysis in the mu band (8–13 Hz).

## Hardware requirements

- **Board:** OpenBCI Ganglion (4 channels, 200 Hz), connected via Bluetooth native (`GANGLION_NATIVE_BOARD`), no BLED112 dongle required.
- **Electrode placement:** active electrodes at Cz, C1, C3, FC3 (primary motor cortex); REF and GND on the earlobes (bilateral), channel switches SW1–SW4 set to DOWN.

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

This repository intentionally does not include the Python virtual environment (`bci_env/`), the PyInstaller build output (`build/`, `dist/`), or calibration data. These are either regenerated locally (see below) or distributed separately via Releases.

## Getting the compiled application

A ready-to-use standalone executable (no Python installation required) is published in the [Releases](../../releases) section of this repository. Download the latest `NIA BCI for Real-Time Control` release, extract the archive, and run the `.exe` found inside — no environment setup needed. See "Running the application" below for the required calibration → cursor control order.

## Environment setup (for running from source)

Requires Python 3.11.9.

Create and activate a virtual environment:
```
python -m venv bci_env
# Windows
bci_env\Scripts\activate
# Git Bash on Windows
source bci_env/Scripts/activate
```

Install the required dependencies:
```
pip install -r requirements.txt
```

## Running the application

With the virtual environment active:
```
python main.py
```

Typical workflow:

1. Run **calibration** first, providing a subject name. This records EEG data during motor imagery tasks and automatically trains and saves an LDA model (`<subject>_model.joblib`) in `calibration_data/`.
2. Run **cursor control** with the same subject name. The application loads the corresponding model and translates live EEG classification into cursor movements (`CURSOR_STEP = 50 px`, `WINDOW_SECONDS = 4`).

`pyautogui.FAILSAFE` is enabled as a safety measure: moving the mouse to a screen corner immediately stops cursor control.

## Rebuilding the standalone executable

The executable is built with PyInstaller using the provided specification file:
```
pyinstaller main.spec
```
This regenerates the `build/` and `dist/` folders locally; the resulting `dist/main.exe` is not tracked in this repository — it is instead attached to the corresponding [Release](../../releases).

## Known issues

- The Ganglion board does not support simultaneous Bluetooth sessions; connection status is handled reactively rather than through a background connection checker.
- Auricular reference/ground electrodes may introduce ECG contamination into the recorded signal.

---

Part of the master's thesis project **NIA (Non-Invasive and Adaptable BCI System)**, Politecnico di Torino.
