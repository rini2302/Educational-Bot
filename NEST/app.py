from flask import Flask, render_template, jsonify, request
import subprocess
import os

app = Flask(__name__)  # No need to specify template_folder if it's "templates" by default

@app.route('/')
def home():
    return render_template('index.html')  # Make sure "index.html" is inside the "templates" folder

@app.route('/run_python', methods=['POST'])
def run_python():
    try:
         script_path = os.path.join(os.getcwd(), "bubba.py")
         if not os.path.exists(script_path):
            return jsonify({'error': f"Script not found: {script_path}"})

        # Run the script and capture output
         result = subprocess.run(['python', script_path], capture_output=True, text=True)

        # Debugging logs
         print("STDOUT:", result.stdout)
         print("STDERR:", result.stderr)

        # Return script output or error
         if result.returncode == 0:
            return jsonify({'output': result.stdout.strip()})
         else:
            return jsonify({'error': result.stderr.strip()})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)