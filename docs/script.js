const videoElement = document.getElementById('input_video');
const canvasElement = document.getElementById('output_canvas');
const canvasCtx = canvasElement.getContext('2d');

const startBtn = document.getElementById('startBtn');
const terminalLogs = document.getElementById('terminal-logs');
const pointsCount = document.getElementById('points-count');
const fpsCount = document.getElementById('fps-count');
const loader = document.getElementById('loader');

let isEngineRunning = false;
let camera = null;
let lastTime = 0;
let frames = 0;

function logToTerminal(message) {
    const p = document.createElement('p');
    p.innerText = `> ${message}`;
    terminalLogs.appendChild(p);
    terminalLogs.scrollTop = terminalLogs.scrollHeight;
}

// Format time
function padZero(num) {
    return num.toString().padStart(2, '0');
}
function getTimeStamp() {
    const d = new Date();
    return `[${padZero(d.getHours())}:${padZero(d.getMinutes())}:${padZero(d.getSeconds())}:${padZero(d.getMilliseconds(), 3)}]`;
}

// MediaPipe FaceMesh Setup
const faceMesh = new FaceMesh({locateFile: (file) => {
  return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
}});

faceMesh.setOptions({
  maxNumFaces: 1,
  refineLandmarks: true,
  minDetectionConfidence: 0.5,
  minTrackingConfidence: 0.5
});

faceMesh.onResults(onResults);

function onResults(results) {
    loader.style.display = 'none';

    // Calculate FPS
    const now = performance.now();
    frames++;
    if (now - lastTime >= 1000) {
        fpsCount.innerText = frames;
        frames = 0;
        lastTime = now;
    }

    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    
    // Draw Video Frame
    canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
    
    // Draw Mesh
    if (results.multiFaceLandmarks) {
        for (const landmarks of results.multiFaceLandmarks) {
            
            // Draw tessellation map
            drawConnectors(canvasCtx, landmarks, FACEMESH_TESSELATION, {
                color: '#C0C0C070', 
                lineWidth: 1
            });
            
            // Draw Right Eye
            drawConnectors(canvasCtx, landmarks, FACEMESH_RIGHT_EYE, {color: '#00f0ff', lineWidth: 2});
            drawConnectors(canvasCtx, landmarks, FACEMESH_RIGHT_EYEBROW, {color: '#00f0ff', lineWidth: 2});
            drawConnectors(canvasCtx, landmarks, FACEMESH_RIGHT_IRIS, {color: '#00f0ff', lineWidth: 2});
            
            // Draw Left Eye
            drawConnectors(canvasCtx, landmarks, FACEMESH_LEFT_EYE, {color: '#9d00ff', lineWidth: 2});
            drawConnectors(canvasCtx, landmarks, FACEMESH_LEFT_EYEBROW, {color: '#9d00ff', lineWidth: 2});
            drawConnectors(canvasCtx, landmarks, FACEMESH_LEFT_IRIS, {color: '#9d00ff', lineWidth: 2});
            
            // Draw Face Oval & Lips
            drawConnectors(canvasCtx, landmarks, FACEMESH_FACE_OVAL, {color: '#E0E0E0', lineWidth: 2});
            drawConnectors(canvasCtx, landmarks, FACEMESH_LIPS, {color: '#E0E0E0', lineWidth: 2});
            
            pointsCount.innerText = '468';
            
            // Randomly log to terminal for effect
            if(Math.random() > 0.95) {
                const centerNode = landmarks[1]; // Nose tip
                logToTerminal(`${getTimeStamp()} VERIFY: Euclidean metrics stable. N_X: ${centerNode.x.toFixed(3)}`);
            }
        }
    } else {
        pointsCount.innerText = '0';
        if(Math.random() > 0.98) {
            logToTerminal(`${getTimeStamp()} WARN: Target lost. Scanning geometry...`);
        }
    }
    canvasCtx.restore();
}

// Start/Stop Engine Logic
startBtn.addEventListener('click', () => {
    if (!isEngineRunning) {
        logToTerminal(`${getTimeStamp()} BOOT: Initializing Neural Engine...`);
        logToTerminal(`${getTimeStamp()} REQUESTING CAM ACCESS...`);
        
        if (!camera) {
            camera = new Camera(videoElement, {
                onFrame: async () => {
                    await faceMesh.send({image: videoElement});
                },
                width: 640,
                height: 480
            });
        }
        
        camera.start().then(() => {
            isEngineRunning = true;
            startBtn.innerHTML = '<i class="fa-solid fa-power-off"></i> Stop Engine';
            startBtn.style.background = '#ff0033';
            startBtn.style.boxShadow = '0 0 15px rgba(255, 0, 51, 0.5)';
            document.querySelector('.dot').classList.add('live');
            logToTerminal(`${getTimeStamp()} SYSTEM ONLINE: Face Mesh mapped to /dev/video0`);
        }).catch(err => {
            logToTerminal(`${getTimeStamp()} ERROR: Hardware failure or permission denied.`);
            console.error(err);
        });
    } else {
        if(camera) {
            camera.stop();
        }
        isEngineRunning = false;
        startBtn.innerHTML = '<i class="fa-solid fa-power-off"></i> Start Engine';
        startBtn.style.background = 'var(--accent-neon)';
        startBtn.style.boxShadow = '0 0 15px rgba(0, 240, 255, 0.5)';
        document.querySelector('.dot').classList.remove('live');
        
        // Clear canvas
        canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
        pointsCount.innerText = '0';
        fpsCount.innerText = '0';
        loader.style.display = 'block';
        logToTerminal(`${getTimeStamp()} SHUTDOWN: Neural Engine offline.`);
    }
});
