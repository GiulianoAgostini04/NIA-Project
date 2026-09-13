# Importing PyQt5 components to build the window, the layout and the time
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox, QScrollArea
from PyQt5.QtCore import QTimer

# Import the necessary elements for graphs plotting
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Importing the prepared class
from signal_visualisation import EEGAcquisition

CHANNEL_COLOURS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
    "#bcbd22", "#17becf", "#393b79", "#637939",
    "#8c6d31", "#843c39", "#7b4173", "#3182bd"
]

class MonitorWindow(QWidget):

    # Costructing the window GUI
    def __init__(self, use_synthetic=True, serial_port=None):
        super().__init__()
        self.setWindowTitle("EEG Signal Monitoring")
        self.setMinimumSize(800, 700)

        # Making the objects for the acquisition and starting it
        self.acq = EEGAcquisition(use_synthetic=use_synthetic, serial_port=serial_port)
        
        try:
            self.acq.connect()
        except ConnectionError as e:
            QMessageBox.critical(self, "Board not available", str(e))
            self.connection_failed = True
            return
        
        self.connection_failed = False
        self.acq.start_stream()

        # Calculating the necessary samples contained in 4 seconds
        self.window_seconds = 4
        self.n_samples = int(self.acq.sampling_rate * self.window_seconds)

        # Calling the method that creates the interface
        self._build_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(4000)
    
    def closeEvent(self, event):
        self.timer.stop()
        if not self.connection_failed:
            try:
                self.acq.stop_stream()
                self.acq.disconnect()
            except Exception:
                pass
        event.accept()

    # Creating the refreshing timer    
    def _build_ui(self):
        main_layout = QVBoxLayout()

        # Creation of the info label that explains the activated channels
        info_label = QLabel(
            f"Active Channels: {len(self.acq.eeg_channels)} | "
            f"Sampling Rate: {self.acq.sampling_rate} Hz"
        )
        main_layout.addWidget(info_label)

        n_channels = len(self.acq.eeg_channels)
        # self.figure = Figure(figsize=(6, 2*n_channels))
        # self.canvas = FigureCanvas(self.figure)
        # layout.addWidget(self.canvas)

        height_per_channel = 2.2
        self.figure = Figure(figsize=(7, height_per_channel * n_channels))
        self.canvas = FigureCanvas(self.figure)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.canvas)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        # Loop that creates a subgraph for each channel
        self.axes = []
        for i in range(n_channels):
            ax = self.figure.add_subplot(n_channels, 1, i + 1)
            ax.set_ylabel(f"Ch {i + 1}\n(µV)", fontsize=8)
            ax.set_xlabel("Samples", fontsize=8)
            ax.grid(True, linewidth=0.4, alpha=0.6)
            ax.tick_params(labelsize=7)
            self.axes.append(ax)

        # Managing the spaces between the graphs    
        self.figure.tight_layout()
        self.setLayout(main_layout)

    def update_plots(self):
        try:
            data = self.acq.get_latest_data(self.n_samples)
        except Exception:
            # Board disconnected during streaming — stop the timer gracefully
            self.timer.stop()
            QMessageBox.critical(
                self, "Connection lost",
                "Connection to the board was lost.\n"
                "Please check the board and restart the session."
            )
            return

        for i, channel_index in enumerate(self.acq.eeg_channels):
            ax = self.axes[i]
            ax.clear()
            color = CHANNEL_COLOURS[i % len(CHANNEL_COLOURS)]
            ax.plot(data[channel_index], linewidth=0.8, color=color)
            ax.set_ylabel(f"Ch {i + 1}\n(µV)", fontsize=8)
            ax.set_xlabel("Samples", fontsize=8)
            ax.grid(True, linewidth=0.4, alpha=0.6)
            ax.tick_params(labelsize=7)

        self.canvas.draw()

# Creation of the application    
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # For synthetic board testing:
    # window = MonitorWindow(use_synthetic=True)
    window = MonitorWindow(use_synthetic=False)

    if not window.connection_failed:
        window.show()
        sys.exit(app.exec_())