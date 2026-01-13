"""
Main application entry point
Run this file to start the Flask application
"""
import os
from app import create_app

# Create app instance
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
