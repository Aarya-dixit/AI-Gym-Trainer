/**
 * AI Personal Gym Trainer - Frontend Application
 * Handles webcam, MediaPipe pose detection, and WebSocket communication
 */

class GymTrainerApp {
    constructor() {
        console.log('Initializing GymTrainerApp...');
        
        // DOM elements - Video Section
        this.video = document.getElementById('webcam');
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.startBtn = document.getElementById('startBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.exerciseSelect = document.getElementById('exerciseSelect');
        this.statusText = document.getElementById('statusText');
        this.instructionText = document.getElementById('instructionText');
        
        // DOM elements - Stats Section
        this.repCount = document.getElementById('repCount');
        this.phase = document.getElementById('phase');
        this.currentExercise = document.getElementById('currentExercise');
        this.feedback = document.getElementById('feedback');
        this.footerExercise = document.getElementById('footerExercise');
        this.footerStatus = document.getElementById('footerStatus');
        
        // State
        this.isRunning = false;
        this.camera = null;
        this.pose = null;
        this.ws = null;
        this.selectedExercise = 'squat';
        
        // WebSocket URL
        this.wsUrl = 'ws://localhost:8000/ws/live';
        
        // Exercise instructions
        this.instructions = {
            squat: `<strong>Squat:</strong>
                <ul>
                    <li>Stand with feet shoulder-width apart</li>
                    <li>Keep your back straight</li>
                    <li>Lower your hips until thighs are parallel to ground</li>
                    <li>Push through heels to return to start</li>
                </ul>`,
            boxing: `<strong>Boxing:</strong>
                <ul>
                    <li>Stand in boxing stance (one foot forward)</li>
                    <li>Keep hands up near face</li>
                    <li>Extend arm forward for punch</li>
                    <li>Retract quickly to guard position</li>
                </ul>`,
            waving: `<strong>Waving:</strong>
                <ul>
                    <li>Stand naturally with arms at sides</li>
                    <li>Raise one or both hands above shoulder</li>
                    <li>Wave hand side to side</li>
                    <li>Lower hand back down</li>
                </ul>`,
            jumping: `<strong>Jumping:</strong>
                <ul>
                    <li>Stand with feet together</li>
                    <li>Bend knees slightly</li>
                    <li>Jump up explosively</li>
                    <li>Land softly with bent knees</li>
                </ul>`
        };
        
        // Bind events
        this.startBtn.addEventListener('click', () => this.start());
        this.stopBtn.addEventListener('click', () => this.stop());
        this.resetBtn.addEventListener('click', () => this.reset());
        this.exerciseSelect.addEventListener('change', (e) => this.changeExercise(e.target.value));
        
        console.log('Event listeners bound');
        
        // Initialize MediaPipe
        this.initMediaPipe();
    }
    
    initMediaPipe() {
        console.log('Initializing MediaPipe...');
        this.pose = new Pose({
            locateFile: (file) => {
                return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
            }
        });
        
        this.pose.setOptions({
            modelComplexity: 1,
            smoothLandmarks: true,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
        });
        
        this.pose.onResults((results) => this.onPoseResults(results));
        console.log('MediaPipe initialized');
    }
    
    changeExercise(exercise) {
        console.log(`Changing exercise to: ${exercise}`);
        this.selectedExercise = exercise;
        
        // Update instructions
        this.instructionText.innerHTML = this.instructions[exercise];
        
        // Update UI
        const exerciseName = exercise.charAt(0).toUpperCase() + exercise.slice(1);
        this.currentExercise.textContent = exerciseName;
        this.footerExercise.textContent = exerciseName;
        
        // Reset counters
        this.repCount.textContent = '0';
        this.phase.textContent = 'READY';
        this.feedback.textContent = `Ready for ${exercise}! Start moving...`;
        
        // Update status
        this.updateStatus(`Exercise changed to ${exerciseName}`);
        
        // Send exercise change to backend if connected
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            console.log(`Sending exercise to backend: ${exercise}`);
            this.ws.send(JSON.stringify({ exercise: exercise }));
        }
    }
    
    async start() {
        try {
            this.updateStatus('Starting camera...');
            
            // Get webcam stream
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 1280, height: 720 }
            });
            
            this.video.srcObject = stream;
            
            // Wait for video to load
            await new Promise((resolve) => {
                this.video.onloadedmetadata = resolve;
            });
            
            // Set canvas size
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;
            
            // Connect WebSocket
            await this.connectWebSocket();
            
            // Start camera
            this.camera = new Camera(this.video, {
                onFrame: async () => {
                    await this.pose.send({ image: this.video });
                },
                width: 1280,
                height: 720
            });
            
            await this.camera.start();
            
            this.isRunning = true;
            this.startBtn.disabled = true;
            this.stopBtn.disabled = false;
            
            this.updateStatus('Running - analyzing your form');
            this.footerStatus.textContent = 'Active';
            
        } catch (error) {
            console.error('Error starting:', error);
            this.updateStatus('Error: ' + error.message);
            alert('Failed to start camera. Please check permissions.');
        }
    }
    
    stop() {
        console.log('Stopping camera...');
        if (this.camera) {
            this.camera.stop();
        }
        
        if (this.video.srcObject) {
            this.video.srcObject.getTracks().forEach(track => track.stop());
        }
        
        if (this.ws) {
            this.ws.close();
        }
        
        this.isRunning = false;
        this.startBtn.disabled = false;
        this.stopBtn.disabled = true;
        
        this.updateStatus('Stopped');
        this.footerStatus.textContent = 'Stopped';
    }
    
    async reset() {
        try {
            const response = await fetch('http://localhost:8000/reset', {
                method: 'POST'
            });
            
            if (response.ok) {
                this.repCount.textContent = '0';
                this.phase.textContent = '-';
                this.feedback.textContent = 'Count reset! Continue exercising...';
                
                this.updateStatus('Count reset');
            }
        } catch (error) {
            console.error('Error resetting:', error);
        }
    }
    
    connectWebSocket() {
        return new Promise((resolve, reject) => {
            console.log('Connecting to WebSocket...');
            this.ws = new WebSocket(this.wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                resolve();
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                reject(error);
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleServerResponse(data);
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket closed');
            };
        });
    }
    
    onPoseResults(results) {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw pose landmarks
        if (results.poseLandmarks) {
            this.drawPose(results.poseLandmarks);
            
            // Send landmarks to server with current exercise
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                const landmarks = results.poseLandmarks.map(lm => ({
                    x: lm.x,
                    y: lm.y,
                    z: lm.z,
                    visibility: lm.visibility
                }));
                
                // Always include current exercise in the message
                const message = { 
                    landmarks: landmarks,
                    exercise: this.selectedExercise
                };
                
                this.ws.send(JSON.stringify(message));
            }
        }
    }
    
    drawPose(landmarks) {
        const ctx = this.ctx;
        const width = this.canvas.width;
        const height = this.canvas.height;
        
        // Draw connections
        const connections = [
            [11, 12], [11, 13], [13, 15], [12, 14], [14, 16],
            [11, 23], [12, 24], [23, 24],
            [23, 25], [25, 27], [24, 26], [26, 28],
            [27, 29], [29, 31], [28, 30], [30, 32]
        ];
        
        ctx.strokeStyle = '#00ff00';
        ctx.lineWidth = 3;
        
        connections.forEach(([start, end]) => {
            const startLm = landmarks[start];
            const endLm = landmarks[end];
            
            if (startLm.visibility > 0.5 && endLm.visibility > 0.5) {
                ctx.beginPath();
                ctx.moveTo(startLm.x * width, startLm.y * height);
                ctx.lineTo(endLm.x * width, endLm.y * height);
                ctx.stroke();
            }
        });
        
        // Draw landmarks
        ctx.fillStyle = '#ff0000';
        landmarks.forEach(lm => {
            if (lm.visibility > 0.5) {
                ctx.beginPath();
                ctx.arc(lm.x * width, lm.y * height, 5, 0, 2 * Math.PI);
                ctx.fill();
            }
        });
    }
    
    handleServerResponse(data) {
        if (data.error) {
            console.error('Server error:', data.error);
            return;
        }
        
        if (data.status === 'buffering') {
            this.updateStatus(data.message);
            return;
        }
        
        if (data.status === 'exercise_changed') {
            this.updateStatus(data.message);
            return;
        }
        
        // Update UI with results
        if (data.rep_count !== undefined) {
            this.repCount.textContent = data.rep_count;
        }
        
        if (data.phase) {
            this.phase.textContent = data.phase.toUpperCase();
        }
        
        if (data.exercise) {
            const exerciseName = data.exercise.charAt(0).toUpperCase() + data.exercise.slice(1);
            this.currentExercise.textContent = exerciseName;
        }
        
        if (data.feedback) {
            this.feedback.textContent = data.feedback;
        }
    }
    
    updateStatus(message) {
        this.statusText.textContent = message;
    }
}

// Initialize app when page loads
window.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, creating app...');
    const app = new GymTrainerApp();
    console.log('App created successfully');
});
