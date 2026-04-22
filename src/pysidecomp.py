from typing import List, Optional, Union, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QSlider, QComboBox, QSpinBox, QGroupBox, QCheckBox, 
    QRadioButton, QProgressBar, QFrame, QStackedWidget,
    QPushButton, QScrollArea, QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWebEngineWidgets import QWebEngineView

# --- Constants ---
DEFAULT_SPACING = 10
DEFAULT_MARGIN = 10
SLIDER_MIN = 0
SLIDER_MAX = 100
PROGRESS_PRECISION = 1000  # Used to map [0,1] float to integer range

class LabeledInput(QWidget):
    '''
    A text input paired with a label to its left.

    Inputs
        label_text:  The string to display in the label.
        placeholder: Ghost text shown when the input is empty.
    '''
    def __init__(self, label_text: str, placeholder: str = "") -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label_text)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(placeholder)

        layout.addWidget(self.label)
        layout.addWidget(self.input_field)
        return None

    def text(self) -> str:
        '''
        Returns the current text in the input field.
        '''
        return self.input_field.text()


class LabeledSlider(QWidget):
    '''
    A labeled slider bar with a dynamic value display.

    Inputs
        label_text:  The name of the parameter.
        min_val:     Minimum integer value.
        max_val:     Maximum integer value.
        orientation: Qt.Orientation.Horizontal or Qt.Orientation.Vertical.
    '''
    def __init__(self, label_text: str, min_val: int = 0, max_val: int = 100, 
                 orientation: Qt.Orientation = Qt.Horizontal) -> None:
        super().__init__()
        self.orientation = orientation
        
        # Select layout based on orientation
        if orientation == Qt.Horizontal:
            layout = QHBoxLayout(self)
        else:
            layout = QVBoxLayout(self)
        
        layout.setContentsMargins(0, 0, 0, 0)

        self.name_label = QLabel(label_text)
        self.slider = QSlider(orientation)
        self.slider.setRange(min_val, max_val)
        self.value_label = QLabel(str(self.slider.value()))

        # Arrange components based on requested logic
        if orientation == Qt.Horizontal:
            layout.addWidget(self.name_label)
            layout.addWidget(self.slider)
            layout.addWidget(self.value_label)
        else:
            # Vertical: Value on top, Name on bottom
            layout.addWidget(self.value_label, alignment=Qt.AlignCenter)
            layout.addWidget(self.slider, alignment=Qt.AlignCenter)
            layout.addWidget(self.name_label, alignment=Qt.AlignCenter)

        # Update the value label whenever the slider moves
        self.slider.valueChanged.connect(self._update_label)
        return None

    def _update_label(self, value: int) -> None:
        '''
        Internal helper to update the text display.
        '''
        self.value_label.setText(str(value))
        return None


class LabeledComboBox(QWidget):
    '''
    A dropdown selector paired with a label.

    Inputs
        label_text: The string to display in the label.
        items:      A list of strings for the dropdown options.
    '''
    def __init__(self, label_text: str, items: List[str]) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label_text)
        self.combo = QComboBox()
        self.combo.addItems(items)

        layout.addWidget(self.label)
        layout.addWidget(self.combo)
        return None


class LabeledSpinBox(QWidget):
    '''
    A numeric input with a label.

    Inputs
        label_text: The string to display in the label.
        min_val:    Minimum numeric value.
        max_val:    Maximum numeric value.
    '''
    def __init__(self, label_text: str, min_val: int = 0, max_val: int = 100) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label_text)
        self.spin = QSpinBox()
        self.spin.setRange(min_val, max_val)

        layout.addWidget(self.label)
        layout.addWidget(self.spin)
        return None


class CheckBoxGroup(QGroupBox):
    '''
    A titled container for multiple checkboxes.

    Inputs
        title:  The text displayed on the group border.
        names:  A list of strings for each checkbox label.
    '''
    def __init__(self, title: str, names: List[str]) -> None:
        super().__init__(title)
        layout = QVBoxLayout(self)
        self.checkboxes = {}

        for name in names:
            cb = QCheckBox(name)
            layout.addWidget(cb)
            self.checkboxes[name] = cb
        return None


class RadioButtonGroup(QGroupBox):
    '''
    A titled container for mutually exclusive radio buttons.

    Inputs
        title:  The text displayed on the group border.
        names:  A list of strings for each option.
    '''
    def __init__(self, title: str, names: List[str]) -> None:
        super().__init__(title)
        layout = QVBoxLayout(self)
        self.buttons = []

        for name in names:
            rb = QRadioButton(name)
            layout.addWidget(rb)
            self.buttons.append(rb)
        
        # Set first item as default checked
        if self.buttons:
            self.buttons[0].setChecked(True)
        return None


class StatusBarSimple(QFrame):
    '''
    A lightweight display area for status messages.

    Inputs
        initial_message: The text to show on startup.
    '''
    def __init__(self, initial_message: str = "Ready") -> None:
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)

        self.label = QLabel(initial_message)
        layout.addWidget(self.label)
        return None

    def set_message(self, message: str) -> None:
        '''
        Updates the status text.
        '''
        self.label.setText(message)
        return None


class ProgressBar(QWidget):
    '''
    A progress bar wrapper accepting float values [0.0, 1.0].

    Inputs
        label_text: Optional text to show above the bar.
    '''
    def __init__(self, label_text: str = "") -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if label_text:
            layout.addWidget(QLabel(label_text))

        self.bar = QProgressBar()
        # Scale range to allow for smoother float-to-int mapping
        self.bar.setRange(0, PROGRESS_PRECISION)
        layout.addWidget(self.bar)
        return None

    def set_progress(self, value: float) -> None:
        '''
        Sets progress using a normalized value between 0.0 and 1.0.
        '''
        # Clamp value between 0 and 1
        clamped = max(0.0, min(1.0, value))
        self.bar.setValue(int(clamped * PROGRESS_PRECISION))
        return None


class TwoPanelLayout(QWidget):
    '''
    A generic container that holds two separate panels.

    Inputs
        panel1:      The first QWidget.
        panel2:      The second QWidget.
        orientation: Qt.Horizontal or Qt.Vertical.
    '''
    def __init__(self, panel1: QWidget, panel2: QWidget, 
                 orientation: Qt.Orientation = Qt.Horizontal) -> None:
        super().__init__()
        layout = QHBoxLayout(self) if orientation == Qt.Horizontal else QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Using a Splitter allows the user to resize panels manually
        self.splitter = QSplitter(orientation)
        self.splitter.addWidget(panel1)
        self.splitter.addWidget(panel2)
        
        layout.addWidget(self.splitter)
        return None


class ControlPanel(QFrame):
    '''
    A styled container used to group UI controls.

    Inputs
        title: Optional title for the panel.
    '''
    def __init__(self, title: str = "") -> None:
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.main_layout = QVBoxLayout(self)
        
        if title:
            header = QLabel(f"<b>{title}</b>")
            self.main_layout.addWidget(header)
        return None

    def add_widget(self, widget: QWidget) -> None:
        '''
        Adds a widget to the control panel layout.
        '''
        self.main_layout.addWidget(widget)
        return None


class FigureDisplayArea(QStackedWidget):
    '''
    A dedicated widget for swapping between images, Matplotlib, and Web views.

    Inputs
        None
    '''
    def __init__(self) -> None:
        super().__init__()
        
        # Page 0: Static Image
        self.image_display = QLabel("No Image Loaded")
        self.image_display.setAlignment(Qt.AlignCenter)
        self.addWidget(self.image_display)

        # Page 1: Matplotlib Canvas
        self.mpl_figure = plt.figure()
        self.mpl_canvas = FigureCanvas(self.mpl_figure)
        self.addWidget(self.mpl_canvas)

        # Page 2: Web/Plotly View
        #self.web_view = QWebEngineView()
        #self.addWidget(self.web_view)
        #return None

    def show_image(self, pixmap: QPixmap) -> None:
        '''
        Displays a static image and switches to image view.
        '''
        self.image_display.setPixmap(pixmap.scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        self.setCurrentIndex(0)
        return None

    def get_mpl_figure(self) -> plt.Figure:
        '''
        Returns the matplotlib figure and switches to canvas view.
        '''
        self.setCurrentIndex(1)
        return self.mpl_figure

    def load_html(self, html_content: str) -> None:
        '''
        Renders HTML (e.g. Plotly) and switches to web view.
        '''
        self.web_view.setHtml(html_content)
        self.setCurrentIndex(2)
        return None


class WindowWithFigureAbove(QWidget):
    '''
    A vertical layout with a figure area on top and a control area below.

    Inputs
        figure_area:  A FigureDisplayArea instance.
        control_area: A widget (e.g., ControlPanel) to place below the figure.
    '''
    def __init__(self, figure_area: FigureDisplayArea, control_area: QWidget) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        
        layout.addWidget(figure_area, stretch=3)  # Figure takes more space
        layout.addWidget(control_area, stretch=1)
        return None


class ButtonRow(QWidget):
    '''
    A horizontal row of buttons.

    Inputs
        button_names: List of strings for button labels.
    '''
    def __init__(self, button_names: List[str]) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.buttons = {}

        for name in button_names:
            btn = QPushButton(name)
            layout.addWidget(btn)
            self.buttons[name] = btn
        return None


class ButtonBox(QWidget):
    '''
    A vertical container of ButtonRow objects.

    Inputs
        rows_config: A list where each element is a list of button names.
    '''
    def __init__(self, rows_config: List[List[str]]) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        for row_names in rows_config:
            layout.addWidget(ButtonRow(row_names))
        return None


class CollapsibleSection(QWidget):
    '''
    A section with a toggle button that hides or shows its content.

    Inputs
        title:   The text on the toggle button.
        content: The widget to be collapsed/expanded.
    '''
    def __init__(self, title: str, content: QWidget) -> None:
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.toggle_btn = QPushButton(f"▼ {title}")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(True)
        
        self.content = content
        
        self.layout.addWidget(self.toggle_btn)
        self.layout.addWidget(self.content)

        # Connect the toggle logic
        self.toggle_btn.clicked.connect(self._toggle_state)
        return None

    def _toggle_state(self, checked: bool) -> None:
        '''
        Switches the visibility of the content widget.
        '''
        self.content.setVisible(checked)
        # Update the arrow icon based on state
        prefix = "▼" if checked else "▶"
        # We assume the title follows the first two characters
        clean_title = self.toggle_btn.text()[2:]
        self.toggle_btn.setText(f"{prefix} {clean_title}")
        return None