from flask import Flask, jsonify, send_file
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for testing

@app.route('/model')
def get_model():
    return send_file('Adjusted_Mannequin.obj', as_attachment=False)

@app.route('/generate', methods=['POST'])
def generate_model():
    try:
        # Command to execute Blender
        blender_command = [
            "blender",
            "C:\\Users\\migzuu\\Downloads\\Adjustable+Mannequin+v1.2\\Adjustable Mannequin v1.2.blend",
            "--background",
            "--python",
            "randomize_bones.py"
        ]
        subprocess.run(blender_command, check=True)
        return jsonify({"message": "Model generation successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
