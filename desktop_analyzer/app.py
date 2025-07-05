# -*- coding: utf-8 -*-
"""
Refactored main application entry point for Desktop UI/UX Analyzer.
This file replaces the old monolithic main.py with a clean, modular architecture.
"""
import sys
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.views.main_window import MainWindow
from config.config import config_manager


def setup_logging():
    """Setup logging configuration."""
    config = config_manager.config
    
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log', encoding='utf-8')
        ]
    )
    
    # Set specific loggers
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)


def create_application():
    """Create and configure the QApplication."""
    app = QApplication(sys.argv)
    
    # Set application properties
    ui_config = config_manager.get_ui_config()
    app.setApplicationName(ui_config.window_title)
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Desktop Analyzer")
    
    # Enable high DPI scaling
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    
    return app


def main():
    """Main application entry point."""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting Desktop UI/UX Analyzer v2.0")
        
        # Create application
        app = create_application()
        
        # Create and show main window
        main_window = MainWindow()
        main_window.show()
        
        # Log startup completion
        logger.info("Application started successfully")
        
        # Run application
        exit_code = app.exec()
        logger.info(f"Application exited with code: {exit_code}")
        
        return exit_code
        
    except Exception as e:
        print(f"Critical error starting application: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
