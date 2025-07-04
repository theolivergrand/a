# -*- coding: utf-8 -*-
"""
Gradio application for UI element analysis with Vertex AI.
"""

import gradio as gr
import io
import json
import base64
import zlib
import urllib.parse
from xml.etree import ElementTree as ET
from PIL import Image, ImageDraw

# NEW IMPORTS
import google.generativeai as genai
from google.cloud import secretmanager

# Configuration import
try:
    from config import PROJECT_ID, SECRET_ID, APP_TITLE, APP_DESCRIPTION, MODEL_NAME
except ImportError:
    # Fallback values if config.py doesn't exist
    PROJECT_ID = "ai-agent-test-464915"
    SECRET_ID = "Gemini-Api"
    APP_TITLE = "AI UI/UX Analyzer"
    APP_DESCRIPTION = "Загрузите скриншот пользовательского интерфейса, и ИИ определит и пронумерует интерактивные элементы."
    MODEL_NAME = "gemini-1.5-flash"
    print("⚠️  Файл config.py не найден. Используются значения по умолчанию.")
    print("📝 Скопируйте config_example.py в config.py и заполните ваши настройки.")

# This will be our system prompt
SYSTEM_PROMPT = """
You are an expert in UI/UX design. Your task is to analyze an image of a user interface and identify key interactive elements.
For each element you identify, provide its bounding box coordinates (top-left x, top-left y, bottom-right x, bottom-right y) and a brief description of the element and its likely function.
Number each element starting from 1.
Respond with a JSON object containing a single key "elements", which is a list of objects. Each object in the list should have three keys: "id" (a number starting from 1), "box" (a list of 4 integers for the coordinates) and "description" (a string).
Example:
{
  "elements": [
    {
      "id": 1,
      "box": [10, 20, 100, 50],
      "description": "A blue button with the text 'Submit'. Likely used to send form data."
    },
    {
      "id": 2,
      "box": [10, 80, 200, 110],
      "description": "A text input field with a placeholder 'Enter your name'. Used for user text input."
    }
  ]
}
"""


def get_api_key(project_id, secret_id, version_id="latest"):
    """
    Retrieves a secret from Google Cloud Secret Manager.
    """
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    # Return the secret payload.
    return response.payload.data.decode("UTF-8")


def parse_drawio_diagram(file_path):
    """
    Parses a Draw.io diagram file (XML) to extract nodes and edges.
    This is a placeholder and will be replaced with actual parsing logic.
    """
    nodes = {}
    edges = []
    
    # In a real scenario, you would parse the XML file here
    # to extract node IDs, positions, and connections.
    # For now, we'll just return dummy data.
    return nodes, edges

def run_agent(nodes, edges):
    """
    Executes the agent logic based on the parsed diagram.
    For now, it just prints the flow.
    """
    # In a real scenario, you would implement the agent's logic
    # here, using the parsed nodes and edges.
    # For now, we'll just simulate the flow.
    print("Agent started.")
    # Example: Iterate through nodes and edges to simulate a simple flow
    for node_id, node_value in nodes.items():
        print(f"Agent visiting node {node_id} ('{node_value}').")
        # Simulate processing time
        import time
        time.sleep(1)
    print("Agent finished.")
    return "Agent run completed following the diagram."

def create_interactive_html(image, json_data):
    """
    Creates an interactive HTML visualization with hover areas over the original image.
    """
    if image is None or "elements" not in json_data:
        return "<p>No elements to visualize</p>"
    
    # Convert PIL image to base64 for embedding in HTML
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Get image dimensions
    img_width, img_height = image.size
    
    # Create HTML with interactive areas
    html_content = f"""
    <div style="position: relative; display: inline-block; max-width: 100%; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
        <img src="data:image/png;base64,{img_str}" 
             style="width: 100%; height: auto; display: block;" 
             id="ui-image" />
        <div id="overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;">
    """
    
    # Add interactive areas for each element
    if isinstance(json_data.get("elements"), list):
        for element in json_data["elements"]:
            if "box" in element and "description" in element:
                box = element["box"]
                description = element["description"]
                element_id = element.get("id", "?")
                
                # Calculate percentages for responsive positioning
                left_percent = (box[0] / img_width) * 100
                top_percent = (box[1] / img_height) * 100
                width_percent = ((box[2] - box[0]) / img_width) * 100
                height_percent = ((box[3] - box[1]) / img_height) * 100
                
                html_content += f"""
                <div class="ui-element" 
                     style="position: absolute; 
                            left: {left_percent}%; 
                            top: {top_percent}%; 
                            width: {width_percent}%; 
                            height: {height_percent}%; 
                            border: 2px solid #00ff00; 
                            background-color: rgba(0, 255, 0, 0.1);
                            cursor: pointer;
                            pointer-events: auto;
                            border-radius: 4px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-weight: bold;
                            color: #00ff00;
                            text-shadow: 1px 1px 2px rgba(0,0,0,0.8);"
                     onmouseover="showTooltip(event, '{description.replace("'", "\\'")}', {element_id})"
                     onmouseout="hideTooltip()"
                     onclick="selectElement({element_id})">
                    {element_id}
                </div>
                """
    
    html_content += """
        </div>
        <div id="tooltip" style="position: absolute; 
                                 background: rgba(0, 0, 0, 0.9); 
                                 color: white; 
                                 padding: 8px 12px; 
                                 border-radius: 6px; 
                                 font-size: 14px; 
                                 max-width: 300px; 
                                 z-index: 1000; 
                                 display: none;
                                 box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                                 pointer-events: none;">
        </div>
    </div>
    
    <script>
        function showTooltip(event, description, elementId) {
            const tooltip = document.getElementById('tooltip');
            tooltip.innerHTML = `<strong>Element ${elementId}:</strong><br>${description}`;
            tooltip.style.display = 'block';
            
            // Position tooltip near cursor
            const rect = event.currentTarget.getBoundingClientRect();
            const container = event.currentTarget.closest('div');
            const containerRect = container.getBoundingClientRect();
            
            tooltip.style.left = (rect.left - containerRect.left + rect.width + 10) + 'px';
            tooltip.style.top = (rect.top - containerRect.top) + 'px';
            
            // Highlight the element
            event.currentTarget.style.backgroundColor = 'rgba(0, 255, 0, 0.3)';
            event.currentTarget.style.borderWidth = '3px';
        }
        
        function hideTooltip() {
            const tooltip = document.getElementById('tooltip');
            tooltip.style.display = 'none';
            
            // Remove highlight
            const elements = document.querySelectorAll('.ui-element');
            elements.forEach(el => {
                el.style.backgroundColor = 'rgba(0, 255, 0, 0.1)';
                el.style.borderWidth = '2px';
            });
        }
        
        function selectElement(elementId) {
            alert(`Выбран элемент ${elementId}`);
        }
    </script>
    """
    
    return html_content


def analyze_ui_elements(image):
    """
    This function calls the Gemini API to analyze the image.
    """
    if image is None:
        return {}, None, "<p>Загрузите изображение для анализа</p>"
        
    try:
        # 1. Get API Key by calling get_api_key()
        api_key = get_api_key(PROJECT_ID, SECRET_ID)

        # 2. Configure the generative model with the key
        genai.configure(api_key=api_key)

        # 3. Create the model instance
        model = genai.GenerativeModel(MODEL_NAME)

        # 4. Create a prompt with the system prompt and the user image
        prompt_parts = [
            SYSTEM_PROMPT,
            image
        ]
        
        # 5. Call the model
        response = model.generate_content(prompt_parts)
        
        # 6. Get the JSON response
        # The response text might be enclosed in markdown backticks
        response_text = response.text.strip().replace("```json", "").replace("```", "")
        json_response = json.loads(response_text)
        
        # 7. Create interactive HTML and return
        interactive_html = create_interactive_html(image, json_response)
        return json_response, draw_boxes(image, json_response), interactive_html

    except Exception as e:
        print(f"An error occurred: {e}")
        # Return a user-friendly error message in the UI
        error_message = {"error": str(e)}
        return error_message, None, f"<p>Ошибка: {str(e)}</p>"


def draw_boxes(image, json_data):
    """
    Draws numbered bounding boxes on the image based on the JSON data.
    """
    image_with_boxes = image.copy()
    draw = ImageDraw.Draw(image_with_boxes)

    # Check if 'elements' key exists and is a list
    if "elements" in json_data and isinstance(json_data["elements"], list):
        for element in json_data["elements"]:
            # Check if 'box' and 'description' keys exist
            if "box" in element and "description" in element:
                box = element["box"]
                description = element["description"]
                element_id = element.get("id", "?")
                
                # Draw thin bright green rectangle
                draw.rectangle(box, outline="#00ff00", width=2)
                
                # Draw number in the center of the box
                center_x = (box[0] + box[2]) // 2
                center_y = (box[1] + box[3]) // 2
                
                # Draw background circle for number
                circle_radius = 15
                draw.ellipse([center_x - circle_radius, center_y - circle_radius,
                             center_x + circle_radius, center_y + circle_radius],
                            fill="#00ff00", outline="#ffffff", width=2)
                
                # Draw number text
                draw.text((center_x, center_y), str(element_id), 
                         fill="black", anchor="mm", font_size=20)

    return image_with_boxes


def main():
    """Main function to launch the Gradio app."""
    print("Launching Gradio app...")

    # Gradio Interface
    with gr.Blocks(title=APP_TITLE) as demo:
        gr.Markdown(f"# 🎯 {APP_TITLE}")
        gr.Markdown(APP_DESCRIPTION)
        
        with gr.Row():
            image_input = gr.Image(type="pil", label="📱 Загрузите скриншот UI")
            
        with gr.Row():
            with gr.Column(scale=1):
                image_output = gr.Image(label="🖼️ Анализ с рамками")
                json_output = gr.JSON(label="📋 Обнаруженные элементы")
            with gr.Column(scale=1):
                html_output = gr.HTML(label="✨ Интерактивная визуализация")
        
        image_input.change(
            fn=analyze_ui_elements,
            inputs=image_input,
            outputs=[json_output, image_output, html_output]
        )

    demo.launch()


if __name__ == "__main__":
    main() 