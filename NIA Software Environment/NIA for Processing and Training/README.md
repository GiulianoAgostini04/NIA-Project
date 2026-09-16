# NIA BCI for Processing And Training

MATLAB (App Designer) application for offline EEG signal processing and training, part of the **NIA – Non-Invasive and Adaptable BCI System**.

## Contents of this folder

- `NIA_BCI_v1.mlapp` — main application (`classdef NIA_BCI_v1 < matlab.apps.AppBase`)
- other supporting `.mlapp` / `.m` files
- configuration files and resources required for the build

This folder contains **only the MATLAB source files**. The compiled, ready-to-use application (standalone installer) is **not included in the repository** due to file size, and is instead distributed through this repository's [Releases](../../releases).

## Downloading the compiled application

To use the application without installing MATLAB:

1. Go to the [Releases](../../releases) section of this repository
2. Download `NIA_BCI_v1_ProcessingAndTraining_Installer.exe` from the latest available release
3. Run the installer: it automatically includes the required **MATLAB Runtime**, so MATLAB does not need to be installed on the target machine

> Note: the installer bundles the MATLAB Runtime version required by the build (see `requiredMCRProducts.txt` in the build logs attached to the release). Do not use the standalone `.exe` without the installer on machines that don't already have the correct Runtime installed — it will not work.

## Requirements for development (if modifying the source)

- MATLAB (R2025b or later)
- App Designer
- MATLAB Compiler (to rebuild the executable)
- EEGLAB (integrated as a manual resource in the compiler project)

## Functional overview

- Import of an OpenBCI acquisition session (`.txt`) via file dialog, with folder name validation (`EEG_subject_trial`)
- Reading of `InfoTrial.xlsx` and `InfoSubject.xlsx` to identify active channels and subject data
- Three mutually exclusive operating modes (checkboxes):
  - Display Raw Data
  - Data Processing with EEGLAB
  - Start Training Session
- Error handling via `uialert` and application state reset

## Reference hardware

- OpenBCI Ganglion, 4 channels, 200 Hz, native Bluetooth connection
- Electrodes: Cz, C1, C3, FC3; bilateral auricular reference

---

Part of the master's thesis project **NIA (Non-Invasive and Adaptable BCI System)**, Politecnico di Torino.
