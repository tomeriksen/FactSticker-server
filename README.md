### 1. **Create a Project Directory:**
   - Start by creating a directory for your Flask project and navigate into it:
     ```bash
     mkdir FactSticker_Server
     cd FactSticker_Server
     ```

### 2. **Set Up a Virtual Environment:**
   - Create a virtual environment within your project directory to isolate your project's dependencies:
     ```bash
     python3 -m venv venv
     ```
   - Activate the virtual environment:
     ```bash
     source venv/bin/activate  # On macOS/Linux
     venv\Scripts\activate  # On Windows
     ```

### 3. **Install Flask and python-dotenv:**
   - With your virtual environment activated, install Flask and `python-dotenv`:
     ```bash
     pip install Flask openai python-dotenv
     ```

### 4. **Create a .env File for Environment Variables:**
   - In your project root, create a `.env` file to store sensitive information like API keys:
     ```
     SECRET_KEY=your_secret_key
     DATABASE_URL=your_database_url
     ```
   - Make sure to add `.env` to your `.gitignore` file to prevent it from being tracked by version control.

### 5. **Load Environment Variables in Your Flask App:**
   - In your main Flask application file (e.g., `app.py`), use `python-dotenv` to load environment variables:
     ```python
     from flask import Flask, render_template, request, jsonify
     from dotenv import load_dotenv
     import openai

     load_dotenv()  # This loads the variables from .env

     app = Flask(__name__)
     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

     @app.route('/')
     def home():
         return "Hello, Flask!"

     if __name__ == "__main__":
         app.run(debug=True)
     ```

### 6. **Run the Flask Application:**
   - Run your Flask app with the command:
     ```bash
     python app.py
     ```
   - Your Flask application should now be running on `http://localhost:5000`.

### 7. **Deactivate the Virtual Environment:**
   - When you're done working, deactivate the virtual environment:
     ```bash
     deactivate
     ```

### 8. **Managing Dependencies:**
   - To manage your project dependencies effectively, create a `requirements.txt` file:
     ```bash
     pip freeze > requirements.txt
     ```
   - This file should be included in your version control so that others can install the exact same dependencies with `pip install -r requirements.txt`.

This setup ensures that your Flask application can use environment variables securely and efficiently, keeping sensitive information out of your source code and version control, while also maintaining a clean and isolated development environment with `venv`.
