# AI UI/UX Analyzer - Спецификация проекта

## 🎯 Описание проекта
AI UI/UX Analyzer - это Gradio-приложение для анализа пользовательских интерфейсов с помощью искусственного интеллекта. Приложение использует Google Vertex AI (Gemini) для автоматического распознавания и анализа интерактивных элементов на скриншотах UI.

## 📋 Основной функционал

### 1. Загрузка и обработка изображений
- Загрузка скриншотов через веб-интерфейс ✅
- Использование оригинального размера изображения ✅ **ИЗМЕНЕНО v1.2**
- Поддержка PNG, JPG, JPEG форматов ✅
- ❌ **УДАЛЕНО**: Функция `resize_and_crop()` убрана по запросу пользователя

### 2. AI-анализ элементов интерфейса
- Определение интерактивных элементов (кнопки, поля ввода, навигация) ✅
- Получение координат bounding box для каждого элемента ✅
- Генерация описаний функций элементов ✅
- Интеграция с Google Vertex AI (Gemini) ✅

### 3. Интерактивная визуализация
- Наложение пронумерованных областей на изображение ✅
- Точные, НЕ размытые рамки ✅ **ИСПРАВЛЕНО**
- Hover-эффекты с описаниями элементов ✅
- Отображение выбранного элемента в нижнем поле ✅ **ИСПРАВЛЕНО**
- Четкие границы 3px для ML-обучения ✅

### 4. Форма обратной связи
- Поле для комментариев пользователя ✅ **ДОБАВЛЕНО**
- Возможность корректировки анализа ✅ **ДОБАВЛЕНО**
- Сохранение фидбека в файл feedback.txt ✅ **ДОБАВЛЕНО**

## 🔧 Технические требования

### Компоненты Gradio:
1. **gr.Image** - загрузка скриншота ✅
2. **gr.HTML** - интерактивная визуализация ✅
3. **gr.Textbox** - вывод информации о выбранном элементе ✅
4. **gr.Textbox** - форма обратной связи ✅
5. **gr.Button** - кнопка "Проанализировать UI" ✅
6. **gr.Button** - кнопка "Отправить отзыв" ✅

### Обработка изображений:
- ❌ **УДАЛЕНО**: Масштабирование убрано по запросу пользователя
- ❌ **УДАЛЕНО**: Целевое разрешение 1024x1024
- ❌ **УДАЛЕНО**: Функция `resize_and_crop()`
- ✅ **НОВОЕ**: Изображения используются в оригинальном размере

### Визуализация:
- Четкие, не размытые границы областей ✅ **ИСПРАВЛЕНО**
- Цветные рамки с номерами элементов ✅
- Точное позиционирование для ML-обучения ✅
- Граница 3px зеленая, при выборе 4px красная ✅

## ✅ Решенные проблемы (v1.1):

### 1. Tooltip теперь работает ✅
- Клик на элемент показывает описание в нижнем поле ✅
- JavaScript обработчики событий функционируют ✅
- Добавлена функция `getSelectedElementInfo()` для Gradio ✅

### 2. ❌ **УДАЛЕНО**: Масштабирование (v1.2)
- ❌ **УДАЛЕНО**: Функция `resize_and_crop()` убрана по запросу пользователя
- ✅ **НОВОЕ**: Изображения обрабатываются в оригинальном размере
- ✅ **НОВОЕ**: Нет необходимости в обрезке или масштабировании

### 3. Четкие рамки для ML ✅
- Убрана избыточная полупрозрачность ✅
- Четкие границы 3px для точности ✅
- Эффект свечения при наведении ✅
- Красная рамка 4px для выбранного элемента ✅

### 4. Форма обратной связи ✅
- Добавлено текстовое поле для комментариев ✅
- Кнопка отправки фидбека ✅
- Сохранение отзывов в файл feedback.txt ✅
- Очистка поля после отправки ✅

## 📝 Правила разработки

### ПЕРЕД каждым обновлением:
1. Прочитать этот файл PROJECT_SPECS.md
2. Сверить планируемые изменения с требованиями
3. Убедиться, что не нарушается существующий функционал

### ПОСЛЕ каждого обновления:
1. Обновить этот файл PROJECT_SPECS.md
2. Добавить описание новых функций
3. Отметить исправленные проблемы
4. Обновить версию в истории изменений

## 🎨 Правила создания диаграмм

### ОБЯЗАТЕЛЬНО использовать Draw.io для всех диаграмм:
1. **Файл**: `workflow.drawio` - основная диаграмма архитектуры
2. **Формат**: XML-формат Draw.io для совместимости
3. **Обновление**: диаграмма ДОЛЖНА обновляться при изменении функционала
4. **Содержание**: диаграмма должна отражать текущее состояние v1.1+

### Требования к диаграммам:
- **Актуальность**: диаграмма должна соответствовать текущей версии кода
- **Полнота**: включать все основные компоненты и потоки данных
- **Читаемость**: четкие подписи, логичная структура
- **Легенда**: обозначение цветов и символов

### Типы диаграмм:
1. **Архитектурная диаграмма** - общая структура приложения
2. **Поток данных** - как данные проходят через систему
3. **Компоненты UI** - структура пользовательского интерфейса
4. **Исправления** - что было исправлено в каждой версии

## 🔧 Технические правила

### Инструменты разработки:
- **Draw.io** - для создания и редактирования диаграмм ✅ **ОБЯЗАТЕЛЬНО**
- **Gradio** - для создания веб-интерфейса ✅
- **Google Vertex AI** - для анализа изображений ✅
- **PIL (Pillow)** - для обработки изображений ✅

### Стандарты кодирования:
- **Python** - PEP 8 стандарт
- **Комментарии** - на русском языке для пользовательских функций
- **Docstrings** - на английском для технических функций
- **Переменные** - понятные имена на английском

### Файловая структура:
```
vertex_ai_project/
├── app.py                 # Основное приложение
├── config.py              # Конфигурация (не в git)
├── config_example.py      # Пример конфигурации
├── requirements.txt       # Зависимости Python
├── preview.html          # Страница предпросмотра
├── workflow.drawio       # Диаграмма архитектуры ✅
├── PROJECT_SPECS.md      # Спецификация проекта ✅
└── feedback.txt          # Отзывы пользователей
```

## 🔄 История изменений

### v1.0 (предыдущая версия)
- Базовый функционал анализа UI
- Интеграция с Vertex AI/Gemini
- Проблемы: tooltip, масштабирование, рамки, обратная связь

### v1.1 (текущая версия) ✅
- ✅ **ИСПРАВЛЕНО**: Tooltip и JavaScript работают с Gradio
- ✅ **ИСПРАВЛЕНО**: Масштабирование без белых полей (center crop)
- ✅ **ИСПРАВЛЕНО**: Четкие рамки 3px для ML-обучения
- ✅ **ДОБАВЛЕНО**: Форма обратной связи с сохранением в файл
- ✅ **УЛУЧШЕНО**: Визуальные эффекты (свечение, четкие границы)
- ✅ **ДОБАВЛЕНО**: Поле "Информация о выбранном элементе"
- ✅ **СОЗДАНО**: Правила разработки с обязательным использованием Draw.io
- ✅ **СОЗДАНО**: Полная архитектурная диаграмма в workflow.drawio

### v1.2 (текущая версия) ✅
- ❌ **УДАЛЕНО**: Функция `resize_and_crop()` по запросу пользователя
- ✅ **ИЗМЕНЕНО**: Изображения используются в оригинальном размере
- ✅ **УПРОЩЕНО**: Убрано масштабирование и обрезка изображений
- ✅ **ОБНОВЛЕНО**: PROJECT_SPECS.md и workflow.drawio согласно правилам

### v1.3 (планируемая)
- Экспорт результатов в JSON/CSV
- Группировка элементов по типу
- Цветовая кодировка разных типов элементов
- Настройки качества анализа

## 📊 Архитектурная диаграмма

### workflow.drawio содержит:
1. **Полную архитектуру системы** - все компоненты и их связи ✅
2. **Поток данных** - от загрузки до отображения результатов ✅
3. **Критические исправления v1.1** - визуально показаны все улучшения ✅
4. **Технический стек** - все используемые технологии ✅
5. **Легенду** - цветовая кодировка для понимания схемы ✅

### Правила обновления диаграммы:
- **ОБЯЗАТЕЛЬНО** обновлять при изменении функционала
- **ВСЕГДА** использовать Draw.io формат
- **ВКЛЮЧАТЬ** актуальную информацию о версии
- **ПОКАЗЫВАТЬ** исправленные и добавленные компоненты

---

**⚠️ ВАЖНО**: Этот файл и workflow.drawio ОБЯЗАТЕЛЬНО обновлять после каждого изменения функционала!

**📋 Последнее обновление**: v1.2 - Убрана функция resize_and_crop() по запросу пользователя
**📅 Дата**: Текущая версия  
**✅ Статус**: Изображения используются в оригинальном размере, архитектура обновлена

## 🎨 UI/UX Требования

### Интерфейс Gradio:
- Заголовок: "AI UI/UX Analyzer" ✅
- Описание: "Загрузите скриншот пользовательского интерфейса" ✅
- Кнопка: "🔍 Проанализировать UI" ✅
- Секция: "📤 Отправить отзыв" ✅

### Макет:
```
[Загрузка изображения]           [Интерактивная визуализация]
[Кнопка анализа]                 [JSON данные (скрыто)]
[Статус]                         [Обработанное изображение (скрыто)]

[Информация о выбранном элементе]
[Форма обратной связи]
[Статус отзыва]
```

### Стили:
- Современный Gradio Soft Theme ✅
- Четкие контрасты ✅
- Интуитивная навигация ✅
- Адаптивная верстка ✅

## 🔧 Настройки и конфигурация

### Файлы конфигурации:
- `config.py` - настройки API, модели, проекта ✅
- `requirements.txt` - зависимости Python ✅
- `preview.html` - страница предпросмотра ✅
- `feedback.txt` - файл для сохранения отзывов ✅

### Переменные окружения:
- PROJECT_ID - ID проекта Google Cloud ✅
- SECRET_ID - ID секрета с API ключом ✅
- MODEL_NAME - название модели Gemini ✅

## 📊 Метрики качества

### Точность анализа:
- Процент правильно определенных элементов
- Точность координат bounding box
- Качество описаний элементов
- Фидбек пользователей (теперь собирается) ✅

### Производительность:
- Время обработки изображения
- Скорость генерации результатов
- Отзывчивость интерфейса
- Качество визуализации (четкие рамки) ✅

## 🎯 Цели проекта

### Основные:
1. Автоматизация анализа UI/UX ✅
2. Помощь дизайнерам в аудите интерфейсов ✅
3. Создание датасетов для обучения ML-моделей ✅

### Дополнительные:
1. Интеграция с дизайн-системами
2. Экспорт результатов в различные форматы
3. Пакетная обработка изображений

## 🚀 Новые возможности v1.1

### Улучшенная обработка изображений:
- **resize_and_crop()** - точное масштабирование без искажений
- Центрированная обрезка для сохранения важных областей
- Высокое качество resampling (LANCZOS)

### Четкая визуализация:
- Границы 3px для базового состояния
- Границы 4px + свечение для hover/selected
- Красная рамка для выбранного элемента
- Улучшенные tooltip с затемнением

### Система обратной связи:
- Текстовое поле для развернутых комментариев
- Автоматическое сохранение в файл
- Очистка формы после отправки
- Статус уведомления пользователя

---

**⚠️ ВАЖНО**: Этот файл ОБЯЗАТЕЛЬНО обновлять после каждого изменения функционала!

**📋 Последнее обновление**: v1.1 - Исправлены все критические проблемы
**📅 Дата**: Текущая версия
**✅ Статус**: Все основные функции работают корректно 