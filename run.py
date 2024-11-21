import sys
import os

# Add the root of the project to sys.path to ensure Python can find the 'app' module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

# Import the create_app function from the app package
from app import create_app  # Ensure the 'create_app' module is imported correctly

# Create an instance of the Flask application
app = create_app()

# Run the Flask server
if __name__ == "__main__":
    # Start the server in debug mode for development (optional, turn off for production)
    app.run(debug=True, host="0.0.0.0", port=5000)
