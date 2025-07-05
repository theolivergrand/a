import json
from app import create_interactive_html
from PIL import Image

# Создаем тестовое изображение
test_image = Image.new('RGB', (100, 100), color='white')

# Создаем тестовые данные
test_json = {
    "elements": [
        {
            "id": 1,
            "box": [10, 10, 50, 50],
            "description": "Test button with 'quotes' and \"double quotes\""
        }
    ]
}

# Генерируем HTML
html = create_interactive_html(test_image, test_json)

# Сохраняем в файл для проверки
with open("test_output.html", "w", encoding="utf-8") as f:
    f.write("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Test Interactive HTML</title>
</head>
<body>
""")
    f.write(html)
    f.write("""
</body>
</html>
""")

print("HTML сохранен в test_output.html")
print("\nПервые 500 символов сгенерированного HTML:")
print(html[:500]) 