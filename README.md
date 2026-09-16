# NIA-Project
### Title:
Realisation of an Integrated Digital Environment for Human-Machine Interaction in Brain-Computer Interfaces

## Subtitle:
Design and Development of a Complete BCI Pipeline from Signal Processing to Real-Time Motor Imagery Control

## Context:
Personal project developed independently

## Description:
This project takes the first steps into Brain-Computer Interfaces, focusing on their software side. It involves designing a complete BCI pipeline, aiming to build a stable hardware-software combination and give to end-users a new communication pathway with their digital devices. Named NIA (Non-Invasive and Adaptable), the project starts from the definition of the clinical challenge it addresses. BCI systems can help overcome the effects of neuropathology and neurotrauma that compromise interaction between body and outside world. Combining non-invasive, open-source instrumentation with a digital environment tailored to hardware, experimenter and patient needs makes it possible to build this new pathway. NIA has a two-section architecture. The first is a standalone MATLAB App Designer application combining patient intake, signal visualisation, processing and training, integrating EEGLAB. The experimenter gathers preliminary patient data while visualising raw EEG signals, acquired via an OpenBCI Ganglion board, from the primary motor cortex, then uses EEGLAB to clean the signal and extract feature of Event-Related Desynchronisation (ERD). Then, the patient trains on the neural mechanism used next through a dedicated training session. The second section is a standalone Python 3.11 application built with BrainFlow, following the same logic: checking the raw EEG signal, calibrating the classification algorithm and enabling real-time cursor control via motor imagery.
