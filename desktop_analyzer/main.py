# -*- coding: utf-8 -*-
"""
Main application file for the Desktop UI/UX Analyzer.
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, 
    QFileDialog, QPushButton, QHBoxLayout, QListWidget, QListWidgetItem,
    QSplitter, QMessageBox, QTextEdit, QGroupBox, QScrollArea
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

    def contains(self, point: QPoint) -> bool:
        return self.scaled_rect.contains(point)

    def draw(self, painter: QPainter, scale: float, offset: QPoint):
        # Calculate scaled coordinates
        self.scaled_rect = QRect(
            int(offset.x() + self.rect.x() * scale),
            int(offset.y() + self.rect.y() * scale),
            int(self.rect.width() * scale),
            int(self.rect.height() * scale)
        )

        if self.is_selected:
            pen = QPen(QColor(239, 68, 68), 3) # Red-500
        elif self.is_hovered:
            pen = QPen(QColor(16, 185, 129), 3) # Emerald-500
        else:
            pen = QPen(QColor(52, 211, 153), 2) # Emerald-400
        
        painter.setPen(pen)
        painter.setBrush(QColor(0,0,0,0))
        painter.drawRect(self.scaled_rect)

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

    def mouseMoveEvent(self, event):
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
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self.update()

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

        # Add all groups to right panel
        right_layout.addWidget(elements_group)
        right_layout.addWidget(desc_group)
        right_layout.addWidget(feedback_group)
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

        # Prepare data for JSON export
        output_data = {
            "image_path": self.canvas.image_path,
            "elements": []
        }
        for box in self.canvas.boxes:
            output_data["elements"].append({
                "id": box.element_id,
                "description": box.description,
                "box": [box.rect.x(), box.rect.y(), box.rect.x() + box.rect.width(), box.rect.y() + box.rect.height()]
            })

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
                    json.dump(output_data, f, ensure_ascii=False, indent=4)
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
        
        # Update element description
        self.element_description.setText(box.description)

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
                # Update element description
                self.element_description.setText(box.description)
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

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 