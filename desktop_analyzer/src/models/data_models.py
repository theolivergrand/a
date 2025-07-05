# -*- coding: utf-8 -*-
"""
Data models for the Desktop UI/UX Analyzer.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


class ElementType(Enum):
    """UI element types."""
    BUTTON = "button"
    INPUT = "input"
    LABEL = "label"
    IMAGE = "image"
    LINK = "link"
    MENU = "menu"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    DROPDOWN = "dropdown"
    ICON = "icon"
    CONTAINER = "container"
    TEXT = "text"
    UNKNOWN = "unknown"


@dataclass
class Rectangle:
    """Simple rectangle representation."""
    x: int
    y: int
    width: int
    height: int
    
    def contains(self, point_x: int, point_y: int) -> bool:
        """Check if point is within rectangle."""
        return (self.x <= point_x <= self.x + self.width and 
                self.y <= point_y <= self.y + self.height)
    
    def center(self) -> Tuple[int, int]:
        """Get center point."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def right(self) -> int:
        """Get right edge."""
        return self.x + self.width
    
    def bottom(self) -> int:
        """Get bottom edge."""
        return self.y + self.height


@dataclass
class BoundingBox:
    """Represents a bounding box for a detected UI element."""
    rect: Rectangle
    description: str
    element_id: str
    element_type: ElementType = ElementType.UNKNOWN
    confidence: float = 0.0
    is_selected: bool = False
    is_hovered: bool = False
    is_dragging: bool = False
    is_resizing: bool = False
    resize_handle: Optional[str] = None
    
    # UI properties
    resize_handle_size: int = 8
    scaled_rect: Optional[Rectangle] = None
    resize_handles: Dict[str, Rectangle] = field(default_factory=dict)
    
    # Resize handle types
    HANDLE_TYPES = {
        'top-left': 'nw-resize',
        'top-right': 'ne-resize', 
        'bottom-left': 'sw-resize',
        'bottom-right': 'se-resize',
        'top': 'n-resize',
        'bottom': 's-resize',
        'left': 'w-resize',
        'right': 'e-resize'
    }
    
    def contains(self, point_x: int, point_y: int) -> bool:
        """Check if point is within the bounding box."""
        if self.scaled_rect:
            return self.scaled_rect.contains(point_x, point_y)
        return self.rect.contains(point_x, point_y)
    
    def get_resize_handle_at(self, point_x: int, point_y: int) -> Optional[str]:
        """Get resize handle at the given point."""
        for handle_type, handle_rect in self.resize_handles.items():
            if handle_rect.contains(point_x, point_y):
                return handle_type
        return None
    
    def update_resize_handles(self):
        """Update resize handle positions."""
        if not self.scaled_rect:
            return
            
        size = self.resize_handle_size
        rect = self.scaled_rect
        center_x, center_y = rect.center()
        
        self.resize_handles = {
            'top-left': Rectangle(rect.x - size//2, rect.y - size//2, size, size),
            'top-right': Rectangle(rect.right() - size//2, rect.y - size//2, size, size),
            'bottom-left': Rectangle(rect.x - size//2, rect.bottom() - size//2, size, size),
            'bottom-right': Rectangle(rect.right() - size//2, rect.bottom() - size//2, size, size),
            'top': Rectangle(center_x - size//2, rect.y - size//2, size, size),
            'bottom': Rectangle(center_x - size//2, rect.bottom() - size//2, size, size),
            'left': Rectangle(rect.x - size//2, center_y - size//2, size, size),
            'right': Rectangle(rect.right() - size//2, center_y - size//2, size, size)
        }


@dataclass
class AnalysisResult:
    """Result of UI element analysis."""
    elements: List[BoundingBox]
    image_size: Tuple[int, int]
    analysis_time: float
    status_message: str
    raw_response: Optional[dict] = None
    
    def get_element_by_id(self, element_id: str) -> Optional[BoundingBox]:
        """Get element by ID."""
        for element in self.elements:
            if element.element_id == element_id:
                return element
        return None
    
    def get_elements_by_type(self, element_type: ElementType) -> List[BoundingBox]:
        """Get elements by type."""
        return [element for element in self.elements if element.element_type == element_type]
    
    def get_selected_elements(self) -> List[BoundingBox]:
        """Get selected elements."""
        return [element for element in self.elements if element.is_selected]


@dataclass
class ProjectData:
    """Project data container."""
    name: str
    image_path: Optional[str] = None
    analysis_result: Optional[AnalysisResult] = None
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
    
    def has_analysis(self) -> bool:
        """Check if project has analysis results."""
        return self.analysis_result is not None and len(self.analysis_result.elements) > 0
    
    def get_element_count(self) -> int:
        """Get total number of elements."""
        if not self.analysis_result:
            return 0
        return len(self.analysis_result.elements)
