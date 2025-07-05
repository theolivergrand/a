# -*- coding: utf-8 -*-
"""
Main window for the Desktop UI/UX Analyzer application.
"""
import logging
from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QFileDialog, QLabel, QTextEdit, QSplitter, QGroupBox,
    QListWidget, QListWidgetItem, QMessageBox, QMenuBar, QMenu,
    QStatusBar, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QPixmap

from ..controllers.app_controller import app_controller
from ..models.ui_element import AnalysisResult
from .image_canvas import ImageCanvas
from config.config import config_manager

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window with refactored, modular design."""
    
    # Signals
    analysis_started = pyqtSignal()
    analysis_completed = pyqtSignal(AnalysisResult)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._current_analysis: Optional[AnalysisResult] = None
        self._progress_bar: Optional[QProgressBar] = None
        
        self._setup_ui()
        self._setup_connections()
        self._setup_controller_callbacks()
        
        logger.info("Main window initialized")
    
    def _setup_ui(self):
        """Setup the user interface."""
        ui_config = config_manager.get_ui_config()
        
        # Window properties
        self.setWindowTitle(ui_config.window_title)
        self.setGeometry(100, 100, ui_config.window_width, ui_config.window_height)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layouts
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel (controls and results)
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel (image canvas)
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 1)  # Left panel
        splitter.setStretchFactor(1, 2)  # Right panel (image area)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create status bar
        self._create_status_bar()
    
    def _create_left_panel(self) -> QWidget:
        """Create the left control panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # File controls group
        file_group = QGroupBox("Загрузка файла")
        file_layout = QVBoxLayout(file_group)
        
        self.load_button = QPushButton("📁 Выбрать изображение")
        self.load_button.setMinimumHeight(40)
        file_layout.addWidget(self.load_button)
        
        self.file_label = QLabel("Файл не выбран")
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet("color: gray; font-style: italic;")
        file_layout.addWidget(self.file_label)
        
        layout.addWidget(file_group)
        
        # Analysis controls group
        analysis_group = QGroupBox("Анализ")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.analyze_button = QPushButton("🤖 Анализировать UI")
        self.analyze_button.setMinimumHeight(40)
        self.analyze_button.setEnabled(False)
        analysis_layout.addWidget(self.analyze_button)
        
        layout.addWidget(analysis_group)
        
        # Results group
        results_group = QGroupBox("Результаты")
        results_layout = QVBoxLayout(results_group)
        
        self.elements_list = QListWidget()
        self.elements_list.setMaximumHeight(200)
        results_layout.addWidget(self.elements_list)
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        self.export_json_button = QPushButton("📄 JSON")
        self.export_json_button.setEnabled(False)
        export_layout.addWidget(self.export_json_button)
        
        self.export_txt_button = QPushButton("📝 TXT")
        self.export_txt_button.setEnabled(False)
        export_layout.addWidget(self.export_txt_button)
        
        results_layout.addLayout(export_layout)
        layout.addWidget(results_group)
        
        # Details group
        details_group = QGroupBox("Детали элемента")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(150)
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(details_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Create the right image panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Image canvas
        self.image_canvas = ImageCanvas()
        layout.addWidget(self.image_canvas)
        
        return panel
    
    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("Файл")
        
        open_action = QAction("Открыть изображение", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._load_image)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Analysis menu
        analysis_menu = menubar.addMenu("Анализ")
        
        analyze_action = QAction("Анализировать", self)
        analyze_action.setShortcut(QKeySequence("Ctrl+A"))
        analyze_action.triggered.connect(self._analyze_image)
        analysis_menu.addAction(analyze_action)
        
        # Export menu
        export_menu = menubar.addMenu("Экспорт")
        
        export_json_action = QAction("Экспорт JSON", self)
        export_json_action.triggered.connect(self._export_json)
        export_menu.addAction(export_json_action)
        
        export_txt_action = QAction("Экспорт TXT", self)
        export_txt_action.triggered.connect(self._export_txt)
        export_menu.addAction(export_txt_action)
        
        # Help menu
        help_menu = menubar.addMenu("Справка")
        
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Progress bar for analysis
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self._progress_bar)
        
        self.status_bar.showMessage("Готов к работе")
    
    def _setup_connections(self):
        """Setup signal-slot connections."""
        # Button connections
        self.load_button.clicked.connect(self._load_image)
        self.analyze_button.clicked.connect(self._analyze_image)
        self.export_json_button.clicked.connect(self._export_json)
        self.export_txt_button.clicked.connect(self._export_txt)
        
        # List connections
        self.elements_list.itemClicked.connect(self._on_element_selected)
        
        # Canvas connections
        self.image_canvas.element_clicked.connect(self._on_canvas_element_clicked)
        self.image_canvas.element_hovered.connect(self._on_canvas_element_hovered)
        
        # Internal signals
        self.analysis_started.connect(self._on_analysis_started)
        self.analysis_completed.connect(self._on_analysis_completed)
        self.error_occurred.connect(self._on_error_occurred)
    
    def _setup_controller_callbacks(self):
        """Setup callbacks with the application controller."""
        app_controller.add_analysis_callback(self._on_controller_analysis_completed)
        app_controller.add_error_callback(self._on_controller_error)
    
    def _load_image(self):
        """Load an image file."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "Изображения (*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp)"
        )
        
        if file_path:
            if app_controller.load_image(file_path):
                # Update UI
                self.file_label.setText(f"Файл: {Path(file_path).name}")
                self.file_label.setStyleSheet("color: green;")
                self.analyze_button.setEnabled(True)
                
                # Load image to canvas
                self.image_canvas.load_image(file_path)
                
                # Clear previous results
                self._clear_results()
                
                self.status_bar.showMessage(f"Загружено: {Path(file_path).name}")
                logger.info(f"Image loaded: {file_path}")
    
    def _analyze_image(self):
        """Start image analysis."""
        if app_controller.get_current_image():
            self.analysis_started.emit()
            
            # Start analysis in controller
            QTimer.singleShot(100, app_controller.analyze_current_image)
    
    def _export_json(self):
        """Export analysis results as JSON."""
        if not self._current_analysis:
            return
        
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self,
            "Сохранить JSON",
            "analysis_results.json",
            "JSON файлы (*.json)"
        )
        
        if file_path:
            if app_controller.export_analysis(file_path, "json"):
                self.status_bar.showMessage(f"Экспорт JSON завершен: {Path(file_path).name}")
            else:
                self.error_occurred.emit("Ошибка экспорта JSON")
    
    def _export_txt(self):
        """Export analysis results as text."""
        if not self._current_analysis:
            return
        
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self,
            "Сохранить TXT",
            "analysis_results.txt",
            "Текстовые файлы (*.txt)"
        )
        
        if file_path:
            if app_controller.export_analysis(file_path, "txt"):
                self.status_bar.showMessage(f"Экспорт TXT завершен: {Path(file_path).name}")
            else:
                self.error_occurred.emit("Ошибка экспорта TXT")
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "О программе",
            """
            <h3>Desktop UI/UX Analyzer v2.0</h3>
            <p>Интеллектуальный анализатор пользовательских интерфейсов</p>
            <p>Использует Google Gemini AI для автоматического обнаружения UI элементов</p>
            <p><b>Особенности:</b></p>
            <ul>
            <li>Автоматическое обнаружение UI элементов</li>
            <li>Интерактивная визуализация</li>
            <li>Экспорт результатов</li>
            <li>Модульная архитектура</li>
            </ul>
            """
        )
    
    def _clear_results(self):
        """Clear analysis results."""
        self._current_analysis = None
        self.elements_list.clear()
        self.details_text.clear()
        self.image_canvas.clear_analysis()
        self.export_json_button.setEnabled(False)
        self.export_txt_button.setEnabled(False)
    
    def _on_analysis_started(self):
        """Handle analysis start."""
        self.analyze_button.setEnabled(False)
        self.analyze_button.setText("⏳ Анализ...")
        self._progress_bar.setVisible(True)
        self._progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_bar.showMessage("Выполняется анализ...")
        logger.info("Analysis started")
    
    def _on_analysis_completed(self, result: AnalysisResult):
        """Handle analysis completion."""
        self._current_analysis = result
        
        # Update UI
        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("🤖 Анализировать UI")
        self._progress_bar.setVisible(False)
        
        # Populate elements list
        self._populate_elements_list(result)
        
        # Update canvas
        self.image_canvas.set_analysis_result(result)
        
        # Enable export buttons
        self.export_json_button.setEnabled(True)
        self.export_txt_button.setEnabled(True)
        
        # Update status
        self.status_bar.showMessage(f"Анализ завершен: найдено {len(result.elements)} элементов")
        logger.info(f"Analysis completed: {len(result.elements)} elements")
    
    def _on_error_occurred(self, error_message: str):
        """Handle error occurrence."""
        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("🤖 Анализировать UI")
        self._progress_bar.setVisible(False)
        
        QMessageBox.critical(self, "Ошибка", error_message)
        self.status_bar.showMessage("Ошибка анализа")
        logger.error(f"Error occurred: {error_message}")
    
    def _populate_elements_list(self, result: AnalysisResult):
        """Populate the elements list widget."""
        self.elements_list.clear()
        
        for element in result.elements:
            item_text = f"{element.element_id}. {element.element_type.value.upper()}: {element.description[:50]}..."
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, element.element_id)
            self.elements_list.addItem(item)
    
    def _on_element_selected(self, item: QListWidgetItem):
        """Handle element selection from list."""
        element_id = item.data(Qt.ItemDataRole.UserRole)
        if element_id and self._current_analysis:
            element = self._current_analysis.get_element_by_id(element_id)
            if element:
                # Update details
                self._show_element_details(element)
                
                # Select in controller and canvas
                app_controller.select_element(element_id)
                self.image_canvas.select_element(element_id)
    
    def _on_canvas_element_clicked(self, element_id: int):
        """Handle element click from canvas."""
        if self._current_analysis:
            element = self._current_analysis.get_element_by_id(element_id)
            if element:
                # Update details
                self._show_element_details(element)
                
                # Select in controller
                app_controller.select_element(element_id)
                
                # Update list selection
                for i in range(self.elements_list.count()):
                    item = self.elements_list.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) == element_id:
                        self.elements_list.setCurrentItem(item)
                        break
    
    def _on_canvas_element_hovered(self, element_id: int, is_hovered: bool):
        """Handle element hover from canvas."""
        app_controller.hover_element(element_id, is_hovered)
    
    def _show_element_details(self, element):
        """Show element details in the details text widget."""
        details = f"""
<b>Элемент {element.element_id}</b><br>
<b>Тип:</b> {element.element_type.value.upper()}<br>
<b>Описание:</b> {element.description}<br>
<b>Координаты:</b> ({element.bounding_box.x1}, {element.bounding_box.y1}) - ({element.bounding_box.x2}, {element.bounding_box.y2})<br>
<b>Размер:</b> {element.bounding_box.width} x {element.bounding_box.height} px<br>
<b>Центр:</b> {element.bounding_box.center}<br>
        """.strip()
        
        self.details_text.setHtml(details)
    
    def _on_controller_analysis_completed(self, result: AnalysisResult):
        """Callback from controller when analysis is completed."""
        self.analysis_completed.emit(result)
    
    def _on_controller_error(self, error_message: str):
        """Callback from controller when error occurs."""
        self.error_occurred.emit(error_message)
