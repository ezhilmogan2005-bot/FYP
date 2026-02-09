"""
Intelligent Pesticide Sprinkler System - Flask Backend API
Handles image analysis, disease detection, and spray control
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
import io
import base64
import os
from datetime import datetime

from model import get_model

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global state
latest_sensor_data = {
    'temperature': 25.0,
    'humidity': 60.0,
    'soil_moisture': 55.0,
    'timestamp': datetime.now().isoformat()
}

spray_status = {
    'is_spraying': False,
    'last_command': None,
    'last_spray_time': None
}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """API root endpoint."""
    return jsonify({
        'message': 'Intelligent Pesticide Sprinkler System API',
        'version': '1.0.0',
        'endpoints': [
            'POST /analyze - Analyze leaf image',
            'GET /sensors - Get sensor readings',
            'POST /sensors/update - Update sensor data from IoT',
            'POST /control/spray - Control spray pump'
        ]
    })


@app.route('/analyze', methods=['POST'])
def analyze_image():
    """
    Analyze leaf image for disease detection.
    
    Accepts:
        - image: Image file (multipart/form-data)
        - OR image_base64: Base64 encoded image
        - soil_moisture: Current soil moisture percentage (optional)
    
    Returns:
        - disease_name: Detected disease name
        - infection_level: Percentage of leaf affected
        - confidence: Model confidence score
        - recommendation: Treatment recommendation
        - spray_allowed: Whether spraying is safe
        - alert_message: Notification message
    """
    try:
        # Get image from request
        image = None
        soil_moisture = None
        
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            if file and allowed_file(file.filename):
                image = Image.open(file.stream)
        elif 'image_base64' in request.form:
            image_data = base64.b64decode(request.form['image_base64'])
            image = Image.open(io.BytesIO(image_data))
        
        if image is None:
            return jsonify({'error': 'No image provided'}), 400
        
        # Get soil moisture if provided
        if 'soil_moisture' in request.form:
            soil_moisture = float(request.form['soil_moisture'])
        else:
            soil_moisture = latest_sensor_data.get('soil_moisture', 50)
        
        # Save image for logging
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"leaf_{timestamp}.jpg"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        
        # Get model and run inference
        model = get_model()
        
        # Run prediction
        mask, disease_key, confidence = model.predict(image)
        infection_level = model.calculate_infection_level(mask)
        
        # Get recommendation
        recommendation = model.get_recommendation(disease_key, infection_level)
        
        # Safety check: Only allow spraying if soil moisture is in safe range (40-70%)
        moisture_safe = 40 <= soil_moisture <= 70
        
        # Generate alert message
        if infection_level > 15:
            alert_message = (
                f"🚨 DISEASE ALERT: {recommendation['disease_name']}\n"
                f"Infection Level: {infection_level}% ({recommendation['severity']})\n"
                f"Recommended Pesticide: {recommendation['pesticide']}\n"
                f"Dosage: {recommendation['dosage']}\n"
                f"Spray Duration: {recommendation['spray_duration']} seconds"
            )
            if not moisture_safe:
                alert_message += "\n⚠️ WARNING: Soil moisture outside safe range (40-70%). Spraying NOT recommended."
            else:
                alert_message += "\n✅ Spraying recommended."
        else:
            alert_message = f"✅ Plant appears healthy. Infection level: {infection_level}%"
        
        response = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'disease_detected': disease_key != 'healthy',
            'disease_name': recommendation['disease_name'],
            'disease_description': recommendation['description'],
            'infection_level': infection_level,
            'severity': recommendation['severity'],
            'confidence': round(confidence * 100, 2),
            'pesticide': recommendation['pesticide'],
            'dosage': recommendation['dosage'],
            'spray_recommended': recommendation['spray_recommended'] and moisture_safe,
            'spray_duration': recommendation['spray_duration'],
            'spray_allowed': moisture_safe,
            'soil_moisture': soil_moisture,
            'moisture_safe': moisture_safe,
            'alert_message': alert_message,
            'image_path': image_path
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/sensors', methods=['GET'])
def get_sensors():
    """Get latest sensor readings."""
    return jsonify({
        'success': True,
        'data': latest_sensor_data
    })


@app.route('/sensors/update', methods=['POST'])
def update_sensors():
    """
    Update sensor data from IoT device.
    
    Accepts JSON:
        - temperature: float
        - humidity: float
        - soil_moisture: float
    """
    global latest_sensor_data
    
    try:
        data = request.get_json()
        
        latest_sensor_data.update({
            'temperature': data.get('temperature', latest_sensor_data['temperature']),
            'humidity': data.get('humidity', latest_sensor_data['humidity']),
            'soil_moisture': data.get('soil_moisture', latest_sensor_data['soil_moisture']),
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'message': 'Sensor data updated',
            'data': latest_sensor_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/control/spray', methods=['POST'])
def control_spray():
    """
    Control the pesticide spray pump.
    
    Accepts JSON:
        - command: 'START' or 'STOP'
        - duration: spray duration in seconds (optional)
        - soil_moisture: current soil moisture reading (optional)
    
    Returns:
        - command: Command sent to device
        - spray_allowed: Whether spray is permitted
        - reason: Reason if spray not allowed
    """
    global spray_status
    
    try:
        data = request.get_json()
        command = data.get('command', '').upper()
        duration = data.get('duration', 5)
        soil_moisture = data.get('soil_moisture', latest_sensor_data.get('soil_moisture', 50))
        
        if command not in ['START', 'STOP']:
            return jsonify({'error': 'Invalid command. Use START or STOP'}), 400
        
        # Check soil moisture safety
        moisture_safe = 40 <= soil_moisture <= 70
        
        if command == 'START':
            if not moisture_safe:
                spray_status['last_command'] = 'REJECTED'
                return jsonify({
                    'success': False,
                    'command': 'REJECTED',
                    'spray_allowed': False,
                    'reason': f'Soil moisture {soil_moisture}% outside safe range (40-70%). Cannot spray.',
                    'soil_moisture': soil_moisture,
                    'moisture_safe': False
                }), 403
            
            spray_status.update({
                'is_spraying': True,
                'last_command': 'START',
                'last_spray_time': datetime.now().isoformat(),
                'spray_duration': duration
            })
            
            return jsonify({
                'success': True,
                'command': 'START_SPRAY',
                'spray_allowed': True,
                'duration': duration,
                'soil_moisture': soil_moisture,
                'message': f'Spray started for {duration} seconds'
            })
        
        else:  # STOP command
            spray_status.update({
                'is_spraying': False,
                'last_command': 'STOP'
            })
            
            return jsonify({
                'success': True,
                'command': 'STOP_SPRAY',
                'spray_allowed': True,
                'message': 'Spray stopped'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/control/status', methods=['GET'])
def get_spray_status():
    """Get current spray system status."""
    return jsonify({
        'success': True,
        'spray_status': spray_status
    })


if __name__ == '__main__':
    print("🌱 Intelligent Pesticide Sprinkler System - Backend API")
    print("=" * 60)
    print("Initializing U-Net Model...")
    
    # Initialize model on startup
    model = get_model()
    
    print("✅ Model loaded successfully")
    print(f"🚀 Server starting on http://0.0.0.0:5000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
