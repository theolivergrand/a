# -*- coding: utf-8 -*-
"""
Configuration example file for AI UI/UX Analyzer
Copy this file to config.py and fill in your actual values
"""

# Google Cloud Project Configuration
PROJECT_ID = "your-gcp-project-id"
SECRET_ID = "your-secret-manager-secret-id"

# Alternative: Direct API Key (not recommended for production)
# Uncomment and use this if you want to use API key directly
# GEMINI_API_KEY = "your-gemini-api-key-here"

# Application Configuration
APP_PORT = 7860
APP_HOST = "0.0.0.0"
DEBUG = False

# Optional: Custom model settings
MODEL_NAME = "gemini-1.5-flash"
MAX_TOKENS = 1000
TEMPERATURE = 0.7

# UI Configuration
APP_TITLE = "AI UI/UX Analyzer"
APP_DESCRIPTION = "Загрузите скриншот пользовательского интерфейса, и ИИ определит и пронумерует интерактивные элементы." 