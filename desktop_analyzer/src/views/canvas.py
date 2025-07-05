# -*- coding: utf-8 -*-
"""
Canvas widget for displaying and interacting with UI analysis results.
"""
from typing import Optional, List, Tuple
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QCursor, QFont
from PIL import Image

from ..models.data_models import BoundingBox, AnalysisResult, Rectangle
from ...config.config import config_manager


class ImageCanvas(QWidget):
    """Canvas widget for displaying image with interactive bounding boxes."""
    
    element_selected = pyqtSignal(str)  # element_id
    element_hovered = pyqtSignal(str)   # element_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui_config = config_manager.get_ui_config()
        
        # Data
        self.original_image: Optional[Image.Image] = None
        self.scaled_pixmap: Optional[QPixmap] = None
        self.analysis_result: Optional[AnalysisResult] = None
        self.scale_factor: float = 1.0
        self.image_offset: QPoint = QPoint(0, 0)
        
        # Interaction state
        self.dragging_element: Optional[BoundingBox] = None
        self.resizing_element: Optional[BoundingBox] = None
        self.drag_start_pos: Optional[QPoint] = None
        self.last_mouse_pos: Optional[QPoint] = None
        
        # Setup UI
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the canvas UI."""
        self.setMinimumSize(400, 300)
        self.setMouseTracking(True)
        self.setStyleSheet(f"background-color: {self.ui_config.canvas_background_color};")
        
        # Tooltip
        self.setToolTip("Загрузите изображение для анализа")
    
    def set_image(self, image: Image.Image):
        """Set the image to display."""
        self.original_image = image
        self._update_scaled_image()
        self.update()
    
    def set_analysis_result(self, result: AnalysisResult):
        """Set the analysis result to display."""
        self.analysis_result = result
        self._update_element_positions()
        self.update()
    
    def clear(self):
        """Clear the canvas."""
        self.original_image = None
        self.scaled_pixmap = None
        self.analysis_result = None
        self.update()
    
    def _update_scaled_image(self):
        """Update the scaled pixmap."""
        if not self.original_image:
            return
        
        # Convert PIL to QPixmap
        if self.original_image.mode != 'RGB':
            rgb_image = self.original_image.convert('RGB')
        else:
            rgb_image = self.original_image
        
        # Create QPixmap
        qimage = rgb_image.toqimage()
        full_pixmap = QPixmap.fromImage(qimage)
        
        # Scale to fit widget
        widget_size = self.size()
        scaled_pixmap = full_pixmap.scaled(
            widget_size, Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.scaled_pixmap = scaled_pixmap
        self.scale_factor = scaled_pixmap.width() / full_pixmap.width()
        
        # Calculate image offset for centering
        self.image_offset = QPoint(
            (widget_size.width() - scaled_pixmap.width()) // 2,
            (widget_size.height() - scaled_pixmap.height()) // 2
        )
    
    def _update_element_positions(self):
        """Update element positions based on current scale."""
        if not self.analysis_result or not self.scaled_pixmap:
            return
        
        for element in self.analysis_result.elements:
            # Convert Rectangle to QRect with scaling
            orig_rect = element.rect
            scaled_rect = QRect(
                int(orig_rect.x * self.scale_factor) + self.image_offset.x(),
                int(orig_rect.y * self.scale_factor) + self.image_offset.y(),
                int(orig_rect.width * self.scale_factor),
                int(orig_rect.height * self.scale_factor)
            )
            
            # Update element's scaled_rect (convert back to Rectangle)
            element.scaled_rect = Rectangle(
                x=scaled_rect.x(),
                y=scaled_rect.y(),
                width=scaled_rect.width(),
                height=scaled_rect.height()
            )
            
            # Update resize handles
            element.update_resize_handles()
    
    def _get_element_at_position(self, pos: QPoint) -> Optional[BoundingBox]:
        """Get element at the given position."""
        if not self.analysis_result:
            return None
        
        for element in reversed(self.analysis_result.elements):  # Check top elements first
            if element.contains(pos.x(), pos.y()):
                return element
        return None
    
    def paintEvent(self, event):
        """Paint the canvas."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw image
        if self.scaled_pixmap:
            painter.drawPixmap(self.image_offset, self.scaled_pixmap)
        
        # Draw bounding boxes
        if self.analysis_result:
            self._draw_bounding_boxes(painter)
        
        # Draw instructions if no image
        if not self.original_image:
            self._draw_instructions(painter)
    
    def _draw_bounding_boxes(self, painter: QPainter):
        """Draw bounding boxes for all elements."""
        for element in self.analysis_result.elements:
            if not element.scaled_rect:
                continue
            
            # Set pen color based on state
            if element.is_selected:
                color = QColor(255, 0, 0, 200)  # Red for selected
                width = self.ui_config.box_width + 1
            elif element.is_hovered:
                color = QColor(255, 255, 0, 200)  # Yellow for hovered
                width = self.ui_config.box_width + 1
            else:
                color = QColor(0, 255, 0, 150)  # Green for normal
                width = self.ui_config.box_width
            
            pen = QPen(color, width)
            painter.setPen(pen)
            
            # Draw rectangle
            rect = element.scaled_rect
            qrect = QRect(rect.x, rect.y, rect.width, rect.height)
            painter.drawRect(qrect)
            
            # Draw element ID
            font = QFont()
            font.setPointSize(10)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            
            # Draw background for text
            text = element.element_id
            metrics = painter.fontMetrics()
            text_rect = metrics.boundingRect(text)
            bg_rect = QRect(rect.x, rect.y - text_rect.height() - 2, 
                           text_rect.width() + 4, text_rect.height() + 2)
            painter.fillRect(bg_rect, QColor(0, 0, 0, 180))
            
            # Draw text
            painter.drawText(rect.x + 2, rect.y - 2, text)
            
            # Draw resize handles for selected elements
            if element.is_selected:
                self._draw_resize_handles(painter, element)
    
    def _draw_resize_handles(self, painter: QPainter, element: BoundingBox):
        """Draw resize handles for an element."""
        painter.setPen(QPen(QColor(255, 0, 0), 1))
        painter.setBrush(QColor(255, 255, 255, 200))
        
        for handle_rect in element.resize_handles.values():
            qrect = QRect(handle_rect.x, handle_rect.y, handle_rect.width, handle_rect.height)
            painter.drawRect(qrect)
    
    def _draw_instructions(self, painter: QPainter):
        """Draw instructions when no image is loaded."""
        painter.setPen(QPen(QColor(128, 128, 128), 1))
        font = QFont()
        font.setPointSize(14)
        painter.setFont(font)
        
        text = "Загрузите изображение для анализа\n\nПоддерживаемые форматы:\nPNG, JPG, JPEG, BMP, GIF, TIFF, WEBP"
        rect = self.rect()
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() != Qt.MouseButton.LeftButton:
            return
        
        pos = event.pos()
        element = self._get_element_at_position(pos)
        
        if element:
            # Check for resize handle
            handle = element.get_resize_handle_at(pos.x(), pos.y())
            if handle and element.is_selected:
                self.resizing_element = element
                element.is_resizing = True
                element.resize_handle = handle
                self._update_cursor(handle)
            else:
                # Start dragging
                self.dragging_element = element
                element.is_dragging = True
                self.drag_start_pos = pos
            
            # Emit selection signal
            self.element_selected.emit(element.element_id)
        
        self.last_mouse_pos = pos
        self.update()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        pos = event.pos()
        
        # Handle resizing
        if self.resizing_element and self.resizing_element.is_resizing:
            self._handle_resize(pos)
        # Handle dragging
        elif self.dragging_element and self.dragging_element.is_dragging:
            self._handle_drag(pos)
        else:
            # Handle hovering
            self._handle_hover(pos)
        
        self.last_mouse_pos = pos
        self.update()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if self.dragging_element:
            self.dragging_element.is_dragging = False
            self.dragging_element = None
        
        if self.resizing_element:
            self.resizing_element.is_resizing = False
            self.resizing_element.resize_handle = None
            self.resizing_element = None
        
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.update()
    
    def _handle_drag(self, pos: QPoint):
        """Handle element dragging."""
        if not self.dragging_element or not self.last_mouse_pos:
            return
        
        delta = pos - self.last_mouse_pos
        element = self.dragging_element
        
        if element.scaled_rect:
            element.scaled_rect.x += delta.x()
            element.scaled_rect.y += delta.y()
            element.update_resize_handles()
    
    def _handle_resize(self, pos: QPoint):
        """Handle element resizing."""
        if not self.resizing_element or not self.last_mouse_pos:
            return
        
        delta = pos - self.last_mouse_pos
        element = self.resizing_element
        handle = element.resize_handle
        
        if not element.scaled_rect or not handle:
            return
        
        rect = element.scaled_rect
        
        # Apply resize based on handle type
        if handle == 'top-left':
            rect.x += delta.x()
            rect.y += delta.y()
            rect.width -= delta.x()
            rect.height -= delta.y()
        elif handle == 'top-right':
            rect.y += delta.y()
            rect.width += delta.x()
            rect.height -= delta.y()
        elif handle == 'bottom-left':
            rect.x += delta.x()
            rect.width -= delta.x()
            rect.height += delta.y()
        elif handle == 'bottom-right':
            rect.width += delta.x()
            rect.height += delta.y()
        elif handle == 'top':
            rect.y += delta.y()
            rect.height -= delta.y()
        elif handle == 'bottom':
            rect.height += delta.y()
        elif handle == 'left':
            rect.x += delta.x()
            rect.width -= delta.x()
        elif handle == 'right':
            rect.width += delta.x()
        
        # Ensure minimum size
        min_size = 10
        if rect.width < min_size:
            rect.width = min_size
        if rect.height < min_size:
            rect.height = min_size
        
        element.update_resize_handles()
    
    def _handle_hover(self, pos: QPoint):
        """Handle mouse hovering."""
        element = self._get_element_at_position(pos)
        
        # Clear previous hover states
        if self.analysis_result:
            for el in self.analysis_result.elements:
                if el.is_hovered and el != element:
                    el.is_hovered = False
        
        # Set new hover state
        if element:
            if not element.is_hovered:
                element.is_hovered = True
                self.element_hovered.emit(element.element_id)
            
            # Update cursor for resize handles
            if element.is_selected:
                handle = element.get_resize_handle_at(pos.x(), pos.y())
                if handle:
                    self._update_cursor(handle)
                else:
                    self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
    
    def _update_cursor(self, handle_type: str):
        """Update cursor based on resize handle type."""
        cursor_map = {
            'top-left': Qt.CursorShape.SizeFDiagCursor,
            'top-right': Qt.CursorShape.SizeBDiagCursor,
            'bottom-left': Qt.CursorShape.SizeBDiagCursor,
            'bottom-right': Qt.CursorShape.SizeFDiagCursor,
            'top': Qt.CursorShape.SizeVerCursor,
            'bottom': Qt.CursorShape.SizeVerCursor,
            'left': Qt.CursorShape.SizeHorCursor,
            'right': Qt.CursorShape.SizeHorCursor
        }
        
        cursor = cursor_map.get(handle_type, Qt.CursorShape.ArrowCursor)
        self.setCursor(QCursor(cursor))
    
    def resizeEvent(self, event):
        """Handle widget resize."""
        super().resizeEvent(event)
        if self.original_image:
            self._update_scaled_image()
            self._update_element_positions()
            self.update()
