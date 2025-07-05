# -*- coding: utf-8 -*-
"""
Main application controller for the Desktop UI/UX Analyzer.
"""
import os
from datetime import datetime
from typing import Optional, List, Callable
from PIL import Image

from ..models.data_models import ProjectData, AnalysisResult, BoundingBox
from ..services.ai_service import ai_service
from ..utils.file_utils import file_manager


class AppController:
    """Main application controller implementing business logic."""
    
    def __init__(self):
        self.current_project: Optional[ProjectData] = None
        self.current_image: Optional[Image.Image] = None
        
        # Event callbacks
        self.on_project_changed: Optional[Callable[[Optional[ProjectData]], None]] = None
        self.on_analysis_completed: Optional[Callable[[AnalysisResult], None]] = None
        self.on_analysis_failed: Optional[Callable[[str], None]] = None
        self.on_image_loaded: Optional[Callable[[Image.Image], None]] = None
        self.on_status_changed: Optional[Callable[[str], None]] = None
    
    def create_new_project(self, name: str) -> bool:
        """Create a new project."""
        try:
            self.current_project = ProjectData(
                name=name,
                created_at=datetime.now().isoformat()
            )
            
            self._emit_status(f"✅ Создан новый проект: {name}")
            self._emit_project_changed()
            return True
            
        except Exception as e:
            self._emit_status(f"❌ Ошибка создания проекта: {e}")
            return False
    
    def load_project(self, file_path: str) -> bool:
        """Load project from file."""
        try:
            project = file_manager.load_project(file_path)
            if not project:
                self._emit_status("❌ Не удалось загрузить проект")
                return False
            
            self.current_project = project
            
            # Load associated image if available
            if project.image_path and os.path.exists(project.image_path):
                self.load_image(project.image_path)
            
            self._emit_status(f"✅ Проект загружен: {project.name}")
            self._emit_project_changed()
            return True
            
        except Exception as e:
            self._emit_status(f"❌ Ошибка загрузки проекта: {e}")
            return False
    
    def save_project(self, file_path: str) -> bool:
        """Save current project to file."""
        if not self.current_project:
            self._emit_status("❌ Нет активного проекта для сохранения")
            return False
        
        try:
            success = file_manager.save_project(self.current_project, file_path)
            if success:
                self._emit_status(f"✅ Проект сохранен: {file_path}")
            else:
                self._emit_status("❌ Не удалось сохранить проект")
            return success
            
        except Exception as e:
            self._emit_status(f"❌ Ошибка сохранения проекта: {e}")
            return False
    
    def load_image(self, file_path: str) -> bool:
        """Load image for analysis."""
        try:
            image = file_manager.load_image(file_path)
            if not image:
                self._emit_status("❌ Не удалось загрузить изображение")
                return False
            
            self.current_image = image
            
            # Update current project
            if self.current_project:
                self.current_project.image_path = file_path
            else:
                # Create new project
                project_name = os.path.splitext(os.path.basename(file_path))[0]
                self.create_new_project(project_name)
                if self.current_project:
                    self.current_project.image_path = file_path
            
            self._emit_status(f"✅ Изображение загружено: {os.path.basename(file_path)} ({image.size})")
            self._emit_image_loaded(image)
            self._emit_project_changed()
            return True
            
        except Exception as e:
            self._emit_status(f"❌ Ошибка загрузки изображения: {e}")
            return False
    
    def analyze_current_image(self) -> bool:
        """Analyze current image for UI elements."""
        if not self.current_image:
            self._emit_status("❌ Нет изображения для анализа")
            return False
        
        if not ai_service.is_available():
            self._emit_status("❌ AI сервис недоступен")
            return False
        
        try:
            self._emit_status("🤖 Начинаем анализ изображения...")
            
            result, status_msg = ai_service.analyze_image(self.current_image)
            
            if result:
                # Update project with results
                if self.current_project:
                    self.current_project.analysis_result = result
                    self.current_project.modified_at = datetime.now().isoformat()
                
                self._emit_status(status_msg)
                self._emit_analysis_completed(result)
                self._emit_project_changed()
                return True
            else:
                self._emit_status(status_msg)
                self._emit_analysis_failed(status_msg)
                return False
                
        except Exception as e:
            error_msg = f"❌ Критическая ошибка анализа: {e}"
            self._emit_status(error_msg)
            self._emit_analysis_failed(error_msg)
            return False
    
    def export_analysis(self, file_path: str, format_type: str = 'json') -> bool:
        """Export analysis results."""
        if not self.current_project or not self.current_project.analysis_result:
            self._emit_status("❌ Нет результатов анализа для экспорта")
            return False
        
        try:
            if format_type.lower() == 'json':
                success = file_manager.export_analysis_json(
                    self.current_project.analysis_result, file_path
                )
            elif format_type.lower() == 'text':
                success = file_manager.export_analysis_text(
                    self.current_project.analysis_result, file_path
                )
            else:
                self._emit_status(f"❌ Неподдерживаемый формат: {format_type}")
                return False
            
            if success:
                self._emit_status(f"✅ Результаты экспортированы: {file_path}")
            else:
                self._emit_status("❌ Не удалось экспортировать результаты")
            
            return success
            
        except Exception as e:
            self._emit_status(f"❌ Ошибка экспорта: {e}")
            return False
    
    def get_analysis_summary(self) -> dict:
        """Get summary of current analysis."""
        if not self.current_project or not self.current_project.analysis_result:
            return {}
        
        result = self.current_project.analysis_result
        element_types = {}
        
        for element in result.elements:
            element_type = element.element_type.value
            element_types[element_type] = element_types.get(element_type, 0) + 1
        
        return {
            'total_elements': len(result.elements),
            'element_types': element_types,
            'image_size': result.image_size,
            'analysis_time': result.analysis_time,
            'selected_elements': len(result.get_selected_elements())
        }
    
    def toggle_element_selection(self, element_id: str) -> bool:
        """Toggle selection state of an element."""
        if not self.current_project or not self.current_project.analysis_result:
            return False
        
        element = self.current_project.analysis_result.get_element_by_id(element_id)
        if element:
            element.is_selected = not element.is_selected
            return True
        return False
    
    def clear_selection(self):
        """Clear all element selections."""
        if not self.current_project or not self.current_project.analysis_result:
            return
        
        for element in self.current_project.analysis_result.elements:
            element.is_selected = False
    
    def select_all_elements(self):
        """Select all elements."""
        if not self.current_project or not self.current_project.analysis_result:
            return
        
        for element in self.current_project.analysis_result.elements:
            element.is_selected = True
    
    # Event emission helpers
    def _emit_project_changed(self):
        """Emit project changed event."""
        if self.on_project_changed:
            self.on_project_changed(self.current_project)
    
    def _emit_analysis_completed(self, result: AnalysisResult):
        """Emit analysis completed event."""
        if self.on_analysis_completed:
            self.on_analysis_completed(result)
    
    def _emit_analysis_failed(self, error_msg: str):
        """Emit analysis failed event."""
        if self.on_analysis_failed:
            self.on_analysis_failed(error_msg)
    
    def _emit_image_loaded(self, image: Image.Image):
        """Emit image loaded event."""
        if self.on_image_loaded:
            self.on_image_loaded(image)
    
    def _emit_status(self, message: str):
        """Emit status changed event."""
        if self.on_status_changed:
            self.on_status_changed(message)


# Global controller instance
app_controller = AppController()
