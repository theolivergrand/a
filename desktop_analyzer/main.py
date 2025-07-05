# -*- coding: utf-8 -*-
"""
Main application file for the Desktop UI/UX Analyzer.
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, 
    QFileDialog, QPushButton, QHBoxLayout, QListWidget, QListWidgetItem,
    QSplitter, QMessageBox, QTextEdit, QGroupBox, QScrollArea, QDialog,
    QMenu, QInputDialog
)
import json
import os
from datetime import datetime
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPixmap, QAction, QPainter, QColor, QPen, QCursor
from PIL import Image
from ai_analyzer import analyze_ui_elements

class BoundingBox:
    """Represents a bounding box for a detected UI element."""
    def __init__(self, rect: QRect, description: str, element_id: str = None):
        self.rect = rect
        self.description = description
        self.element_id = element_id
        self.is_selected = False
        self.is_hovered = False
        self.is_dragging = False
        self.is_resizing = False
        self.resize_handle = None  # Which resize handle is being dragged
        self.resize_handle_size = 8  # Size of resize handles in pixels
        self.scaled_rect = QRect()
        self.resize_handles = {}  # Dictionary to store resize handle rects
        
        # Resize handle types
        self.HANDLE_TYPES = {
            'top-left': 'nw-resize',
            'top-right': 'ne-resize', 
            'bottom-left': 'sw-resize',
            'bottom-right': 'se-resize',
            'top': 'n-resize',
            'bottom': 's-resize',
            'left': 'w-resize',
            'right': 'e-resize'
        }

    def contains(self, point: QPoint) -> bool:
        return self.scaled_rect.contains(point)

    def get_resize_handle_at(self, point: QPoint) -> str:
        """Returns the resize handle type at the given point, or None if no handle."""
        if not self.is_selected:
            return None
            
        for handle_type, handle_rect in self.resize_handles.items():
            if handle_rect.contains(point):
                return handle_type
        return None

    def calculate_resize_handles(self):
        """Calculate positions of all resize handles."""
        if not self.is_selected:
            self.resize_handles = {}
            return
            
        handle_size = self.resize_handle_size
        half_size = handle_size // 2
        
        # Corner handles
        self.resize_handles['top-left'] = QRect(
            self.scaled_rect.left() - half_size,
            self.scaled_rect.top() - half_size,
            handle_size, handle_size
        )
        self.resize_handles['top-right'] = QRect(
            self.scaled_rect.right() - half_size,
            self.scaled_rect.top() - half_size,
            handle_size, handle_size
        )
        self.resize_handles['bottom-left'] = QRect(
            self.scaled_rect.left() - half_size,
            self.scaled_rect.bottom() - half_size,
            handle_size, handle_size
        )
        self.resize_handles['bottom-right'] = QRect(
            self.scaled_rect.right() - half_size,
            self.scaled_rect.bottom() - half_size,
            handle_size, handle_size
        )
        
        # Edge handles
        self.resize_handles['top'] = QRect(
            self.scaled_rect.center().x() - half_size,
            self.scaled_rect.top() - half_size,
            handle_size, handle_size
        )
        self.resize_handles['bottom'] = QRect(
            self.scaled_rect.center().x() - half_size,
            self.scaled_rect.bottom() - half_size,
            handle_size, handle_size
        )
        self.resize_handles['left'] = QRect(
            self.scaled_rect.left() - half_size,
            self.scaled_rect.center().y() - half_size,
            handle_size, handle_size
        )
        self.resize_handles['right'] = QRect(
            self.scaled_rect.right() - half_size,
            self.scaled_rect.center().y() - half_size,
            handle_size, handle_size
        )

    def draw(self, painter: QPainter, scale: float, offset: QPoint):
        # Calculate scaled coordinates
        self.scaled_rect = QRect(
            int(offset.x() + self.rect.x() * scale),
            int(offset.y() + self.rect.y() * scale),
            int(self.rect.width() * scale),
            int(self.rect.height() * scale)
        )

        # Draw main rectangle
        if self.is_selected:
            pen = QPen(QColor(239, 68, 68), 3) # Red-500
        elif self.is_hovered:
            pen = QPen(QColor(16, 185, 129), 3) # Emerald-500
        else:
            pen = QPen(QColor(52, 211, 153), 2) # Emerald-400
        
        painter.setPen(pen)
        painter.setBrush(QColor(0,0,0,0))
        painter.drawRect(self.scaled_rect)
        
        # Draw resize handles if selected
        if self.is_selected:
            self.calculate_resize_handles()
            self.draw_resize_handles(painter)

    def draw_resize_handles(self, painter: QPainter):
        """Draw resize handles for the selected bounding box."""
        # Set style for resize handles
        painter.setPen(QPen(QColor(239, 68, 68), 2))  # Red border
        painter.setBrush(QColor(255, 255, 255))       # White fill
        
        # Draw all resize handles
        for handle_type, handle_rect in self.resize_handles.items():
            painter.drawRect(handle_rect)

class ImageCanvas(QWidget):
    """A widget to display the image and interactive bounding boxes."""
    box_selected = pyqtSignal(object) # Signal to emit when a box is selected

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window # Reference to main window to update status
        self.setMinimumSize(600, 400)
        self.pixmap = None
        self.boxes = []
        self.scale = 1.0
        self.offset = QPoint(0, 0)
        self.selected_box = None
        self.drag_start_position = QPoint(0,0)
        self.original_rect = QRect()  # Store original rect for resize operations
        
        self.setMouseTracking(True) # Enable mouse move events even when button is not pressed

    def set_image(self, image_path):
        self.image_path = image_path
        self.pixmap = QPixmap(image_path)
        
        pil_image = Image.open(image_path)
        json_data, status_msg = analyze_ui_elements(pil_image)
        self.main_window.statusBar().showMessage(status_msg)
        
        if json_data and "elements" in json_data:
            self.boxes = [
                BoundingBox(QRect(el["box"][0], el["box"][1], el["box"][2] - el["box"][0], el["box"][3] - el["box"][1]), 
                           el["description"], el.get("id"))
                for el in json_data.get("elements", [])
            ]
        else:
            self.boxes = []

        self.window().resize(self.pixmap.width(), self.pixmap.height())
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        if not self.pixmap:
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Загрузите изображение...")
            return

        # Calculate scaling and offset
        scaled_pixmap = self.pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.offset = QPoint((self.width() - scaled_pixmap.width()) // 2, (self.height() - scaled_pixmap.height()) // 2)
        self.scale = scaled_pixmap.width() / self.pixmap.width() if self.pixmap.width() > 0 else 1
        
        painter.drawPixmap(self.offset, scaled_pixmap)
        
        for box in self.boxes:
            box.draw(painter, self.scale, self.offset)

    def _get_box_at(self, pos: QPoint):
        # Iterate in reverse to get the top-most box
        for box in reversed(self.boxes):
            if box.contains(pos):
                return box
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            box = self._get_box_at(event.pos())
            
            # Check if we're clicking on a resize handle first
            resize_handle = None
            if self.selected_box:
                resize_handle = self.selected_box.get_resize_handle_at(event.pos())
            
            if resize_handle:
                # Starting resize operation
                self.selected_box.is_resizing = True
                self.selected_box.resize_handle = resize_handle
                self.drag_start_position = event.pos()
                self.original_rect = QRect(self.selected_box.rect)  # Save original rect
            else:
                # Deselect previous box
                if self.selected_box:
                    self.selected_box.is_selected = False
                
                self.selected_box = box
                
                if self.selected_box:
                    self.selected_box.is_selected = True
                    self.selected_box.is_dragging = True
                    self.drag_start_position = event.pos() - self.selected_box.scaled_rect.topLeft()
                    self.box_selected.emit(self.selected_box) # Emit signal
                else:
                    self.box_selected.emit(None) # Emit signal for deselection
            
            self.update()
            
        elif event.button() == Qt.MouseButton.RightButton:
            # Handle right-click for context menu
            box = self._get_box_at(event.pos())
            if box:
                # Select the box if it's not already selected
                if self.selected_box:
                    self.selected_box.is_selected = False
                self.selected_box = box
                self.selected_box.is_selected = True
                self.box_selected.emit(self.selected_box)
                self.update()
                
                # Show context menu
                self.show_context_menu(event.pos(), box)

    def mouseMoveEvent(self, event):
        # Handle resizing
        if self.selected_box and self.selected_box.is_resizing:
            self._handle_resize(event)
            return

        # Handle dragging
        if self.selected_box and self.selected_box.is_dragging:
            # Move the original, unscaled rectangle
            new_top_left_scaled = event.pos() - self.drag_start_position
            new_top_left_unscaled = (new_top_left_scaled - self.offset) / self.scale
            # Convert to QPoint properly
            if hasattr(new_top_left_unscaled, 'toPoint'):
                point = new_top_left_unscaled.toPoint()
            else:
                point = QPoint(int(new_top_left_unscaled.x()), int(new_top_left_unscaled.y()))
            self.selected_box.rect.moveTo(point)
            self.update()
            self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
            return

        # Handle cursor changes for resize handles
        if self.selected_box:
            resize_handle = self.selected_box.get_resize_handle_at(event.pos())
            if resize_handle:
                cursor_shape = self._get_cursor_for_handle(resize_handle)
                self.setCursor(QCursor(cursor_shape))
                self.update()
                return

        # Handle hovering
        current_hovered_box = self._get_box_at(event.pos())
        hover_changed = False
        for box in self.boxes:
            is_now_hovered = (box == current_hovered_box)
            if box.is_hovered != is_now_hovered:
                box.is_hovered = is_now_hovered
                hover_changed = True
        
        if hover_changed:
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor) if current_hovered_box else QCursor(Qt.CursorShape.ArrowCursor))
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.selected_box:
            self.selected_box.is_dragging = False
            self.selected_box.is_resizing = False
            self.selected_box.resize_handle = None
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self.update()

    def _handle_resize(self, event):
        """Handle resizing of the selected bounding box."""
        if not self.selected_box or not self.selected_box.resize_handle:
            return
            
        # Calculate mouse movement
        delta = event.pos() - self.drag_start_position
        
        # Convert delta to unscaled coordinates
        delta_unscaled = QPoint(int(delta.x() / self.scale), int(delta.y() / self.scale))
        
        # Start with original rect
        new_rect = QRect(self.original_rect)
        
        handle = self.selected_box.resize_handle
        
        # Apply resize based on handle type
        if handle == 'top-left':
            new_rect.setTopLeft(new_rect.topLeft() + delta_unscaled)
        elif handle == 'top-right':
            new_rect.setTop(new_rect.top() + delta_unscaled.y())
            new_rect.setRight(new_rect.right() + delta_unscaled.x())
        elif handle == 'bottom-left':
            new_rect.setLeft(new_rect.left() + delta_unscaled.x())
            new_rect.setBottom(new_rect.bottom() + delta_unscaled.y())
        elif handle == 'bottom-right':
            new_rect.setBottomRight(new_rect.bottomRight() + delta_unscaled)
        elif handle == 'top':
            new_rect.setTop(new_rect.top() + delta_unscaled.y())
        elif handle == 'bottom':
            new_rect.setBottom(new_rect.bottom() + delta_unscaled.y())
        elif handle == 'left':
            new_rect.setLeft(new_rect.left() + delta_unscaled.x())
        elif handle == 'right':
            new_rect.setRight(new_rect.right() + delta_unscaled.x())
        
        # Ensure minimum size
        min_size = 10
        if new_rect.width() < min_size:
            if handle in ['top-left', 'bottom-left', 'left']:
                new_rect.setLeft(new_rect.right() - min_size)
            else:
                new_rect.setRight(new_rect.left() + min_size)
                
        if new_rect.height() < min_size:
            if handle in ['top-left', 'top-right', 'top']:
                new_rect.setTop(new_rect.bottom() - min_size)
            else:
                new_rect.setBottom(new_rect.top() + min_size)
        
        # Update the bounding box
        self.selected_box.rect = new_rect
        self.update()

    def _get_cursor_for_handle(self, handle_type):
        """Get appropriate cursor shape for resize handle."""
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
        return cursor_map.get(handle_type, Qt.CursorShape.ArrowCursor)

    def show_context_menu(self, position, box):
        """Show context menu for the selected bounding box."""
        context_menu = QMenu(self)
        
        # Add feedback action
        feedback_action = context_menu.addAction("💬 Добавить комментарий")
        feedback_action.triggered.connect(lambda: self.add_element_feedback(box))
        
        # Edit description action
        edit_action = context_menu.addAction("✏️ Редактировать описание")
        edit_action.triggered.connect(lambda: self.edit_element_description(box))
        
        # Show feedback action (if feedback exists)
        feedback = getattr(box, 'feedback', '')
        if feedback:
            show_feedback_action = context_menu.addAction("👁️ Показать комментарий")
            show_feedback_action.triggered.connect(lambda: self.show_element_feedback(box))
        
        context_menu.addSeparator()
        
        # Delete action
        delete_action = context_menu.addAction("🗑️ Удалить элемент")
        delete_action.triggered.connect(lambda: self.delete_element(box))
        
        # Show context menu
        context_menu.exec(self.mapToGlobal(position))

    def add_element_feedback(self, box):
        """Add or edit feedback for the selected element."""
        current_feedback = getattr(box, 'feedback', '')
        
        feedback, ok = QInputDialog.getMultiLineText(
            self, 
            "Комментарий к элементу",
            f"Элемент: {box.description}\n\nВведите комментарий:",
            current_feedback
        )
        
        if ok:
            box.feedback = feedback.strip()
            self.main_window.statusBar().showMessage("✅ Комментарий сохранён", 3000)

    def edit_element_description(self, box):
        """Edit the description of the selected element."""
        new_description, ok = QInputDialog.getText(
            self,
            "Редактировать описание",
            "Новое описание элемента:",
            text=box.description
        )
        
        if ok and new_description.strip():
            box.description = new_description.strip()
            # Update the list in main window
            if hasattr(self.main_window, 'populate_element_list'):
                self.main_window.populate_element_list()
            self.main_window.statusBar().showMessage("✅ Описание обновлено", 3000)

    def show_element_feedback(self, box):
        """Show feedback for the selected element."""
        feedback = getattr(box, 'feedback', '')
        if feedback:
            QMessageBox.information(
                self,
                f"Комментарий: {box.description}",
                feedback
            )

    def delete_element(self, box):
        """Delete the selected element after confirmation."""
        reply = QMessageBox.question(
            self,
            "Удалить элемент",
            f"Вы уверены, что хотите удалить элемент:\n\n{box.description}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove from boxes list
            if box in self.boxes:
                self.boxes.remove(box)
            
            # Clear selection if this was the selected box
            if self.selected_box == box:
                self.selected_box = None
                self.box_selected.emit(None)
            
            # Update UI
            if hasattr(self.main_window, 'populate_element_list'):
                self.main_window.populate_element_list()
            self.update()
            self.main_window.statusBar().showMessage("✅ Элемент удалён", 3000)

class FullScreenMarkupWindow(QDialog):
    """Full-screen markup mode window with floating panels."""
    
    def __init__(self, parent, canvas_data):
        super().__init__(parent)
        self.parent_window = parent
        self.canvas_data = canvas_data  # Contains image path, boxes, etc.
        
        self.setWindowTitle("Полноэкранная разметка - Desktop UI/UX Analyzer")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowCloseButtonHint)
        self.showMaximized()
        
        self.setup_ui()
        self.setup_floating_panels()
        
        # Load data from parent canvas
        if self.canvas_data:
            self.load_canvas_data()
    
    def setup_ui(self):
        """Setup the main UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create enhanced canvas
        self.canvas = ImageCanvas(self)
        main_layout.addWidget(self.canvas)
        
        # Connect canvas signals
        self.canvas.box_selected.connect(self.on_canvas_box_selected)
        
        # Create toolbar
        self.create_toolbar()
        
    def create_toolbar(self):
        """Create floating toolbar with main controls."""
        self.toolbar = QWidget(self)
        self.toolbar.setObjectName("toolbar")
        self.toolbar.setStyleSheet("""
            QWidget#toolbar {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        
        # Exit button
        self.exit_button = QPushButton("✕ Выход")
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        self.exit_button.clicked.connect(self.close_markup_mode)
        
        # Save button
        self.save_button = QPushButton("💾 Сохранить")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.save_button.clicked.connect(self.save_markup)
        
        # Toggle panels button
        self.toggle_panels_button = QPushButton("📋 Панели")
        self.toggle_panels_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        self.toggle_panels_button.clicked.connect(self.toggle_floating_panels)
        
        toolbar_layout.addWidget(self.exit_button)
        toolbar_layout.addWidget(self.save_button)
        toolbar_layout.addWidget(self.toggle_panels_button)
        toolbar_layout.addStretch()
        
        # Position toolbar at top-right
        self.toolbar.setParent(self)
        self.toolbar.move(self.width() - 300, 20)
        self.toolbar.show()
        
    def setup_floating_panels(self):
        """Setup floating panels for elements and feedback."""
        # Elements panel
        self.elements_panel = self.create_floating_panel("Элементы", 300, 400)
        self.elements_list = QListWidget()
        self.elements_list.itemClicked.connect(self.on_list_item_clicked)
        self.elements_panel.layout().addWidget(self.elements_list)
        
        # Feedback panel
        self.feedback_panel = self.create_floating_panel("Обратная связь", 300, 200)
        self.feedback_text = QTextEdit()
        self.feedback_text.setPlaceholderText("Комментарий к выбранному элементу...")
        self.feedback_button = QPushButton("Сохранить комментарий")
        self.feedback_button.clicked.connect(self.save_element_feedback)
        self.feedback_panel.layout().addWidget(self.feedback_text)
        self.feedback_panel.layout().addWidget(self.feedback_button)
        
        # Position panels
        self.elements_panel.move(20, 100)
        self.feedback_panel.move(20, 520)
        
        # Initially hide panels
        self.panels_visible = True
        self.toggle_floating_panels()
    
    def create_floating_panel(self, title, width, height):
        """Create a floating panel widget."""
        panel = QWidget(self)
        panel.setFixedSize(width, height)
        panel.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border: 1px solid #ccc;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #374151;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(title_label)
        
        return panel
    
    def load_canvas_data(self):
        """Load image and boxes from parent canvas."""
        if hasattr(self.canvas_data, 'image_path') and self.canvas_data.image_path:
            self.canvas.set_image(self.canvas_data.image_path)
            self.populate_element_list()
    
    def populate_element_list(self):
        """Populate the elements list."""
        self.elements_list.clear()
        if not self.canvas.boxes:
            return
            
        for i, box in enumerate(self.canvas.boxes):
            item_text = f"Элемент {box.element_id or i+1}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, box)
            self.elements_list.addItem(item)
    
    def on_canvas_box_selected(self, box):
        """Handle box selection from canvas."""
        if box is None:
            self.elements_list.clearSelection()
            self.feedback_text.clear()
            return
            
        # Select corresponding item in list
        for i in range(self.elements_list.count()):
            item = self.elements_list.item(i)
            item_box = item.data(Qt.ItemDataRole.UserRole)
            if item_box == box:
                item.setSelected(True)
                self.elements_list.scrollToItem(item)
                # Load existing feedback if any
                feedback = getattr(box, 'feedback', '')
                self.feedback_text.setPlainText(feedback)
                break
    
    def on_list_item_clicked(self, item):
        """Handle element list item selection."""
        box = item.data(Qt.ItemDataRole.UserRole)
        if self.canvas.selected_box:
            self.canvas.selected_box.is_selected = False
            
        self.canvas.selected_box = box
        self.canvas.selected_box.is_selected = True
        self.canvas.update()
        
        # Load feedback for selected element
        feedback = getattr(box, 'feedback', '')
        self.feedback_text.setPlainText(feedback)
    
    def save_element_feedback(self):
        """Save feedback for the selected element."""
        if not self.canvas.selected_box:
            QMessageBox.warning(self, "Нет выбранного элемента", "Выберите элемент для добавления комментария.")
            return
            
        feedback = self.feedback_text.toPlainText().strip()
        self.canvas.selected_box.feedback = feedback
        
        # Visual feedback
        self.feedback_button.setText("✓ Сохранено")
        self.feedback_button.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
        """)
        
        # Reset button after 2 seconds
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, self.reset_feedback_button)
    
    def reset_feedback_button(self):
        """Reset feedback button to original state."""
        self.feedback_button.setText("Сохранить комментарий")
        self.feedback_button.setStyleSheet("")
    
    def toggle_floating_panels(self):
        """Toggle visibility of floating panels."""
        self.panels_visible = not self.panels_visible
        self.elements_panel.setVisible(self.panels_visible)
        self.feedback_panel.setVisible(self.panels_visible)
        
        # Update button text
        if self.panels_visible:
            self.toggle_panels_button.setText("📋 Скрыть панели")
        else:
            self.toggle_panels_button.setText("📋 Показать панели")
    
    def save_markup(self):
        """Save current markup data."""
        if not self.canvas.boxes:
            QMessageBox.warning(self, "Нет данных", "Нет данных для сохранения.")
            return
            
        # Prepare data including feedback
        output_data = {
            "image_path": getattr(self.canvas, 'image_path', ''),
            "timestamp": datetime.now().isoformat(),
            "elements": []
        }
        
        for box in self.canvas.boxes:
            element_data = {
                "id": box.element_id,
                "description": box.description,
                "box": [box.rect.x(), box.rect.y(), 
                       box.rect.x() + box.rect.width(), 
                       box.rect.y() + box.rect.height()],
                "feedback": getattr(box, 'feedback', '')
            }
            output_data["elements"].append(element_data)
        
        # Save to file
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить разметку",
            "",
            "JSON Files (*.json)"
        )
        
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=2)
                    
                # Show success message
                self.save_button.setText("✓ Сохранено")
                self.save_button.setStyleSheet("""
                    QPushButton {
                        background-color: #10b981;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-weight: bold;
                    }
                """)
                
                # Reset button after 2 seconds
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(2000, self.reset_save_button)
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка сохранения", f"Не удалось сохранить файл:\n{e}")
    
    def reset_save_button(self):
        """Reset save button to original state."""
        self.save_button.setText("💾 Сохранить")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
    
    def close_markup_mode(self):
        """Close markup mode and return to main window."""
        # Save current state back to parent
        if hasattr(self.parent_window, 'canvas') and self.canvas.boxes:
            self.parent_window.canvas.boxes = self.canvas.boxes
            self.parent_window.populate_element_list()
            self.parent_window.canvas.update()
        
        self.close()
    
    def resizeEvent(self, event):
        """Handle window resize to reposition toolbar."""
        super().resizeEvent(event)
        if hasattr(self, 'toolbar'):
            self.toolbar.move(self.width() - 300, 20)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Desktop UI/UX Analyzer")
        self.setGeometry(100, 100, 1200, 800)
        self.setStatusBar(self.statusBar()) # Add a status bar

        # Main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Image canvas
        self.canvas = ImageCanvas(self)
        
        # Right-side panel for controls and list
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_panel.setFixedWidth(400)

        # Elements list section
        elements_group = QGroupBox("Обнаруженные элементы")
        elements_layout = QVBoxLayout(elements_group)
        
        self.element_list = QListWidget()
        self.element_list.setMaximumHeight(200)
        elements_layout.addWidget(self.element_list)

        # Element description section
        desc_group = QGroupBox("Описание выбранного элемента")
        desc_layout = QVBoxLayout(desc_group)
        
        self.element_description = QTextEdit()
        self.element_description.setReadOnly(True)
        self.element_description.setMaximumHeight(120)
        self.element_description.setPlaceholderText("Выберите элемент для просмотра описания...")
        desc_layout.addWidget(self.element_description)

        # Feedback section
        feedback_group = QGroupBox("Обратная связь")
        feedback_layout = QVBoxLayout(feedback_group)
        
        self.feedback_text = QTextEdit()
        self.feedback_text.setMaximumHeight(100)
        self.feedback_text.setPlaceholderText("Ваши комментарии о качестве анализа...")
        
        self.send_feedback_button = QPushButton("Отправить обратную связь")
        self.send_feedback_button.clicked.connect(self.send_feedback)
        
        feedback_layout.addWidget(self.feedback_text)
        feedback_layout.addWidget(self.send_feedback_button)

        # Save section
        save_group = QGroupBox("Сохранение")
        save_layout = QVBoxLayout(save_group)
        
        self.save_button = QPushButton("Сохранить JSON")
        self.save_button.clicked.connect(self.save_annotations)
        
        self.save_to_folder_button = QPushButton("Сохранить в папку...")
        self.save_to_folder_button.clicked.connect(self.save_to_folder)
        
        save_layout.addWidget(self.save_button)
        save_layout.addWidget(self.save_to_folder_button)

        # Markup mode section
        markup_group = QGroupBox("Режим разметки")
        markup_layout = QVBoxLayout(markup_group)
        
        self.markup_mode_button = QPushButton("🔍 Полноэкранная разметка")
        self.markup_mode_button.setStyleSheet("""
            QPushButton {
                background-color: #FFF3E0;
                border: 2px solid #F57C00;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #FFE0B2;
            }
            QPushButton:pressed {
                background-color: #FFCC02;
            }
        """)
        self.markup_mode_button.clicked.connect(self.open_markup_mode)
        
        markup_layout.addWidget(self.markup_mode_button)

        # Add all groups to right panel
        right_layout.addWidget(elements_group)
        right_layout.addWidget(desc_group)
        right_layout.addWidget(feedback_group)
        right_layout.addWidget(markup_group)
        right_layout.addWidget(save_group)
        right_layout.addStretch()  # Add stretch to push everything to top

        # Splitter to make layout adjustable
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.canvas)
        splitter.addWidget(right_panel)
        splitter.setSizes([800, 400]) # Initial sizes
        main_layout.addWidget(splitter)
        
        self.canvas.box_selected.connect(self.on_canvas_box_selected)
        self.element_list.itemClicked.connect(self.on_list_item_clicked)
        
        self._create_menus()

    def _create_menus(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Файл")
        open_action = QAction("Открыть...", self)
        open_action.triggered.connect(self.open_image_dialog)
        file_menu.addAction(open_action)
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
    def open_image_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть изображение", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            self.canvas.set_image(file_path)
            self.populate_element_list()
            
    def save_annotations(self):
        if not self.canvas.boxes:
            QMessageBox.warning(self, "Нет данных", "Нет аннотаций для сохранения.")
            return

        # Prepare data for JSON export with feedback support
        output_data = {
            "image_path": getattr(self.canvas, 'image_path', ''),
            "timestamp": datetime.now().isoformat(),
            "version": "2.0",
            "elements": []
        }
        
        for box in self.canvas.boxes:
            element_data = {
                "id": box.element_id,
                "description": box.description,
                "box": [box.rect.x(), box.rect.y(), box.rect.x() + box.rect.width(), box.rect.y() + box.rect.height()],
                "type": self._classify_element_type(box.description),
                "feedback": getattr(box, 'feedback', ''),
                "created_at": datetime.now().isoformat()
            }
            output_data["elements"].append(element_data)

        # Open save file dialog
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить аннотации",
            "",
            "JSON Files (*.json)"
        )

        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=2)
                self.statusBar().showMessage(f"✅ Аннотации успешно сохранены в {save_path}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка сохранения", f"Не удалось сохранить файл:\n{e}")

    def populate_element_list(self):
        self.element_list.clear()
        if not self.canvas.boxes: return
        for i, box in enumerate(self.canvas.boxes):
            # Store the box object itself in the item
            item_text = f"Элемент {box.element_id or i+1}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, box)
            self.element_list.addItem(item)
            
    def on_list_item_clicked(self, item):
        box = item.data(Qt.ItemDataRole.UserRole)
        if self.canvas.selected_box:
            self.canvas.selected_box.is_selected = False
            
        self.canvas.selected_box = box
        self.canvas.selected_box.is_selected = True
        self.canvas.update()
        
        # Update element description with feedback
        description_text = f"Описание: {box.description}\n\n"
        feedback = getattr(box, 'feedback', '')
        if feedback:
            description_text += f"Комментарий: {feedback}"
        else:
            description_text += "Комментарий: отсутствует\n\n(Используйте правый клик для добавления комментария)"
        
        self.element_description.setText(description_text)

    def on_canvas_box_selected(self, box):
        if box is None:
            self.element_list.clearSelection()
            self.element_description.clear()
            return
            
        for i in range(self.element_list.count()):
            item = self.element_list.item(i)
            item_box = item.data(Qt.ItemDataRole.UserRole)
            if item_box == box:
                item.setSelected(True)
                self.element_list.scrollToItem(item)
                
                # Update element description with feedback
                description_text = f"Описание: {box.description}\n\n"
                feedback = getattr(box, 'feedback', '')
                if feedback:
                    description_text += f"Комментарий: {feedback}"
                else:
                    description_text += "Комментарий: отсутствует\n\n(Используйте правый клик для добавления комментария)"
                
                self.element_description.setText(description_text)
                break

    def send_feedback(self):
        """Отправляет обратную связь и сохраняет в лог"""
        feedback_text = self.feedback_text.toPlainText().strip()
        if not feedback_text:
            QMessageBox.warning(self, "Пустая обратная связь", "Пожалуйста, введите текст обратной связи.")
            return
            
        # Create feedback directory if it doesn't exist
        feedback_dir = "feedback_logs"
        os.makedirs(feedback_dir, exist_ok=True)
        
        # Create log entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "image_path": getattr(self.canvas, 'image_path', 'Unknown'),
            "elements_count": len(self.canvas.boxes),
            "feedback": feedback_text
        }
        
        # Save to log file
        log_file = os.path.join(feedback_dir, "feedback_log.json")
        logs = []
        
        # Load existing logs
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        # Add new log entry
        logs.append(log_entry)
        
        # Save updated logs
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
            
            # Also save to simple text file for easy reading
            txt_file = os.path.join(feedback_dir, "feedback.txt")
            with open(txt_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {feedback_text}\n")
            
            self.statusBar().showMessage(f"✅ Обратная связь сохранена в {feedback_dir}", 5000)
            self.feedback_text.clear()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения", f"Не удалось сохранить обратную связь:\n{e}")

    def save_to_folder(self):
        """Сохраняет обработанные файлы в выбранную папку"""
        if not self.canvas.boxes:
            QMessageBox.warning(self, "Нет данных", "Нет данных для сохранения.")
            return
            
        # Select folder
        folder_path = QFileDialog.getExistingDirectory(
            self, 
            "Выберите папку для сохранения",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not folder_path:
            return
            
        try:
            # Create timestamp for unique filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save JSON data
            json_data = {
                "timestamp": datetime.now().isoformat(),
                "image_path": getattr(self.canvas, 'image_path', 'Unknown'),
                "image_size": {
                    "width": self.canvas.pixmap.width() if self.canvas.pixmap else 0,
                    "height": self.canvas.pixmap.height() if self.canvas.pixmap else 0
                },
                "elements": []
            }
            
            for box in self.canvas.boxes:
                json_data["elements"].append({
                    "id": box.element_id,
                    "description": box.description,
                    "box": [box.rect.x(), box.rect.y(), 
                           box.rect.x() + box.rect.width(), 
                           box.rect.y() + box.rect.height()],
                    "type": self._classify_element_type(box.description)
                })
            
            # Save JSON file
            json_filename = f"analysis_{timestamp}.json"
            json_path = os.path.join(folder_path, json_filename)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            # Copy original image if available
            if hasattr(self.canvas, 'image_path') and os.path.exists(self.canvas.image_path):
                import shutil
                image_ext = os.path.splitext(self.canvas.image_path)[1]
                image_filename = f"original_{timestamp}{image_ext}"
                image_path = os.path.join(folder_path, image_filename)
                shutil.copy2(self.canvas.image_path, image_path)
            
            # Create summary report
            report_filename = f"report_{timestamp}.txt"
            report_path = os.path.join(folder_path, report_filename)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"UI/UX Analysis Report\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Image: {os.path.basename(getattr(self.canvas, 'image_path', 'Unknown'))}\n")
                f.write(f"Elements found: {len(self.canvas.boxes)}\n\n")
                
                for i, box in enumerate(self.canvas.boxes, 1):
                    f.write(f"Element {i}:\n")
                    f.write(f"  Type: {self._classify_element_type(box.description)}\n")
                    f.write(f"  Position: ({box.rect.x()}, {box.rect.y()})\n")
                    f.write(f"  Size: {box.rect.width()}x{box.rect.height()}\n")
                    f.write(f"  Description: {box.description}\n\n")
            
            self.statusBar().showMessage(f"✅ Файлы сохранены в {folder_path}", 5000)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения", f"Не удалось сохранить файлы:\n{e}")

    def _classify_element_type(self, description):
        """Классифицирует тип UI элемента на основе описания"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['button', 'кнопка', 'btn']):
            return "button"
        elif any(word in description_lower for word in ['input', 'field', 'ввод', 'поле']):
            return "input"
        elif any(word in description_lower for word in ['text', 'label', 'текст', 'надпись']):
            return "text"
        elif any(word in description_lower for word in ['image', 'img', 'изображение', 'картинка']):
            return "image"
        elif any(word in description_lower for word in ['menu', 'nav', 'меню', 'навигация']):
            return "navigation"
        elif any(word in description_lower for word in ['icon', 'иконка', 'значок']):
            return "icon"
        elif any(word in description_lower for word in ['dropdown', 'select', 'выпадающий', 'список']):
            return "dropdown"
        elif any(word in description_lower for word in ['checkbox', 'radio', 'флажок', 'переключатель']):
            return "checkbox"
        else:
            return "other"

    def open_markup_mode(self):
        """Open full-screen markup mode."""
        if not hasattr(self.canvas, 'image_path') or not self.canvas.image_path:
            QMessageBox.warning(self, "Нет изображения", "Сначала загрузите изображение для разметки.")
            return
            
        # Create and show full-screen markup window
        markup_window = FullScreenMarkupWindow(self, self.canvas)
        markup_window.exec()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 