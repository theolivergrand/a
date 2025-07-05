# -*- coding: utf-8 -*-
"""
Core library for UI element analysis with Vertex AI.
This file contains the business logic for analyzing images with Gemini
and does not contain any UI code.
"""
import json
import google.generativeai as genai
import google.cloud.secretmanager as secretmanager
from PIL import Image

# Configuration values should be loaded from a config file or env variables
PROJECT_ID = "ai-agent-test-464915"
SECRET_ID = "Gemini-Api"
MODEL_NAME = "gemini-1.5-flash"

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

def get_api_key(project_id, secret_id, version_id="latest"):
    """
    Retrieves a secret from Google Cloud Secret Manager.
    """
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"❌ Could not retrieve API key from Secret Manager: {e}")
        return None

def analyze_ui_elements(pil_image: Image.Image):
    """
    Analyzes the UI elements and returns the raw JSON from the model.
    Returns a tuple: (json_response, status_message)
    """
    if not isinstance(pil_image, Image.Image):
        return None, "Ошибка: передан неверный объект изображения."

    print(f"🤖 Отправка изображения в Vertex AI: {pil_image.size}...")
    try:
        api_key = get_api_key(PROJECT_ID, SECRET_ID)
        if not api_key:
            error_msg = "Ошибка: не удалось получить API ключ для Vertex AI."
            print(f"❌ {error_msg}")
            return None, error_msg

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content([SYSTEM_PROMPT, pil_image])
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()

        try:
            json_response = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            error_msg = f"Ошибка при разборе ответа от Vertex AI: {e}"
            print(f"❌ {error_msg}")
            return None, error_msg

        if "elements" not in json_response:
            error_msg = "Ошибка: неверный формат ответа от модели."
            print(f"❌ {error_msg}")
            return None, error_msg
        
        status_msg = f"✅ Анализ успешно завершен: найдено {len(json_response.get('elements', []))} элементов."
        print(status_msg)
        return json_response, status_msg

    except Exception as e:
        error_msg = f"Критическая ошибка анализа: {e}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return None, error_msg

if __name__ == "__main__":
    print("🔧 Тестирование модуля ai_analyzer...")
    print("ℹ️  Этот файл содержит бизнес-логику для анализа изображений.")
    print("🚀 Для запуска приложения используйте: python main.py")
    
    # Тест импорта
    try:
        print("✅ Импорт google.cloud.secretmanager успешен")
        print("✅ Импорт google.generativeai успешен")
        print("✅ Импорт PIL успешен")
        print("✅ Модуль готов к работе!")
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}") 