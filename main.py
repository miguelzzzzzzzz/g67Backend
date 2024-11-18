import base64
import os
from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import subprocess
import math
import mediapipe as mp
import cv2
import numpy as np

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for testing


UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/model')
def get_model():
    return send_file('Adjusted_Mannequin.obj', as_attachment=False)

@app.route('/generate', methods=['POST'])
def generate_model():
    try:
        # Command to execute Blender
        blender_command = [
            "blender",
            "C:\\Users\\migzuu\Downloads\\testBlend-20241118T080845Z-001\\testBlend\\test.blend",
            "--background",
            "--python",
            "randomize_bones.py"
        ]
        subprocess.run(blender_command, check=True)
        return jsonify({"message": "Model generation successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        data = request.get_json()
        if 'file' not in data or 'height' not in data:
            return jsonify({'error': 'Missing file or height in request'}), 400

        base64_image = data['file']
        real_height = float(data['height'])  # User-provided height
        print("WOWWWWWWWWWWWWWWWWWWWWWWWWWW",real_height)
        filename = data.get('filename', 'uploaded_image.jpg')

        image_data = base64.b64decode(base64_image)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img_path = "uploads/uploaded_image.jpg"
        with open(filepath, 'wb') as f:
            f.write(image_data)
        get_measurements_from_user('uploads/462550064_1112784256864921_4481066422507567856_n.jpg', real_height)
        return jsonify({'message': 'File uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
def calculate_angle(p1, p2):
    """Calculate the angle between two points with respect to the horizontal."""
    delta_y = p2[1] - p1[1]
    delta_x = p2[0] - p1[0]
    return math.degrees(math.atan2(delta_y, delta_x))
def process_image_and_scale(image_path, real_height):
    """Process the image to extract pose keypoints using MediaPipe,
    and scale the keypoints based on the provided real height.
    """

    # Initialize MediaPipe Pose
    mp_pose = mp.solutions.pose.Pose()

    # Load the image
    img = cv2.imread(image_path)
    print("Read")
    # Convert the image to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Process the image and detect keypoints
    print("IPAPASOK")
    results = mp_pose.process(img_rgb)
    print("NAPASOK")
    if results.pose_landmarks is None:
        print("No pose landmarks detected.")
        return None

    # Extract keypoints from results
    keypoints = {}
    for idx, landmark in enumerate(results.pose_landmarks.landmark):
        keypoints[idx] = (landmark.x, landmark.y)  # Store normalized (x, y) values

    # Calculate the height (vertical distance between the ankle and the top of the head)
    ankle = keypoints[27]  # Left Ankle (for example)
    head = keypoints[0]  # Nose (head top approximation)

    # Calculate the height in the image (distance between ankle and head)
    image_height = calculate_distance(head, ankle)

    # Now scale the keypoints using the real height provided by the user
    if image_height == 0:  # Avoid division by zero
        print("Error: Invalid height in keypoints.")
        return None

    ratio = real_height / image_height  # Calculate scale ratio

    # Scale the keypoints based on the ratio
    scaled_keypoints = {}
    for i in keypoints:
        # Scale the (x, y) positions and store them in scaled_keypoints
        scaled_keypoints[i] = (ratio * keypoints[i][0], ratio * keypoints[i][1])

    # Calculate measurements
    measurements = calculate_body_measurements(scaled_keypoints)

    return measurements
def calculate_body_measurements(keypoints):
    """Calculate body measurements based on pose keypoints."""

    # Chest Circumference (approximation using shoulder width and rib cage expansion)
    left_shoulder = keypoints[11]
    right_shoulder = keypoints[12]
    shoulder_width = calculate_distance(left_shoulder, right_shoulder)
    chest_circumference = shoulder_width * 2  # Approximate

    # Waist Circumference (approximation using hips)
    left_hip = keypoints[23]
    right_hip = keypoints[24]
    waist_circumference = calculate_distance(left_hip, right_hip) * 2  # Approximate

    # Hip Circumference (around the widest point of hips)
    hip_circumference = waist_circumference  # Similar to waist approximation in pose

    # Inseam Length (distance from the hip to the ankle)
    left_ankle = keypoints[27]
    right_ankle = keypoints[28]
    left_leg_length = calculate_distance(left_hip, left_ankle)
    right_leg_length = calculate_distance(right_hip, right_ankle)
    inseam_length = (left_leg_length + right_leg_length) / 2

    # Arm Length (shoulder to wrist)
    left_wrist = keypoints[15]
    right_wrist = keypoints[16]
    left_arm_length = calculate_distance(left_shoulder, left_wrist)
    right_arm_length = calculate_distance(right_shoulder, right_wrist)

    # Shoulder Length (shoulder width)
    shoulder_length = calculate_distance(left_shoulder, right_shoulder)

    # Thigh Circumference (approximation using distance between hips and knees)
    left_knee = keypoints[25]  # Left Knee
    right_knee = keypoints[26]  # Right Knee
    left_thigh_circumference = calculate_distance(left_hip, left_knee) * 2  # Approximate
    right_thigh_circumference = calculate_distance(right_hip, right_knee) * 2  # Approximate

    # Neck Circumference (approximation based on neck length and head width)
    left_shoulder = keypoints[11]
    right_shoulder = keypoints[12]
    neck_length = calculate_distance(left_shoulder, right_shoulder) * 0.25  # Approximate
    neck_circumference = neck_length * 3.14  # Using the neck length to estimate circumference

    measurements = {
        "Chest Circumference": chest_circumference,
        "Waist Circumference": waist_circumference,
        "Hip Circumference": hip_circumference,
        "Inseam Length": inseam_length,
        "Left Arm Length": left_arm_length,
        "Right Arm Length": right_arm_length,
        "Shoulder Length": shoulder_length,
        "Left Thigh Circumference": left_thigh_circumference,
        "Right Thigh Circumference": right_thigh_circumference,
        "Neck Circumference": neck_circumference
    }

    return measurements
def get_measurements_from_user(image_path, real_height):
    """Accept user input for image and height, and generate measurements."""


    # Process the image and generate measurements
    measurements = process_image_and_scale(image_path, real_height)

    # Print the measurements
    if measurements:
        print("\nCalculated Body Measurements:")
        for name, value in measurements.items():
            print(f"{name}: {value:.2f} meters")
    else:
        print("Error processing the image or calculating the measurements.")


if __name__ == '__main__':
    get_measurements_from_user(
        'uploads/462550064_1112784256864921_4481066422507567856_n.jpg', 120
    )
    app.run(host='0.0.0.0', port=5000, debug=True)


