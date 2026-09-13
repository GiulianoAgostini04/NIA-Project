import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel)
from PyQt5.QtCore import Qt
from monitor_gui import MonitorWindow
from calibration_gui import CalibrationWindow
from cursor_gui import CursorWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NIA BCI: Real-Time Control")
        self.setFixedSize(750, 550)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("NIA BCI: Real-Time Control")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("Please select the desired mode")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: gray; font-size: 20px")
        layout.addWidget(subtitle)

        signal_monitor = QPushButton("Signal Visualisation")
        signal_monitor.setMinimumHeight(50)
        signal_monitor.clicked.connect(self.open_monitor)
        layout.addWidget(signal_monitor)

        calibration_button = QPushButton("Calibration")
        calibration_button.setMinimumHeight(50)
        calibration_button.clicked.connect(self.open_calibration)
        layout.addWidget(calibration_button)

        cursor_monitor = QPushButton("Cursor Control")
        cursor_monitor.setMinimumHeight(50)
        cursor_monitor.clicked.connect(self.open_cursor_control)
        layout.addWidget(cursor_monitor)

        self.status_label = QLabel("Board status: unknown")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: gray; font-size: 15px;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def _set_status_connected(self):
        self.status_label.setText("Board connected")
        self.status_label.setStyleSheet("color: green; font-size: 15px;")

    def _set_status_disconnected(self):
        self.status_label.setText("Board not connected")
        self.status_label.setStyleSheet("color: red; font-size: 15px;")

    def open_monitor(self):
        # For synthetic board testing:
        # self.monitor_window = MonitorWindow(use_synthetic=True)
        self.monitor_window = MonitorWindow(use_synthetic=False)
        if not self.monitor_window.connection_failed:
            self._set_status_connected()
            self.monitor_window.show()
        else:
            self._set_status_disconnected()

    def open_calibration(self):
        # For synthetic board testing:
        # self.calibration_window = CalibrationWindow(use_synthetic=True)
        self.calibration_window = CalibrationWindow(use_synthetic=False)
        if not self.calibration_window.connection_failed:
            self._set_status_connected()
            self.calibration_window.show()
        else:
            self._set_status_disconnected()

    def open_cursor_control(self):
        # For synthetic board testing:
        # self.cursor_window = CursorWindow(use_synthetic=True)
        self.cursor_window = CursorWindow(use_synthetic=False)
        if not self.cursor_window.connection_failed:
            self._set_status_connected()
            self.cursor_window.show()
        else:
            self._set_status_disconnected()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())