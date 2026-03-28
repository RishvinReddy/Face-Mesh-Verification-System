document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const toggleMesh = document.getElementById('toggle-mesh');
    const toggleCursor = document.getElementById('toggle-cursor');
    
    const statEmotion = document.getElementById('stat-emotion');
    const statFaceCount = document.getElementById('stat-facecount');
    const statBlinks = document.getElementById('stat-blinks');
    const fpsHud = document.getElementById('fps-hud');

    // Event Listeners for controls
    toggleMesh.addEventListener('change', (e) => {
        fetch(`/toggle_mesh/${e.target.checked}`)
            .then(res => res.json())
            .catch(err => console.error("Error toggling mesh", err));
    });

    toggleCursor.addEventListener('change', (e) => {
        if(e.target.checked) {
            alert("⚠️ WARNING: You are enabling Beta Mouse Control.\nYour mouse cursor will follow your nose. Blink to click.\nMove mouse manually to override or disable!");
        }
        fetch(`/toggle_cursor/${e.target.checked}`)
            .then(res => res.json())
            .catch(err => console.error("Error toggling cursor", err));
    });

    // Polling function for live telemetry
    function fetchTelemetry() {
        fetch('/telemetry')
            .then(res => res.json())
            .then(data => {
                // Update UI elements
                statFaceCount.textContent = data.face_count;
                statBlinks.textContent = data.blinks;
                statEmotion.textContent = data.emotion;
                fpsHud.textContent = `FPS: ${data.fps}`;

                // Dynamic coloring for emotion
                if(data.emotion === "Happy") {
                    statEmotion.style.color = "#00ff87";
                    statEmotion.style.textShadow = "0 0 10px rgba(0, 255, 135, 0.5)";
                } else if (data.emotion === "Surprised") {
                    statEmotion.style.color = "#f6d365";
                    statEmotion.style.textShadow = "0 0 10px rgba(246, 211, 101, 0.5)";
                } else {
                    statEmotion.style.color = "#fff";
                    statEmotion.style.textShadow = "none";
                }
            })
            .catch(err => console.error("Error fetching telemetry", err))
            .finally(() => {
                // Request next frame
                requestAnimationFrame(() => setTimeout(fetchTelemetry, 100)); // ~10fps poll rate
            });
    }

    // Start polling
    fetchTelemetry();
});
