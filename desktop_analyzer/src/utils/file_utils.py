# -*- coding: utf-8 -*-
"""
File utilities for the Desktop UI/UX Analyzer.
"""
import os
import json
from typing import Optional, Dict, Any
from datetime import datetime
from PIL import Image

from ..models.data_models import ProjectData, AnalysisResult


class FileManager:
    """Manages file operations for the application."""
    
    SUPPORTED_IMAGE_FORMATS = {
        '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'
    }
    
    PROJECT_FILE_EXTENSION = '.json'
    
    @staticmethod
    def is_image_file(file_path: str) -> bool:
        """Check if file is a supported image format."""
        _, ext = os.path.splitext(file_path.lower())
        return ext in FileManager.SUPPORTED_IMAGE_FORMATS
    
    @staticmethod
    def load_image(file_path: str) -> Optional[Image.Image]:
        """Load image from file."""
        try:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return None
                
            if not FileManager.is_image_file(file_path):
                print(f"❌ Unsupported image format: {file_path}")
                return None
                
            image = Image.open(file_path)
            print(f"✅ Image loaded: {file_path} ({image.size})")
            return image
            
        except Exception as e:
            print(f"❌ Error loading image {file_path}: {e}")
            return None
    
    @staticmethod
    def save_project(project: ProjectData, file_path: str) -> bool:
        """Save project data to file."""
        try:
            project_dict = {
                'name': project.name,
                'image_path': project.image_path,
                'created_at': project.created_at,
                'modified_at': datetime.now().isoformat(),
                'analysis_result': None
            }
            
            # Serialize analysis result if available
            if project.analysis_result:
                elements_data = []
                for element in project.analysis_result.elements:
                    element_data = {
                        'id': element.element_id,
                        'rect': {
                            'x': element.rect.x,
                            'y': element.rect.y,
                            'width': element.rect.width,
                            'height': element.rect.height
                        },
                        'description': element.description,
                        'element_type': element.element_type.value,
                        'confidence': element.confidence
                    }
                    elements_data.append(element_data)
                
                project_dict['analysis_result'] = {
                    'elements': elements_data,
                    'image_size': project.analysis_result.image_size,
                    'analysis_time': project.analysis_result.analysis_time,
                    'status_message': project.analysis_result.status_message
                }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_dict, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Project saved: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving project {file_path}: {e}")
            return False
    
    @staticmethod
    def load_project(file_path: str) -> Optional[ProjectData]:
        """Load project data from file."""
        try:
            if not os.path.exists(file_path):
                print(f"❌ Project file not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                project_dict = json.load(f)
            
            # Create project
            project = ProjectData(
                name=project_dict.get('name', 'Unnamed Project'),
                image_path=project_dict.get('image_path'),
                created_at=project_dict.get('created_at'),
                modified_at=project_dict.get('modified_at')
            )
            
            # Load analysis result if available
            if 'analysis_result' in project_dict and project_dict['analysis_result']:
                result_data = project_dict['analysis_result']
                
                # Deserialize elements
                elements = []
                for element_data in result_data.get('elements', []):
                    from ..models.data_models import BoundingBox, ElementType, Rectangle
                    
                    rect_data = element_data['rect']
                    rect = Rectangle(
                        x=rect_data['x'],
                        y=rect_data['y'],
                        width=rect_data['width'],
                        height=rect_data['height']
                    )
                    
                    element_type = ElementType(element_data.get('element_type', 'unknown'))
                    
                    bbox = BoundingBox(
                        rect=rect,
                        description=element_data['description'],
                        element_id=element_data['id'],
                        element_type=element_type,
                        confidence=element_data.get('confidence', 0.0)
                    )
                    elements.append(bbox)
                
                project.analysis_result = AnalysisResult(
                    elements=elements,
                    image_size=tuple(result_data.get('image_size', (0, 0))),
                    analysis_time=result_data.get('analysis_time', 0.0),
                    status_message=result_data.get('status_message', '')
                )
            
            print(f"✅ Project loaded: {file_path}")
            return project
            
        except Exception as e:
            print(f"❌ Error loading project {file_path}: {e}")
            return None
    
    @staticmethod
    def export_analysis_json(analysis_result: AnalysisResult, file_path: str) -> bool:
        """Export analysis results to JSON file."""
        try:
            export_data = {
                'metadata': {
                    'export_time': datetime.now().isoformat(),
                    'image_size': analysis_result.image_size,
                    'analysis_time': analysis_result.analysis_time,
                    'element_count': len(analysis_result.elements)
                },
                'elements': []
            }
            
            for element in analysis_result.elements:
                element_data = {
                    'id': element.element_id,
                    'type': element.element_type.value,
                    'description': element.description,
                    'confidence': element.confidence,
                    'bounding_box': {
                        'x': element.rect.x,
                        'y': element.rect.y,
                        'width': element.rect.width,
                        'height': element.rect.height
                    }
                }
                export_data['elements'].append(element_data)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Analysis exported to JSON: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting analysis {file_path}: {e}")
            return False
    
    @staticmethod
    def export_analysis_text(analysis_result: AnalysisResult, file_path: str) -> bool:
        """Export analysis results to text file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("UI/UX Analysis Report\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Image Size: {analysis_result.image_size[0]}x{analysis_result.image_size[1]}\n")
                f.write(f"Analysis Time: {analysis_result.analysis_time:.2f} seconds\n")
                f.write(f"Elements Found: {len(analysis_result.elements)}\n\n")
                
                for i, element in enumerate(analysis_result.elements, 1):
                    f.write(f"Element {i} (ID: {element.element_id})\n")
                    f.write("-" * 30 + "\n")
                    f.write(f"Type: {element.element_type.value}\n")
                    f.write(f"Position: ({element.rect.x}, {element.rect.y})\n")
                    f.write(f"Size: {element.rect.width}x{element.rect.height}\n")
                    f.write(f"Confidence: {element.confidence:.2f}\n")
                    f.write(f"Description: {element.description}\n\n")
            
            print(f"✅ Analysis exported to text: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting analysis {file_path}: {e}")
            return False


# Global file manager instance
file_manager = FileManager()
