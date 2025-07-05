# -*- coding: utf-8 -*-
"""
Basic tests for the refactored Desktop UI/UX Analyzer.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.models.ui_element import UIElement, BoundingBox, ElementType, AnalysisResult
from src.utils.file_utils import FileUtils
from config.config import config_manager


class TestUIElement:
    """Test UIElement model."""
    
    def test_bounding_box_creation(self):
        """Test BoundingBox creation and properties."""
        bbox = BoundingBox(10, 20, 100, 120)
        
        assert bbox.x1 == 10
        assert bbox.y1 == 20
        assert bbox.x2 == 100
        assert bbox.y2 == 120
        assert bbox.width == 90
        assert bbox.height == 100
        assert bbox.center == (55, 70)
    
    def test_bounding_box_contains_point(self):
        """Test point containment in bounding box."""
        bbox = BoundingBox(10, 20, 100, 120)
        
        assert bbox.contains_point(50, 60) == True
        assert bbox.contains_point(5, 60) == False
        assert bbox.contains_point(150, 60) == False
        assert bbox.contains_point(50, 10) == False
        assert bbox.contains_point(50, 130) == False
    
    def test_ui_element_creation(self):
        """Test UIElement creation."""
        bbox = BoundingBox(10, 20, 100, 120)
        element = UIElement(
            element_id=1,
            description="Test button",
            bounding_box=bbox,
            element_type=ElementType.BUTTON
        )
        
        assert element.element_id == 1
        assert element.description == "Test button"
        assert element.element_type == ElementType.BUTTON
        assert element.bounding_box == bbox
        assert element.is_selected == False
        assert element.is_hovered == False
    
    def test_element_type_detection(self):
        """Test automatic element type detection."""
        bbox = BoundingBox(10, 20, 100, 120)
        
        # Test button detection
        button_element = UIElement(
            element_id=1,
            description="Primary blue button with text Submit",
            bounding_box=bbox
        )
        assert button_element.get_element_type_from_description() == ElementType.BUTTON
        
        # Test input detection
        input_element = UIElement(
            element_id=2,
            description="Text input field for username",
            bounding_box=bbox
        )
        assert input_element.get_element_type_from_description() == ElementType.INPUT
        
        # Test icon detection
        icon_element = UIElement(
            element_id=3,
            description="Small information icon",
            bounding_box=bbox
        )
        assert icon_element.get_element_type_from_description() == ElementType.ICON


class TestAnalysisResult:
    """Test AnalysisResult model."""
    
    def test_analysis_result_creation(self):
        """Test AnalysisResult creation."""
        bbox1 = BoundingBox(10, 20, 100, 120)
        bbox2 = BoundingBox(110, 20, 200, 120)
        
        element1 = UIElement(1, "Button", bbox1, ElementType.BUTTON)
        element2 = UIElement(2, "Input field", bbox2, ElementType.INPUT)
        
        result = AnalysisResult(
            elements=[element1, element2],
            image_path="/test/image.png"
        )
        
        assert len(result.elements) == 2
        assert result.total_elements == 2
        assert result.image_path == "/test/image.png"
    
    def test_get_element_by_id(self):
        """Test getting element by ID."""
        bbox = BoundingBox(10, 20, 100, 120)
        element = UIElement(5, "Test element", bbox, ElementType.BUTTON)
        
        result = AnalysisResult(elements=[element])
        
        found_element = result.get_element_by_id(5)
        assert found_element == element
        
        not_found = result.get_element_by_id(999)
        assert not_found is None
    
    def test_get_elements_by_type(self):
        """Test filtering elements by type."""
        bbox = BoundingBox(10, 20, 100, 120)
        
        button1 = UIElement(1, "Button 1", bbox, ElementType.BUTTON)
        button2 = UIElement(2, "Button 2", bbox, ElementType.BUTTON)
        input1 = UIElement(3, "Input 1", bbox, ElementType.INPUT)
        
        result = AnalysisResult(elements=[button1, button2, input1])
        
        buttons = result.get_elements_by_type(ElementType.BUTTON)
        assert len(buttons) == 2
        assert button1 in buttons
        assert button2 in buttons
        
        inputs = result.get_elements_by_type(ElementType.INPUT)
        assert len(inputs) == 1
        assert input1 in inputs


class TestFileUtils:
    """Test file utility functions."""
    
    def test_file_extension_detection(self):
        """Test file extension detection."""
        assert FileUtils.get_file_extension("test.jpg") == ".jpg"
        assert FileUtils.get_file_extension("test.PNG") == ".png"
        assert FileUtils.get_file_extension("path/to/file.JPEG") == ".jpeg"
    
    def test_image_file_detection(self):
        """Test image file detection."""
        assert FileUtils.is_image_file("test.jpg") == True
        assert FileUtils.is_image_file("test.png") == True
        assert FileUtils.is_image_file("test.gif") == True
        assert FileUtils.is_image_file("test.txt") == False
        assert FileUtils.is_image_file("test.pdf") == False
    
    def test_timestamp_filename_generation(self):
        """Test timestamp filename generation."""
        filename = FileUtils.generate_timestamp_filename("test", "suffix", "json")
        
        assert filename.startswith("test_")
        assert filename.endswith("_suffix.json")
        assert len(filename) > 20  # Should contain timestamp


class TestConfiguration:
    """Test configuration management."""
    
    def test_config_manager_initialization(self):
        """Test config manager initialization."""
        config = config_manager.config
        
        assert config is not None
        assert config.ai is not None
        assert config.ui is not None
        assert hasattr(config, 'debug')
        assert hasattr(config, 'log_level')
    
    def test_ai_config_properties(self):
        """Test AI configuration properties."""
        ai_config = config_manager.get_ai_config()
        
        assert ai_config.project_id is not None
        assert ai_config.secret_id is not None
        assert ai_config.model_name is not None
        assert "gemini" in ai_config.model_name.lower()
    
    def test_ui_config_properties(self):
        """Test UI configuration properties."""
        ui_config = config_manager.get_ui_config()
        
        assert ui_config.window_width > 0
        assert ui_config.window_height > 0
        assert ui_config.box_width > 0
        assert ui_config.handle_size > 0
        assert ui_config.window_title is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
