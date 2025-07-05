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
    <div id="interactive-container" style="position: relative; width: {img_width}px; height: {img_height}px; margin: auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
        <img src="data:image/png;base64,{img_str}" 
             style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
             id="ui-image" />
        <div id="overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;">
    """
    
    # Store element data as JSON for JavaScript
    elements_data = []
    
    # Add interactive areas for each element using absolute pixel values
    if isinstance(json_data.get("elements"), list):
        for element in json_data["elements"]:
            if "box" in element and "description" in element:
                box = element["box"]
                description = element["description"]
                element_id = element.get("id", "?")
                
                # Store element data
                elements_data.append({
                    "id": element_id,
                    "description": description
                })
                
                left_px = box[0]
                top_px = box[1]
                width_px = box[2] - box[0]
                height_px = box[3] - box[1]

                # SHARP BORDERS - NO TRANSPARENCY for ML training
                html_content += f"""
                <div class="ui-element ui-element-{element_id}" 
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
                            text-shadow: 1px 1px 2px rgba(0,0,0,0.9);">
                    {element_id}
                </div>
                """
    
    html_content += f"""
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
    // Wait for DOM to be ready
    setTimeout(function() {{
        console.log('Initializing interactive elements...');
        const elementsData = {json.dumps(elements_data)};
        let selectedElementId = null;
        
        function initializeInteractivity() {{
            const container = document.getElementById('interactive-container');
            if (!container) {{
                console.log('Container not found, retrying...');
                setTimeout(initializeInteractivity, 100);
                return;
            }}
            
            console.log('Container found, setting up interactions...');
            const tooltip = document.getElementById('tooltip');
            
            // Add event listeners to all elements
            elementsData.forEach(function(elementData) {{
                const selector = '.ui-element-' + elementData.id;
                const elements = container.querySelectorAll(selector);
                console.log('Found ' + elements.length + ' elements with selector: ' + selector);
                
                elements.forEach(function(element) {{
                    // Remove any existing listeners
                    const newElement = element.cloneNode(true);
                    element.parentNode.replaceChild(newElement, element);
                    
                    // Hover events
                    newElement.addEventListener('mouseenter', function(e) {{
                        console.log('Mouse enter on element ' + elementData.id);
                        if (tooltip) {{
                            tooltip.innerHTML = '<strong>Элемент ' + elementData.id + ':</strong><br>' + elementData.description;
                            tooltip.style.display = 'block';
                            
                            const rect = e.target.getBoundingClientRect();
                            const containerRect = container.getBoundingClientRect();
                            
                            tooltip.style.left = (rect.left - containerRect.left + rect.width + 10) + 'px';
                            tooltip.style.top = (rect.top - containerRect.top) + 'px';
                        }}
                        
                        if (elementData.id !== selectedElementId) {{
                            e.target.style.backgroundColor = 'rgba(0, 255, 0, 0.15)';
                            e.target.style.borderWidth = '4px';
                            e.target.style.borderColor = '#00ff00';
                            e.target.style.boxShadow = '0 0 10px rgba(0, 255, 0, 0.5)';
                        }}
                    }});
                    
                    newElement.addEventListener('mouseleave', function(e) {{
                        console.log('Mouse leave on element ' + elementData.id);
                        if (tooltip) {{
                            tooltip.style.display = 'none';
                        }}
                        
                        if (elementData.id !== selectedElementId) {{
                            e.target.style.backgroundColor = 'rgba(0, 255, 0, 0.05)';
                            e.target.style.borderWidth = '3px';
                            e.target.style.borderColor = '#00ff00';
                            e.target.style.boxShadow = 'none';
                        }}
                    }});
                    
                    // Click event
                    newElement.addEventListener('click', function(e) {{
                        console.log('Click on element ' + elementData.id);
                        e.preventDefault();
                        e.stopPropagation();
                        
                        // Clear all selections
                        container.querySelectorAll('.ui-element').forEach(function(el) {{
                            el.style.backgroundColor = 'rgba(0, 255, 0, 0.05)';
                            el.style.borderWidth = '3px';
                            el.style.borderColor = '#00ff00';
                            el.style.boxShadow = 'none';
                        }});
                        
                        if (selectedElementId === elementData.id) {{
                            // Deselect
                            console.log('Deselecting element ' + elementData.id);
                            selectedElementId = null;
                            
                            // Update Gradio component if it exists
                            const infoOutput = document.querySelector('#element_info_output textarea');
                            if (infoOutput) {{
                                infoOutput.value = 'Нажмите на элемент, чтобы увидеть его описание.';
                                infoOutput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            }}
                        }} else {{
                            // Select
                            console.log('Selecting element ' + elementData.id);
                            selectedElementId = elementData.id;
                            e.target.style.backgroundColor = 'rgba(255, 0, 0, 0.1)';
                            e.target.style.borderWidth = '4px';
                            e.target.style.borderColor = '#ff0000';
                            e.target.style.boxShadow = '0 0 15px rgba(255, 0, 0, 0.6)';
                            
                            // Update Gradio component if it exists
                            const infoOutput = document.querySelector('#element_info_output textarea');
                            if (infoOutput) {{
                                infoOutput.value = 'Элемент ' + elementData.id + ': ' + elementData.description;
                                infoOutput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            }}
                        }}
                    }});
                }});
            }});
            
            console.log('Initialization complete!');
        }}
        
        // Start initialization
        initializeInteractivity();
    }}, 500);  // Delay to ensure Gradio has rendered
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
        print("⚠️ Получено пустое изображение")
        return None, gr.update(interactive=False), "Загрузите изображение для анализа."
    
    try:
        # Проверяем, что изображение имеет правильный формат
        if hasattr(image, 'size'):
            print(f"🖼️ Изображение загружено: {image.size} (используется в оригинальном размере)...")
            print("✅ Изображение готово к анализу (оригинальный размер).")
            # Return the original image and enable the button
            return image, gr.update(interactive=True), "Изображение готово к анализу."
        else:
            print("⚠️ Загруженное изображение не имеет атрибута size")
            return None, gr.update(interactive=False), "Ошибка формата изображения. Пожалуйста, попробуйте другой файл."
    except Exception as e:
        print(f"❌ Ошибка при обработке загруженного изображения: {e}")
        return None, gr.update(interactive=False), f"Ошибка при обработке изображения: {e}"


def analyze_ui_elements(processed_image):
    """
    Analyzes the UI elements in the given image using the Gemini model.
    """
    if processed_image is None:
        print("❌ ERROR: processed_image is None")
        return None, {"elements": []}, "Произошла ошибка: изображение для анализа отсутствует.", "Нажмите на элемент, чтобы увидеть его описание."
    
    try:
        # Проверяем, что у изображения есть размер
        if not hasattr(processed_image, 'size'):
            print("❌ ERROR: processed_image не имеет атрибута size")
            return processed_image, {"elements": []}, "Ошибка: некорректный формат изображения.", "Нажмите на элемент, чтобы увидеть его описание."
            
        print(f"🤖 Отправка изображения в Vertex AI: {processed_image.size}...")

        # Configure the generative model
        api_key = get_api_key(PROJECT_ID, SECRET_ID)
        if not api_key:
            print("❌ ERROR: Не удалось получить API ключ")
            return processed_image, {"elements": []}, "Ошибка: не удалось получить API ключ для Vertex AI.", "Нажмите на элемент, чтобы увидеть его описание."
            
        genai.configure(api_key=api_key)

        # Create the model instance
        model = genai.GenerativeModel(MODEL_NAME)

        # Send the processed image to the model
        response = model.generate_content([SYSTEM_PROMPT, processed_image])
        
        # Clean up the response
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
        
        try:
            json_response = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка при разборе JSON ответа: {e}")
            print(f"Полученный ответ: {cleaned_response[:200]}...")
            return processed_image, {"elements": []}, f"Ошибка при разборе ответа от Vertex AI: {e}", "Нажмите на элемент, чтобы увидеть его описание."
        
        if not isinstance(json_response, dict) or "elements" not in json_response:
            print(f"❌ Неверный формат ответа от модели: {json_response}")
            return processed_image, {"elements": []}, "Ошибка: неверный формат ответа от модели.", "Нажмите на элемент, чтобы увидеть его описание."
        
        print(f"✅ Анализ успешно завершен: найдено {len(json_response.get('elements', []))} элементов.")
        
        # Return the *processed* image and the JSON data for visualization
        return processed_image, json_response, f"Найдено {len(json_response.get('elements', []))} элементов.", "Нажмите на элемент, чтобы увидеть его описание."

    except Exception as e:
        print(f"❌ Произошла ошибка во время анализа: {e}")
        import traceback
        traceback.print_exc()
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
                    lines=3,
                    elem_id="element_info_output"
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
    demo.launch(
        server_name="127.0.0.1", 
        server_port=7863, 
        share=True, 
        debug=True
    )

    print("\n" + "="*50)
    print("✅ Приложение запущено!")
    print("🔗 Публичная ссылка (для доступа откуда угодно): найдите в строке выше, она выглядит как https://....gradio.live")
    print(f"🏠 Локальная ссылка (для этого компьютера): http://127.0.0.1:7863")
    print("="*50 + "\n")


if __name__ == "__main__":
    main() 