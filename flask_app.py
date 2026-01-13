"""
Flask app entry point for PythonAnywhere
This file is used by PythonAnywhere's WSGI configuration
"""
import os
import sys

# Add the project directory to the Python path
project_home = '/home/amsfiles/ipi'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the Flask app with production configuration
from app import create_app

# Create the application instance with production config
app = create_app('production')

if __name__ == '__main__':
    app.run()
