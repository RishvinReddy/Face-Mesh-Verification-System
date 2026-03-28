import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time

# Optional: Disable PyAutoGUI failsafe so cursor doesn't crash if it hits corner
pyautogui.FAILSAFE = False

class FaceAnalyzer:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Telemetry
        self.prev_time = 0
        self.total_blinks = 0
        self.blink_counter = 0
        self.blink_threshold = 0.22 # EAR threshold
        self.blink_frames = 2 # Frames below threshold to count as blink
        
        # State
        self.current_emotion = "Neutral"
        self.cursor_enabled = False
        self.screen_w, self.screen_h = pyautogui.size()
        
    def _calculate_ear(self, landmarks, indices):
        # Calculate Eye Aspect Ratio
        # indices usually: [p0, p1, p2, p3, p4, p5] (leftmost, top-left, top-right, rightmost, bottom-right, bottom-left)
        p0 = np.array([landmarks[indices[0]].x, landmarks[indices[0]].y])
        p1 = np.array([landmarks[indices[1]].x, landmarks[indices[1]].y])
        p2 = np.array([landmarks[indices[2]].x, landmarks[indices[2]].y])
        p3 = np.array([landmarks[indices[3]].x, landmarks[indices[3]].y])
        p4 = np.array([landmarks[indices[4]].x, landmarks[indices[4]].y])
        p5 = np.array([landmarks[indices[5]].x, landmarks[indices[5]].y])

        # vertical distances
        v1 = np.linalg.norm(p1 - p5)
        v2 = np.linalg.norm(p2 - p4)
        # horizontal distance
        h = np.linalg.norm(p0 - p3)
        
        ear = (v1 + v2) / (2.0 * h)
        return ear

    def _estimate_emotion(self, landmarks):
        # Mouth aspect ratio
        top_lip = np.array([landmarks[13].x, landmarks[13].y])
        bottom_lip = np.array([landmarks[14].x, landmarks[14].y])
        left_mouth = np.array([landmarks[78].x, landmarks[78].y])
        right_mouth = np.array([landmarks[308].x, landmarks[308].y])
        
        mouth_height = np.linalg.norm(top_lip - bottom_lip)
        mouth_width = np.linalg.norm(left_mouth - right_mouth)
        
        mar = mouth_height / mouth_width if mouth_width > 0 else 0
        
        # Simple heuristic
        if mar > 0.5:
            return "Surprised"
        elif mouth_width > 0.4: # This threshold depends on face scale, simplified here
            # Let's use a dynamic approach. If the mouth edges are pulled up compared to the center
            left_mouth_y = landmarks[61].y
            right_mouth_y = landmarks[291].y
            center_lip_y = landmarks[13].y
            
            # If corners are significantly higher than the center bottom lip
            if left_mouth_y < center_lip_y and right_mouth_y < center_lip_y:
                return "Happy"
            else:
                return "Neutral"
        return "Neutral"
        
    def _control_mouse(self, nose_landmark):
        # Map nose coordinate to screen
        # Landmark coordinates are normalized [0.0, 1.0]
        # X is mirrored usually in webcam
        x = int(nose_landmark.x * self.screen_w)
        y = int(nose_landmark.y * self.screen_h)
        
        # Smooth cursor movement by limiting drastic jumps or use PyAutoGUI's tweening
        try:
            pyautogui.moveTo(x, y, duration=0.1)
        except pyautogui.FailSafeException:
            pass

    def process_frame(self, frame, draw_mesh=True, enable_cursor=False):
        self.cursor_enabled = enable_cursor
        
        # Calculate FPS
        current_time = time.time()
        fps = 1 / (current_time - self.prev_time) if self.prev_time > 0 else 0
        self.prev_time = current_time
        
        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False # Improve performance
        
        # Process image
        results = self.face_mesh.process(rgb_frame)
        
        rgb_frame.flags.writeable = True
        
        face_count = 0
        
        if results.multi_face_landmarks:
            face_count = len(results.multi_face_landmarks)
            
            for face_landmarks in results.multi_face_landmarks:
                if draw_mesh:
                    self.mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=face_landmarks,
                        connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
                    )
                
                # Extract landmarks for AI features
                landmarks = face_landmarks.landmark
                
                # 1. Blink Detection (using left and right eye indices)
                # Left eye: [33, 160, 158, 133, 153, 144]
                # Right eye: [362, 385, 387, 263, 373, 380]
                left_eye_ear = self._calculate_ear(landmarks, [33, 160, 158, 133, 153, 144])
                right_eye_ear = self._calculate_ear(landmarks, [362, 385, 387, 263, 373, 380])
                avg_ear = (left_eye_ear + right_eye_ear) / 2.0
                
                if avg_ear < self.blink_threshold:
                    self.blink_counter += 1
                else:
                    if self.blink_counter >= self.blink_frames:
                        self.total_blinks += 1
                        # If cursor is enabled, blink = click
                        if self.cursor_enabled:
                            pyautogui.click()
                    self.blink_counter = 0
                
                # 2. Emotion Detection
                self.current_emotion = self._estimate_emotion(landmarks)
                
                # 3. Control System (Nose tip is index 1 or 4)
                if self.cursor_enabled:
                    nose_tip = landmarks[4]
                    self._control_mouse(nose_tip)
                    
        return {
            'frame': frame,
            'fps': int(fps),
            'face_count': face_count,
            'blinks': self.total_blinks,
            'emotion': self.current_emotion,
            'ear': getattr(self, 'avg_ear', 0) # Just in case we want to debug
        }
