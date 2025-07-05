# -*- coding: utf-8 -*-
"""
Data models for the Desktop UI/UX Analyzer.
"""
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
from enum import Enum


class ElementType(Enum):
    """Types of UI elements."""
    BUTTON = "button"
    INPUT = "input"
    LABEL = "label"
    IMAGE = "image"
    ICON = "icon"
    MENU = "menu"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    DROPDOWN = "dropdown"
    LINK = "link"
    CONTAINER = "container"
    OTHER = "other"


@dataclass
class BoundingBox:
    """Represents coordinates of a bounding box."""
    x1: int
    y1: int
    x2: int
    y2: int
    
    @property
    def width(self) -> int:
        return self.x2 - self.x1
    
    @property
    def height(self) -> int:
        return self.y2 - self.y1
    
    @property
    def center(self) -> Tuple[int, int]:
        return (self.x1 + self.width // 2, self.y1 + self.height // 2)
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if point is inside the bounding box."""
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return {
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2
        }


@dataclass
class UIElement:
    """Represents a UI element detected by AI."""
    element_id: int
    description: str
    bounding_box: BoundingBox
    element_type: ElementType = ElementType.OTHER
    confidence: float = 1.0
    is_selected: bool = False
    is_hovered: bool = False
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def get_element_type_from_description(self) -> ElementType:
        """Determine element type from description."""
        desc_lower = self.description.lower()
        
        if any(word in desc_lower for word in ['button', 'btn', 'clickable']):
            return ElementType.BUTTON
        elif any(word in desc_lower for word in ['input', 'field', 'textbox', 'text field']):
            return ElementType.INPUT
        elif any(word in desc_lower for word in ['label', 'text', 'heading', 'title']):
            return ElementType.LABEL
        elif any(word in desc_lower for word in ['image', 'img', 'picture', 'photo']):
            return ElementType.IMAGE
        elif any(word in desc_lower for word in ['icon', 'symbol']):
            return ElementType.ICON
        elif any(word in desc_lower for word in ['menu', 'navigation', 'nav']):
            return ElementType.MENU
        elif any(word in desc_lower for word in ['checkbox', 'check box']):
            return ElementType.CHECKBOX
        elif any(word in desc_lower for word in ['radio', 'radio button']):
            return ElementType.RADIO
        elif any(word in desc_lower for word in ['dropdown', 'select', 'combobox']):
            return ElementType.DROPDOWN
        elif any(word in desc_lower for word in ['link', 'hyperlink']):
            return ElementType.LINK
        elif any(word in desc_lower for word in ['container', 'panel', 'box', 'card']):
            return ElementType.CONTAINER
        else:
            return ElementType.OTHER
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export."""
        return {
            "id": self.element_id,
            "description": self.description,
            "bounding_box": self.bounding_box.to_dict(),
            "type": self.element_type.value,
            "confidence": self.confidence,
            "metadata": self.metadata
        }


@dataclass
class AnalysisResult:
    """Result of UI analysis."""
    elements: List[UIElement]
    image_path: Optional[str] = None
    analysis_timestamp: Optional[str] = None
    total_elements: int = 0
    
    def __post_init__(self):
        self.total_elements = len(self.elements)
        
        # Auto-detect element types
        for element in self.elements:
            if element.element_type == ElementType.OTHER:
                element.element_type = element.get_element_type_from_description()
    
    def get_elements_by_type(self, element_type: ElementType) -> List[UIElement]:
        """Get elements filtered by type."""
        return [el for el in self.elements if el.element_type == element_type]
    
    def get_element_by_id(self, element_id: int) -> Optional[UIElement]:
        """Get element by ID."""
        for element in self.elements:
            if element.element_id == element_id:
                return element
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export."""
        return {
            "elements": [element.to_dict() for element in self.elements],
            "total_elements": self.total_elements,
            "image_path": self.image_path,
            "analysis_timestamp": self.analysis_timestamp
        }
