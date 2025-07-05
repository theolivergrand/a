# -*- coding: utf-8 -*-
"""
Image canvas widget for displaying images with UI element overlays.
"""
import logging
from typing import Optional, List, Dict
from pathlib import Path

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor, QPixmap, QFont, QCursor

from ..models.ui_element import AnalysisResult, UIElement
from config.config import config_manager

logger = logging.getLogger(__name__)


class ImageCanvas(QScrollArea):
    """Widget for displaying images with interactive UI element overlays."""
    
    # Signals
    element_clicked = pyqtSignal(int)  # element_id
    element_hovered = pyqtSignal(int, bool)  # element_id, is_hovered
    
    def __init__(self):
        super().__init__()
        
        self._analysis_result: Optional[AnalysisResult] = None
        self._original_pixmap: Optional[QPixmap] = None
        self._scale_factor: float = 1.0
        self._hovered_element_id: Optional[int] = None
        self._selected_element_id: Optional[int] = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the canvas UI."""
        # Create image label
        self._image_label = ImageLabel()
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self._image_label.setText("Изображение не загружено")
        
        # Connect signals
        self._image_label.mouse_moved.connect(self._on_mouse_moved)
        self._image_label.mouse_clicked.connect(self._on_mouse_clicked)
        self._image_label.mouse_left.connect(self._on_mouse_left)
        
        # Set widget
        self.setWidget(self._image_label)
        self.setWidgetResizable(True)
        
        # Configure scroll area
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        logger.info("Image canvas initialized")
    
    def load_image(self, image_path: str) -> bool:
        """Load an image file."""
        try:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                logger.error(f"Failed to load image: {image_path}")
                return False
            
            self._original_pixmap = pixmap
            self._update_display()
            
            logger.info(f"Image loaded: {image_path} ({pixmap.width()}x{pixmap.height()})")
            return True
            
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return False
    
    def set_analysis_result(self, result: AnalysisResult):
        """Set the analysis result to display overlays."""
        self._analysis_result = result
        self._update_display()
        logger.info(f"Analysis result set: {len(result.elements)} elements")
    
    def clear_analysis(self):
        """Clear the analysis result."""
        self._analysis_result = None
        self._hovered_element_id = None
        self._selected_element_id = None
        self._update_display()
    
    def select_element(self, element_id: int):
        """Select an element by ID."""
        self._selected_element_id = element_id
        self._update_display()
    
    def _update_display(self):
        """Update the display with current image and overlays."""
        if not self._original_pixmap:
            return
        
        # Create a copy of the original pixmap
        display_pixmap = self._original_pixmap.copy()
        
        # Draw overlays if analysis result is available
        if self._analysis_result:
            self._draw_overlays(display_pixmap)
        
        # Set the pixmap to label
        self._image_label.setPixmap(display_pixmap)
        self._image_label.resize(display_pixmap.size())
    
    def _draw_overlays(self, pixmap: QPixmap):
        """Draw UI element overlays on the pixmap."""
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        ui_config = config_manager.get_ui_config()
        
        # Draw each element
        for element in self._analysis_result.elements:
            self._draw_element_overlay(painter, element, ui_config)
        
        painter.end()
    
    def _draw_element_overlay(self, painter: QPainter, element: UIElement, ui_config):
        """Draw overlay for a single element."""
        bbox = element.bounding_box
        rect = QRect(bbox.x1, bbox.y1, bbox.width, bbox.height)
        
        # Determine colors and style based on element state
        if element.element_id == self._selected_element_id:
            # Selected element
            color = QColor("#ff0000")  # Red
            pen_width = 3
            alpha = 200
        elif element.element_id == self._hovered_element_id:
            # Hovered element
            color = QColor("#ffff00")  # Yellow
            pen_width = 2
            alpha = 150
        else:
            # Normal element
            color = QColor(ui_config.box_color)  # Green
            pen_width = ui_config.box_width
            alpha = 100
        
        # Set pen
        pen = QPen(color)
        pen.setWidth(pen_width)
        painter.setPen(pen)
        
        # Draw rectangle
        painter.drawRect(rect)
        
        # Draw fill with transparency
        fill_color = QColor(color)
        fill_color.setAlpha(alpha // 4)
        painter.fillRect(rect, fill_color)
        
        # Draw element ID
        self._draw_element_id(painter, element, rect)
    
    def _draw_element_id(self, painter: QPainter, element: UIElement, rect: QRect):
        """Draw element ID label."""
        # Set font
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        painter.setFont(font)
        
        # Background for text
        id_text = str(element.element_id)
        text_rect = painter.fontMetrics().boundingRect(id_text)
        text_rect.adjust(-4, -2, 4, 2)
        text_rect.moveTo(rect.topLeft())
        
        # Draw background
        painter.fillRect(text_rect, QColor("#ffffff"))
        
        # Draw text
        painter.setPen(QPen(QColor("#000000")))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, id_text)
    
    def _get_element_at_point(self, point: QPoint) -> Optional[UIElement]:
        """Get the element at the given point."""
        if not self._analysis_result:
            return None
        
        # Check each element (in reverse order to prioritize top elements)
        for element in reversed(self._analysis_result.elements):
            bbox = element.bounding_box
            if bbox.contains_point(point.x(), point.y()):
                return element
        
        return None
    
    def _on_mouse_moved(self, point: QPoint):
        """Handle mouse movement."""
        element = self._get_element_at_point(point)
        
        new_hovered_id = element.element_id if element else None
        
        if new_hovered_id != self._hovered_element_id:
            # Clear previous hover
            if self._hovered_element_id:
                self.element_hovered.emit(self._hovered_element_id, False)
            
            # Set new hover
            self._hovered_element_id = new_hovered_id
            if self._hovered_element_id:
                self.element_hovered.emit(self._hovered_element_id, True)
            
            # Update cursor
            if element:
                self._image_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            else:
                self._image_label.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            
            self._update_display()
    
    def _on_mouse_clicked(self, point: QPoint):
        """Handle mouse click."""
        element = self._get_element_at_point(point)
        
        if element:
            self.element_clicked.emit(element.element_id)
            logger.info(f"Element clicked: {element.element_id}")
    
    def _on_mouse_left(self):
        """Handle mouse leaving the widget."""
        if self._hovered_element_id:
            self.element_hovered.emit(self._hovered_element_id, False)
            self._hovered_element_id = None
            self._image_label.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self._update_display()


class ImageLabel(QLabel):
    """Custom QLabel that emits mouse events."""
    
    # Signals
    mouse_moved = pyqtSignal(QPoint)
    mouse_clicked = pyqtSignal(QPoint)
    mouse_left = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        self.mouse_moved.emit(event.pos())
        super().mouseMoveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_clicked.emit(event.pos())
        super().mousePressEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave events."""
        self.mouse_left.emit()
        super().leaveEvent(event)
