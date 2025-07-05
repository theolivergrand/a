# -*- coding: utf-8 -*-
"""
AI analysis service for UI element detection.
"""
import json
import time
from typing import Optional, Tuple, List, Any
from PIL import Image

try:
    import google.generativeai as genai
    import google.cloud.secretmanager as secretmanager
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False

from ..models.data_models import AnalysisResult, BoundingBox, ElementType, Rectangle
from ...config.config import config_manager


class AIAnalysisService:
    """Service for AI-powered UI element analysis."""
    
    SYSTEM_PROMPT = """
You are an expert in UI/UX design. Your task is to analyze an image of a user interface and identify ALL interactive and visual elements with high precision.

ELEMENT TYPES TO IDENTIFY:
- Buttons (primary, secondary, icon buttons, toggle buttons)
- Input fields (text, password, search, number, date)
- Dropdown menus and select boxes
- Checkboxes and radio buttons
- Navigation elements (menus, breadcrumbs, tabs)
- Text elements (headings, labels, paragraphs)
- Images and icons
- Links and hyperlinks
- Cards and containers
- Progress bars and sliders
- Modals and popups
- Form elements
- List items
- Tables and data grids

ANALYSIS REQUIREMENTS:
1. Be thorough - identify even small elements like icons, separators, and decorative elements
2. Provide precise bounding box coordinates (top-left x, top-left y, bottom-right x, bottom-right y)
3. Include detailed descriptions with:
   - Visual appearance (color, size, style)
   - Text content (if visible)
   - Likely function/purpose
   - Element type classification
4. Number each element starting from 1
5. Consider accessibility and usability aspects

RESPONSE FORMAT:
JSON object with "elements" key containing array of objects with:
- "id": number starting from 1
- "box": [x1, y1, x2, y2] coordinates
- "description": detailed description including type, appearance, and function

Example:
{
  "elements": [
    {
      "id": 1,
      "box": [10, 20, 100, 50],
      "description": "Primary blue button with white text 'Submit'. Rounded corners, appears clickable. Likely used to submit form data or confirm an action."
    },
    {
      "id": 2,
      "box": [120, 25, 140, 45],
      "description": "Small gray information icon (i symbol). Circular background, appears to be a tooltip trigger for additional help information."
    }
  ]
}
"""
    
    def __init__(self):
        self.config = config_manager.get_ai_config()
        self._api_key: Optional[str] = None
        self._model: Optional[Any] = None
        
    def _get_api_key(self) -> Optional[str]:
        """Get API key from Secret Manager or direct config."""
        if self._api_key:
            return self._api_key
            
        # Try direct API key first
        if self.config.api_key:
            self._api_key = self.config.api_key
            return self._api_key
            
        # Try Secret Manager
        if not GOOGLE_AI_AVAILABLE:
            return None
            
        try:
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{self.config.project_id}/secrets/{self.config.secret_id}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            self._api_key = response.payload.data.decode("UTF-8")
            return self._api_key
        except Exception as e:
            print(f"❌ Could not retrieve API key from Secret Manager: {e}")
            return None
    
    def _initialize_model(self) -> bool:
        """Initialize the AI model."""
        if not GOOGLE_AI_AVAILABLE:
            print("❌ Google AI libraries not available")
            return False
            
        api_key = self._get_api_key()
        if not api_key:
            print("❌ API key not available")
            return False
            
        try:
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(self.config.model_name)
            return True
        except Exception as e:
            print(f"❌ Failed to initialize model: {e}")
            return False
    
    def _classify_element_type(self, description: str) -> ElementType:
        """Classify element type based on description."""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['button', 'btn', 'clickable']):
            return ElementType.BUTTON
        elif any(word in description_lower for word in ['input', 'field', 'textbox', 'text box']):
            return ElementType.INPUT
        elif any(word in description_lower for word in ['label', 'heading', 'title']):
            return ElementType.LABEL
        elif any(word in description_lower for word in ['image', 'img', 'photo', 'picture']):
            return ElementType.IMAGE
        elif any(word in description_lower for word in ['link', 'hyperlink', 'url']):
            return ElementType.LINK
        elif any(word in description_lower for word in ['menu', 'navigation', 'nav']):
            return ElementType.MENU
        elif any(word in description_lower for word in ['checkbox', 'check box']):
            return ElementType.CHECKBOX
        elif any(word in description_lower for word in ['radio', 'radio button']):
            return ElementType.RADIO
        elif any(word in description_lower for word in ['dropdown', 'select', 'combobox']):
            return ElementType.DROPDOWN
        elif any(word in description_lower for word in ['icon', 'symbol']):
            return ElementType.ICON
        elif any(word in description_lower for word in ['container', 'panel', 'box', 'card']):
            return ElementType.CONTAINER
        elif any(word in description_lower for word in ['text', 'paragraph', 'content']):
            return ElementType.TEXT
        else:
            return ElementType.UNKNOWN
    
    def _parse_analysis_response(self, response_text: str, image_size: Tuple[int, int]) -> List[BoundingBox]:
        """Parse AI response into BoundingBox objects."""
        try:
            # Clean response
            cleaned_response = response_text.strip().replace("```json", "").replace("```", "").strip()
            json_response = json.loads(cleaned_response)
            
            if "elements" not in json_response:
                raise ValueError("Invalid response format: missing 'elements' key")
            
            elements = []
            for element_data in json_response["elements"]:
                if "box" not in element_data or "description" not in element_data:
                    continue
                    
                box_coords = element_data["box"]
                if len(box_coords) != 4:
                    continue
                    
                # Create rectangle
                x1, y1, x2, y2 = box_coords
                width = x2 - x1
                height = y2 - y1
                rect = Rectangle(x1, y1, width, height)
                
                # Create bounding box
                element_id = str(element_data.get("id", len(elements) + 1))
                description = element_data["description"]
                element_type = self._classify_element_type(description)
                
                bbox = BoundingBox(
                    rect=rect,
                    description=description,
                    element_id=element_id,
                    element_type=element_type,
                    confidence=element_data.get("confidence", 0.0)
                )
                
                elements.append(bbox)
            
            return elements
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"❌ Error parsing response: {e}")
            return []
    
    def analyze_image(self, image: Image.Image) -> Tuple[Optional[AnalysisResult], str]:
        """
        Analyze image for UI elements.
        
        Returns:
            Tuple of (AnalysisResult or None, status_message)
        """
        if not isinstance(image, Image.Image):
            return None, "Ошибка: передан неверный объект изображения."
        
        print(f"🤖 Отправка изображения в AI: {image.size}...")
        start_time = time.time()
        
        # Initialize model if needed
        if not self._model and not self._initialize_model():
            return None, "Ошибка: не удалось инициализировать AI модель."
        
        try:
            # Generate analysis
            if not self._model:
                raise RuntimeError("Model not initialized")
            response = self._model.generate_content([self.SYSTEM_PROMPT, image])
            analysis_time = time.time() - start_time
            
            # Parse response
            elements = self._parse_analysis_response(response.text, image.size)
            
            if not elements:
                return None, "Ошибка: не удалось обнаружить элементы в изображении."
            
            # Create result
            result = AnalysisResult(
                elements=elements,
                image_size=image.size,
                analysis_time=analysis_time,
                status_message=f"✅ Анализ успешно завершен: найдено {len(elements)} элементов.",
                raw_response={"text": response.text}
            )
            
            print(result.status_message)
            return result, result.status_message
            
        except Exception as e:
            error_msg = f"Критическая ошибка анализа: {e}"
            print(f"❌ {error_msg}")
            return None, error_msg
    
    def is_available(self) -> bool:
        """Check if AI service is available."""
        return GOOGLE_AI_AVAILABLE and self._get_api_key() is not None


# Global service instance
ai_service = AIAnalysisService()
