from flask import Flask, render_template, Response, jsonify
import cv2
from engine import FaceAnalyzer

app = Flask(__name__)
analyzer = FaceAnalyzer()
camera = cv2.VideoCapture(0)

# Global states
draw_mesh = True
enable_cursor = False
latest_telemetry = {
    'fps': 0,
    'face_count': 0,
    'blinks': 0,
    'emotion': "Neutral"
}

def generate_frames():
    global latest_telemetry
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Process frame
            results = analyzer.process_frame(frame, draw_mesh=draw_mesh, enable_cursor=enable_cursor)
            
            latest_telemetry['fps'] = results['fps']
            latest_telemetry['face_count'] = results['face_count']
            latest_telemetry['blinks'] = results['blinks']
            latest_telemetry['emotion'] = results['emotion']
            
            processed_frame = results['frame']
            
            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/telemetry')
def telemetry():
    return jsonify(latest_telemetry)

@app.route('/toggle_mesh/<state>')
def toggle_mesh(state):
    global draw_mesh
    draw_mesh = state.lower() == 'true'
    return jsonify(success=True)

@app.route('/toggle_cursor/<state>')
def toggle_cursor(state):
    global enable_cursor
    enable_cursor = state.lower() == 'true'
    return jsonify(success=True)

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
