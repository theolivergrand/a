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
    MODEL_NAME = "gemini-2.5-flash-lite-preview-06-17"
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
    Creates an interactive HTML visualization with clear, non-blurred borders.
    """
    print(f"DEBUG: create_interactive_html called. Image: {image is not None}, JSON data present: {'elements' in json_data if isinstance(json_data, dict) else False}")
    print(f"DEBUG: JSON data received (first 100 chars): {str(json_data)[:100]}")

    if image is None or "elements" not in json_data or not isinstance(json_data.get("elements"), list):
        print("DEBUG: Invalid input for create_interactive_html.")
        return "<p>No elements to visualize or invalid data.</p>"
    
    # Convert PIL image to base64 for embedding in HTML
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Get image dimensions (should be the target size, e.g., 1024x1024)
    img_width, img_height = image.size
    
    # Create HTML with interactive areas - SHARP BORDERS for ML training
    html_content = f"""
    <div style="position: relative; width: {img_width}px; height: {img_height}px; margin: auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
        <img src="data:image/png;base64,{img_str}" 
             style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
             id="ui-image" />
        <div id="overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;">
    """
    
    # Add interactive areas for each element using absolute pixel values
    if isinstance(json_data.get("elements"), list):
        for element in json_data["elements"]:
            if "box" in element and "description" in element:
                box = element["box"]
                description = element["description"]
                element_id = element.get("id", "?")
                
                left_px = box[0]
                top_px = box[1]
                width_px = box[2] - box[0]
                height_px = box[3] - box[1]

                # SHARP BORDERS - NO TRANSPARENCY for ML training
                escaped_description = json.dumps(description)
                html_content += f"""
                <div class="ui-element" data-element-id="{element_id}" data-description="{description}"
                     style="position: absolute; 
                            left: {left_px}px; 
                            top: {top_px}px; 
                            width: {width_px}px; 
                            height: {height_px}px; 
                            border: 3px solid #00ff00; 
                            background-color: rgba(0, 255, 0, 0.05);
                            cursor: pointer;
                            pointer-events: auto;
                            border-radius: 4px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-weight: bold;
                            font-size: 16px;
                            color: #00ff00;
                            text-shadow: 1px 1px 2px rgba(0,0,0,0.9);"
                     onmouseover="showTooltip(event, {escaped_description}, {element_id})"
                     onmouseout="hideTooltip()"
                     onclick="selectElement({element_id}, {escaped_description})">
                    {element_id}
                </div>
                """
    
    html_content += """
        </div>
        <div id="tooltip" style="position: absolute; 
                                 background: rgba(0, 0, 0, 0.95); 
                                 color: white; 
                                 padding: 10px 15px; 
                                 border-radius: 8px; 
                                 font-size: 14px; 
                                 max-width: 300px; 
                                 z-index: 1000; 
                                 display: none;
                                 box-shadow: 0 6px 12px rgba(0,0,0,0.4);
                                 pointer-events: none;
                                 border: 1px solid #333;">
        </div>
    </div>

    <script>
        let selectedElementId = null;
        let gradioSelectedText = null;

        function showTooltip(event, description, elementId) {
            const tooltip = document.getElementById('tooltip');
            tooltip.innerHTML = `<strong>Элемент ${elementId}:</strong><br>${description}`;
            tooltip.style.display = 'block';
            
            // Position tooltip near cursor
            const rect = event.currentTarget.getBoundingClientRect();
            const container = event.currentTarget.closest('div[style*="position: relative"]');
            if (!container) return;
            const containerRect = container.getBoundingClientRect();
            
            tooltip.style.left = (rect.left - containerRect.left + rect.width + 10) + 'px';
            tooltip.style.top = (rect.top - containerRect.top) + 'px';

            // Enhanced hover effect with sharp borders
            if (elementId !== selectedElementId) {
                event.currentTarget.style.backgroundColor = 'rgba(0, 255, 0, 0.15)';
                event.currentTarget.style.borderWidth = '4px';
                event.currentTarget.style.borderColor = '#00ff00';
                event.currentTarget.style.boxShadow = '0 0 10px rgba(0, 255, 0, 0.5)';
            }
        }
        
        function hideTooltip() {
            const tooltip = document.getElementById('tooltip');
            tooltip.style.display = 'none';
            
            // Remove hover highlight if not selected
            const elements = document.querySelectorAll('.ui-element');
            elements.forEach(el => {
                const id = parseInt(el.textContent.trim());
                if (id !== selectedElementId) {
                    el.style.backgroundColor = 'rgba(0, 255, 0, 0.05)';
                    el.style.borderWidth = '3px';
                    el.style.borderColor = '#00ff00';
                    el.style.boxShadow = 'none';
                }
            });
        }
        
        function selectElement(elementId, description) {
            // Clear previous selection
            const elements = document.querySelectorAll('.ui-element');
            elements.forEach(el => {
                el.style.backgroundColor = 'rgba(0, 255, 0, 0.05)';
                el.style.borderWidth = '3px';
                el.style.borderColor = '#00ff00';
                el.style.boxShadow = 'none';
            });

            if (selectedElementId === elementId) {
                // Deselect if clicking the same element
                selectedElementId = null;
                gradioSelectedText = null;
                // Trigger Gradio update
                document.dispatchEvent(new CustomEvent('elementDeselected'));
            } else {
                // Select new element
                selectedElementId = elementId;
                gradioSelectedText = `Элемент ${elementId}: ${description}`;
                
                // Highlight selected element with sharp red border
                const selectedEl = Array.from(elements).find(el => 
                    parseInt(el.textContent.trim()) === elementId
                );
                if (selectedEl) {
                    selectedEl.style.backgroundColor = 'rgba(255, 0, 0, 0.1)';
                    selectedEl.style.borderWidth = '4px';
                    selectedEl.style.borderColor = '#ff0000';
                    selectedEl.style.boxShadow = '0 0 15px rgba(255, 0, 0, 0.6)';
                }
                
                // Trigger Gradio update
                document.dispatchEvent(new CustomEvent('elementSelected', {
                    detail: { elementId, description }
                }));
            }
        }
        
        // Function to get selected element info for Gradio
        function getSelectedElementInfo() {
            return gradioSelectedText || "Нажмите на элемент, чтобы увидеть его описание.";
        }
    </script>
    """
    return html_content


def handle_image_upload(image):
    """
    Handles the image upload and enables the analysis button.
    No resizing - image is used as-is.
    """
    if image is None:
        # If image is cleared, disable the button
        return None, gr.update(interactive=False), "Загрузите изображение для анализа."
    
    print(f"🖼️ Изображение загружено: {image.size} (используется в оригинальном размере)...")
    # No resizing - use original image
    print("✅ Изображение готово к анализу (оригинальный размер).")
    # Return the original image and enable the button
    return image, gr.update(interactive=True), "Изображение готово к анализу."


def analyze_ui_elements(processed_image):
    """
    Analyzes the UI elements in the given image using the Gemini model.
    """
    if processed_image is None:
        print("❌ ERROR: processed_image is None")
        return None, {"elements": []}, "Произошла ошибка: изображение для анализа отсутствует.", "Нажмите на элемент, чтобы увидеть его описание."
    
    print(f"🤖 Отправка изображения в Vertex AI: {processed_image.size}...")

    try:
        # Configure the generative model
        api_key = get_api_key(PROJECT_ID, SECRET_ID)
        genai.configure(api_key=api_key)

        # Create the model instance
        model = genai.GenerativeModel(MODEL_NAME)

        # Send the processed image to the model
        response = model.generate_content([SYSTEM_PROMPT, processed_image])
        
        # Clean up the response
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
        json_response = json.loads(cleaned_response)
        
        print(f"✅ Анализ успешно завершен: найдено {len(json_response.get('elements', []))} элементов.")
        
        # Return the *processed* image and the JSON data for visualization
        return processed_image, json_response, f"Найдено {len(json_response.get('elements', []))} элементов.", "Нажмите на элемент, чтобы увидеть его описание."

    except Exception as e:
        print(f"❌ Произошла ошибка во время анализа: {e}")
        return processed_image, {"elements": []}, f"Ошибка анализа: {e}", "Нажмите на элемент, чтобы увидеть его описание."


def handle_feedback(feedback_text):
    """
    Handles user feedback submission.
    """
    if not feedback_text.strip():
        return "Пожалуйста, введите ваш отзыв."
    
    print(f"📝 Получен отзыв пользователя: {feedback_text}")
    
    # Here you could save feedback to a database or file
    # For now, we'll just acknowledge receipt
    with open("feedback.txt", "a", encoding="utf-8") as f:
        f.write(f"Отзыв: {feedback_text}\n")
    
    return "Спасибо за ваш отзыв! Он поможет улучшить качество анализа."


def main():
    """Main function to launch the Gradio app."""
    print("Launching Gradio app...")

    # Define Gradio interface components
    with gr.Blocks(title=APP_TITLE, theme=gr.themes.Soft()) as demo:
        gr.Markdown(f"# {APP_TITLE}")
        gr.Markdown(APP_DESCRIPTION)

        with gr.Row():
            with gr.Column(scale=1):
                image_input = gr.Image(type="pil", label="Загрузите скриншот")
                submit_button = gr.Button("🔍 Проанализировать UI", variant="primary", interactive=False)
                status_output = gr.Textbox(label="Статус", interactive=False)

            with gr.Column(scale=2):
                gr.Markdown("### Интерактивный результат")
                # Using a simple HTML output for visualization
                html_output = gr.HTML()
                
                # Hidden component to store the JSON data
                json_data_output = gr.JSON(visible=False)
                
                # Hidden component to store the processed image
                processed_image_output = gr.Image(visible=False, type="pil")

        # Element information display
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Информация о выбранном элементе")
                element_info_output = gr.Textbox(
                    label="Описание элемента",
                    value="Нажмите на элемент, чтобы увидеть его описание.",
                    interactive=False,
                    lines=3
                )

        # Feedback section
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Форма обратной связи")
                gr.Markdown("Помогите улучшить качество анализа! Оставьте комментарий о точности определения элементов.")
                feedback_input = gr.Textbox(
                    label="Ваш отзыв",
                    placeholder="Например: 'Элемент 3 определен неточно, это не кнопка, а картинка...'",
                    lines=3
                )
                feedback_button = gr.Button("📤 Отправить отзыв", variant="secondary")
                feedback_status = gr.Textbox(label="Статус отзыва", interactive=False)

        # Define the actions inside the 'with' block
        image_input.upload(
            fn=handle_image_upload,
            inputs=image_input,
            outputs=[processed_image_output, submit_button, status_output]
        )
        
        image_input.clear(
            fn=lambda: (None, gr.update(interactive=False), None, None, "Пожалуйста, загрузите изображение для анализа.", "Нажмите на элемент, чтобы увидеть его описание."),
            inputs=[],
            outputs=[processed_image_output, submit_button, html_output, json_data_output, status_output, element_info_output]
        )
        
        submit_button.click(
            fn=analyze_ui_elements,
            inputs=processed_image_output,
            outputs=[processed_image_output, json_data_output, status_output, element_info_output]
        ).then(
            fn=create_interactive_html,
            inputs=[processed_image_output, json_data_output],
            outputs=html_output
        )
        
        feedback_button.click(
            fn=handle_feedback,
            inputs=feedback_input,
            outputs=feedback_status
        ).then(
            fn=lambda: "",
            inputs=[],
            outputs=feedback_input
        )

    # Launch the Gradio app
    print("🚀 Запускаем Gradio приложение...")
    # To make it accessible on the local network and create a public link
    demo.launch(server_name="127.0.0.1", server_port=7862, share=True, debug=True)

    print("\n" + "="*50)
    print("✅ Приложение запущено!")
    print("🔗 Публичная ссылка (для доступа откуда угодно): найдите в строке выше, она выглядит как https://....gradio.live")
    print(f"🏠 Локальная ссылка (для этого компьютера): http://127.0.0.1:7862")
    print("="*50 + "\n")


if __name__ == "__main__":
    main() 