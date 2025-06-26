/**
 * PixelPeak BCI Frontend - Enhanced JavaScript Integration
 * Connects to FastAPI backend with proper error handling and fallbacks
 */

// ===== GLOBAL VARIABLES =====
let scene, camera, renderer, avatar;
let currentScenario = null;
let isAutoDemo = false;
let autoInterval = null;
let sessionStartTime = Date.now();
let apiResponseTimes = [];
let patternsStored = 0;
let brainwaveCanvas, brainwaveCtx;
let currentAudio = null;
let sessionId = generateSessionId();

// API Configuration
const API_BASE = 'http://localhost:8000';
const API_ENDPOINTS = {
    health: '/api/health',
    generateScenario: '/api/generate-scenario',
    processSpeech: '/api/process-speech-enhanced',
    avatarMovements: '/api/avatar-movements',
    generateCaptions: '/api/generate-captions',
    completeWorkflow: '/api/complete-enhanced-workflow',
    similarPatterns: '/api/similar-patterns',
    emotions: '/api/emotions'
};

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 PixelPeak BCI Frontend Initializing...');
    
    // Show loading screen
    showLoadingScreen();
    
    try {
        // Initialize components
        await initializeApplication();
        
        // Hide loading screen
        hideLoadingScreen();
        
        showNotification('success', 'System Ready', 'PixelPeak Neural Interface is online and ready for therapy sessions.');
        
    } catch (error) {
        console.error('❌ Initialization failed:', error);
        hideLoadingScreen();
        showNotification('error', 'Initialization Failed', 'Some components may not be available. Check console for details.');
    }
});

async function initializeApplication() {
    // Update loading progress
    updateLoadingProgress(10);
    
    // Check Three.js availability
    if (typeof THREE === 'undefined') {
        throw new Error('Three.js not loaded');
    }
    updateLoadingProgress(20);
    
    // Initialize 3D scene
    await initScene();
    updateLoadingProgress(40);
    
    // Initialize brainwave visualization
    initBrainwaveVisualization();
    updateLoadingProgress(50);
    
    // Check backend health
    await checkBackendHealth();
    updateLoadingProgress(70);
    
    // Initialize UI components
    initializeUI();
    updateLoadingProgress(85);
    
    // Load initial data
    await loadInitialData();
    updateLoadingProgress(100);
    
    console.log('✅ PixelPeak initialization complete!');
}

// ===== LOADING SCREEN =====
function showLoadingScreen() {
    document.getElementById('loading-screen').style.display = 'flex';
}

function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    loadingScreen.style.opacity = '0';
    setTimeout(() => {
        loadingScreen.style.display = 'none';
    }, 500);
}

function updateLoadingProgress(percentage) {
    const progressBar = document.getElementById('loading-progress');
    progressBar.style.width = `${percentage}%`;
}

// ===== 3D SCENE INITIALIZATION =====
async function initScene() {
    console.log('🎮 Initializing 3D Scene...');
    
    const sceneContainer = document.getElementById('scene-container');
    
    // Create scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87CEEB);
    
    // Create camera
    camera = new THREE.PerspectiveCamera(
        75,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
    );
    camera.position.set(0, 2, 5);
    camera.lookAt(0, 1, 0);
    
    // Create renderer
    renderer = new THREE.WebGLRenderer({ 
        antialias: true,
        alpha: false
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputEncoding = THREE.sRGBEncoding;
    
    sceneContainer.appendChild(renderer.domElement);
    
    // Add lighting and environment
    createLighting();
    createEnvironment();
    createDetailedAvatar();
    
    // Start render loop
    animate();
    
    updateAvatarStatus("✅ Neural Interface Connected");
    console.log('✅ 3D Scene initialized successfully');
}

function createLighting() {
    // Ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    // Main directional light
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 5);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 1024;
    directionalLight.shadow.mapSize.height = 1024;
    scene.add(directionalLight);

    // Fill light
    const fillLight = new THREE.DirectionalLight(0x87CEEB, 0.3);
    fillLight.position.set(-5, 5, -5);
    scene.add(fillLight);
}

function createEnvironment() {
    // Ground plane
    const groundGeometry = new THREE.PlaneGeometry(20, 20);
    const groundMaterial = new THREE.MeshLambertMaterial({ 
        color: 0x90EE90,
        transparent: true,
        opacity: 0.8
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = 0;
    ground.receiveShadow = true;
    scene.add(ground);

    // Backdrop
    const backdropGeometry = new THREE.PlaneGeometry(15, 8);
    const backdropMaterial = new THREE.MeshLambertMaterial({ 
        color: 0x87CEEB,
        transparent: true,
        opacity: 0.5
    });
    const backdrop = new THREE.Mesh(backdropGeometry, backdropMaterial);
    backdrop.position.set(0, 4, -8);
    scene.add(backdrop);
}

function createDetailedAvatar() {
    console.log('👤 Creating detailed avatar...');
    
    const avatarGroup = new THREE.Group();

    // Head
    const headGeometry = new THREE.SphereGeometry(0.4, 32, 16);
    const headMaterial = new THREE.MeshLambertMaterial({ color: 0xffdbac });
    const head = new THREE.Mesh(headGeometry, headMaterial);
    head.position.y = 1.8;
    head.castShadow = true;
    avatarGroup.add(head);

    // Eyes
    const eyeGeometry = new THREE.SphereGeometry(0.06, 16, 8);
    const eyeMaterial = new THREE.MeshLambertMaterial({ color: 0x2196F3 });
    
    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    leftEye.position.set(-0.15, 1.85, 0.25);
    avatarGroup.add(leftEye);
    
    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    rightEye.position.set(0.15, 1.85, 0.25);
    avatarGroup.add(rightEye);

    // Mouth
    const mouthGeometry = new THREE.SphereGeometry(0.05, 16, 8);
    const mouthMaterial = new THREE.MeshLambertMaterial({ color: 0xff6b9d });
    const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial);
    mouth.position.set(0, 1.65, 0.32);
    mouth.scale.set(2, 0.5, 0.5);
    avatarGroup.add(mouth);

    // Body
    const bodyGeometry = new THREE.CylinderGeometry(0.4, 0.5, 1.2, 16);
    const bodyMaterial = new THREE.MeshLambertMaterial({ color: 0x4169e1 });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    body.position.y = 1.0;
    body.castShadow = true;
    avatarGroup.add(body);

    // Arms
    const armGeometry = new THREE.CylinderGeometry(0.1, 0.1, 0.8, 12);
    const armMaterial = new THREE.MeshLambertMaterial({ color: 0xffdbac });
    
    const leftArm = new THREE.Mesh(armGeometry, armMaterial);
    leftArm.position.set(-0.6, 1.2, 0);
    leftArm.rotation.z = Math.PI / 6;
    leftArm.castShadow = true;
    avatarGroup.add(leftArm);

    const rightArm = new THREE.Mesh(armGeometry, armMaterial);
    rightArm.position.set(0.6, 1.2, 0);
    rightArm.rotation.z = -Math.PI / 6;
    rightArm.castShadow = true;
    avatarGroup.add(rightArm);

    // Hands
    const handGeometry = new THREE.SphereGeometry(0.12, 12, 8);
    const handMaterial = new THREE.MeshLambertMaterial({ color: 0xffdbac });
    
    const leftHand = new THREE.Mesh(handGeometry, handMaterial);
    leftHand.position.set(-0.8, 0.7, 0);
    leftHand.castShadow = true;
    avatarGroup.add(leftHand);
    
    const rightHand = new THREE.Mesh(handGeometry, handMaterial);
    rightHand.position.set(0.8, 0.7, 0);
    rightHand.castShadow = true;
    avatarGroup.add(rightHand);

    // Legs
    const legGeometry = new THREE.CylinderGeometry(0.15, 0.15, 0.9, 12);
    const legMaterial = new THREE.MeshLambertMaterial({ color: 0x2c5aa0 });
    
    const leftLeg = new THREE.Mesh(legGeometry, legMaterial);
    leftLeg.position.set(-0.2, 0.45, 0);
    leftLeg.castShadow = true;
    avatarGroup.add(leftLeg);

    const rightLeg = new THREE.Mesh(legGeometry, legMaterial);
    rightLeg.position.set(0.2, 0.45, 0);
    rightLeg.castShadow = true;
    avatarGroup.add(rightLeg);

    // Store references for animation
    avatarGroup.userData = {
        head: head,
        leftEye: leftEye,
        rightEye: rightEye,
        mouth: mouth,
        leftArm: leftArm,
        rightArm: rightArm,
        body: body,
        leftHand: leftHand,
        rightHand: rightHand,
        originalMouthScale: mouth.scale.clone(),
        originalHeadPosition: head.position.clone()
    };

    avatarGroup.position.set(0, 0, 0);
    scene.add(avatarGroup);
    avatar = avatarGroup;
    
    console.log('✅ Avatar created successfully');
}

function animate() {
    requestAnimationFrame(animate);
    
    if (avatar && avatar.userData) {
        const time = Date.now() * 0.002;
        
        // Breathing animation
        const breathe = Math.sin(time) * 0.02;
        avatar.userData.body.scale.y = 1 + breathe;
        avatar.position.y = breathe * 2;
        
        // Emotion-based animations
        if (currentScenario) {
            animateAvatarByEmotion(currentScenario.emotion, time);
        }
        
        // Arm movements
        const armSway = Math.sin(time * 0.7) * 0.1;
        avatar.userData.leftArm.rotation.z = Math.PI / 6 + armSway;
        avatar.userData.rightArm.rotation.z = -Math.PI / 6 - armSway;
    }
    
    // Update brainwave visualization
    updateBrainwaveVisualization();
    
    renderer.render(scene, camera);
}

function animateAvatarByEmotion(emotion, time) {
    const userData = avatar.userData;
    
    switch(emotion) {
        case 'excited':
        case 'happy':
            userData.head.position.y = userData.originalHeadPosition.y + Math.sin(time * 2) * 0.02;
            userData.leftHand.rotation.z = Math.sin(time * 3) * 0.2;
            userData.rightHand.rotation.z = Math.sin(time * 3) * 0.2;
            break;
            
        case 'sad':
            userData.head.rotation.x = -0.1;
            userData.head.position.y = userData.originalHeadPosition.y - 0.05;
            break;
            
        case 'calm':
            userData.head.rotation.x = 0;
            userData.head.position.y = userData.originalHeadPosition.y;
            break;
            
        case 'anxious':
            userData.leftHand.position.x = -0.8 + Math.sin(time * 8) * 0.02;
            userData.rightHand.position.x = 0.8 + Math.sin(time * 8) * 0.02;
            break;
            
        case 'neutral':
        default:
            userData.head.rotation.x = 0;
            userData.head.position.y = userData.originalHeadPosition.y;
            break;
    }
}

// ===== BRAINWAVE VISUALIZATION =====
function initBrainwaveVisualization() {
    brainwaveCanvas = document.getElementById('brainwave-canvas');
    brainwaveCtx = brainwaveCanvas.getContext('2d');
    
    // Set canvas size
    const rect = brainwaveCanvas.getBoundingClientRect();
    brainwaveCanvas.width = rect.width * window.devicePixelRatio;
    brainwaveCanvas.height = rect.height * window.devicePixelRatio;
    brainwaveCtx.scale(window.devicePixelRatio, window.devicePixelRatio);
}

function updateBrainwaveVisualization() {
    if (!brainwaveCtx) return;
    
    const canvas = brainwaveCanvas;
    const ctx = brainwaveCtx;
    const width = canvas.width / window.devicePixelRatio;
    const height = canvas.height / window.devicePixelRatio;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw brainwave pattern
    ctx.strokeStyle = '#4fc3f7';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    const time = Date.now() * 0.005;
    const centerY = height / 2;
    
    for (let x = 0; x < width; x++) {
        const frequency = currentScenario ? getEmotionFrequency(currentScenario.emotion) : 1;
        const amplitude = currentScenario ? getEmotionAmplitude(currentScenario.emotion) : 10;
        
        const y = centerY + Math.sin((x * 0.02 + time) * frequency) * amplitude;
        
        if (x === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    }
    
    ctx.stroke();
}

function getEmotionFrequency(emotion) {
    const frequencies = {
        'excited': 3,
        'happy': 2.5,
        'anxious': 4,
        'calm': 1,
        'sad': 0.8,
        'neutral': 1.5
    };
    return frequencies[emotion] || 1;
}

function getEmotionAmplitude(emotion) {
    const amplitudes = {
        'excited': 15,
        'happy': 12,
        'anxious': 18,
        'calm': 8,
        'sad': 6,
        'neutral': 10
    };
    return amplitudes[emotion] || 10;
}

// ===== BACKEND INTEGRATION =====
async function checkBackendHealth() {
    console.log('🔍 Checking backend health...');
    
    try {
        const response = await fetch(`${API_BASE}${API_ENDPOINTS.health}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const health = await response.json();
            updateAPIStatus(health);
            document.getElementById('backend-status').textContent = health.status;
            console.log('✅ Backend health check passed:', health.status);
            return health;
        } else {
            throw new Error(`Backend health check failed: ${response.status}`);
        }
    } catch (error) {
        console.error('❌ Backend health check failed:', error);
        updateAPIStatus(null);
        document.getElementById('backend-status').textContent = 'Offline';
        showNotification('warning', 'Backend Offline', 'Some features may not work properly. Check if backend server is running.');
        return null;
    }
}

function updateAPIStatus(health) {
    const indicators = {
        'groq-status': 'Groq LLM',
        'elevenlabs-status': 'ElevenLabs TTS', 
        'pinecone-status': 'Pinecone VectorDB'
    };
    
    Object.keys(indicators).forEach(id => {
        const indicator = document.getElementById(id);
        if (health && health.services) {
            const isOnline = health.services[id.replace('-status', '')] === '✅';
            indicator.className = `api-indicator ${isOnline ? 'online' : 'offline'}`;
            
            // Check for fallback mode
            if (health.fallback_info && health.fallback_info.elevenlabs_fallback && id === 'elevenlabs-status') {
                indicator.className = 'api-indicator fallback';
            }
        } else {
            indicator.className = 'api-indicator offline';
        }
    });
}

// ===== API CALLS =====
async function generateScenario() {
    const startTime = Date.now();
    updateAvatarStatus("🧬 Generating Neural Pattern...");
    setButtonState('generate-scenario-btn', false);
    
    try {
        const response = await fetch(`${API_BASE}${API_ENDPOINTS.generateScenario}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                context: "VR therapy session with avatar interaction",
                include_movement: true,
                include_captions: true
            })
        });
        
        if (response.ok) {
            const scenario = await response.json();
            console.log('📊 Generated scenario:', scenario);
            
            // Convert backend response to frontend format
            const enhancedScenario = {
                id: scenario.id,
                emotion: scenario.emotion,
                direction: scenario.direction,
                emotionConfidence: scenario.emotion_confidence,
                directionConfidence: scenario.direction_confidence,
                speech: scenario.speech,
                context: scenario.context || "",
                avatarMovement: scenario.avatar_movement,
                captionStyle: scenario.caption_style,
                speechDuration: scenario.speech_duration || 3000,
                generatedAt: scenario.generated_at
            };
            
            await updateCurrentScenario(enhancedScenario);
            updateAvatarStatus("✅ Neural Pattern Generated");
            patternsStored++;
            
            const responseTime = Date.now() - startTime;
            updateMetrics(responseTime);
            
            showNotification('success', 'Pattern Generated', `New ${scenario.emotion} pattern created successfully.`);
            
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
    } catch (error) {
        console.error('❌ Error generating scenario:', error);
        // Fallback to local scenario
        const fallbackScenario = createFallbackScenario();
        await updateCurrentScenario(fallbackScenario);
        updateAvatarStatus("✅ Using Cached Pattern");
        showNotification('warning', 'Using Fallback', 'Generated local pattern due to API error.');
    }
    
    setButtonState('generate-scenario-btn', true);
}

async function processSpeech() {
    if (!currentScenario) {
        showNotification('error', 'No Scenario', 'Please generate a scenario first.');
        return;
    }
    
    updateAvatarStatus("🗣️ Converting Thoughts to Speech...");
    setButtonState('process-speech-btn', false);
    setButtonState('stop-audio-btn', true);
    
    try {
        const response = await fetch(`${API_BASE}${API_ENDPOINTS.processSpeech}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                scenario_id: currentScenario.id,
                text: currentScenario.speech,
                emotion: currentScenario.emotion,
                include_movement: true,
                words_count: 20
            })
        });
        
        if (response.ok) {
            const speechResult = await response.json();
            console.log('🎵 Speech result:', speechResult);
            
            if (speechResult.success) {
                // Update avatar movement based on response
                if (speechResult.avatar_movement) {
                    applyAvatarMovement(speechResult.avatar_movement);
                }
                
                // Show captions
                if (speechResult.caption_style) {
                    showCaptions(currentScenario.speech, speechResult.caption_style);
                }
                
                // Handle audio
                if (speechResult.audio_available && speechResult.supports_playback && speechResult.audio_url) {
                    await playAudio(speechResult.audio_url, speechResult.duration_estimate);
                    showNotification('success', 'Speech Generated', 'Audio playback started.');
                } else {
                    // Fallback mode - show visual feedback only
                    animateTextSpeech(speechResult.duration_estimate || 3000);
                    const fallbackMsg = speechResult.fallback_mode ? 
                        speechResult.user_message : 'Audio not available, showing visual feedback.';
                    showNotification('info', 'Visual Mode', fallbackMsg);
                }
                
                updateAvatarStatus("✅ Speech Processing Complete");
            } else {
                throw new Error(speechResult.error || 'Speech processing failed');
            }
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
    } catch (error) {
        console.error('❌ Error processing speech:', error);
        // Fallback to text animation
        animateTextSpeech(3000);
        updateAvatarStatus("✅ Speech Complete (Visual Only)");
        showNotification('warning', 'Audio Unavailable', 'Showing visual feedback only.');
    }
    
    setButtonState('process-speech-btn', true);
    setTimeout(() => setButtonState('stop-audio-btn', false), 1000);
}

async function findSimilarPatterns() {
    if (!currentScenario) {
        showNotification('error', 'No Scenario', 'Please generate a scenario first.');
        return;
    }
    
    updateAvatarStatus("🔍 Searching Neural Database...");
    setButtonState('find-similar-btn', false);
    
    try {
        const response = await fetch(`${API_BASE}${API_ENDPOINTS.similarPatterns}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                emotion: currentScenario.emotion,
                direction: currentScenario.direction,
                context: currentScenario.context || "",
                top_k: 3,
                min_score: 0.7
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            
            if (result.success && result.similar_patterns && result.similar_patterns.length > 0) {
                displaySimilarPatterns(result.similar_patterns);
                updateAvatarStatus(`✅ Found ${result.similar_patterns.length} Similar Patterns`);
                showNotification('success', 'Patterns Found', `Found ${result.similar_patterns.length} similar neural patterns.`);
            } else {
                updateAvatarStatus("ℹ️ No Similar Patterns Found");
                showNotification('info', 'No Matches', 'No similar patterns found in the database.');
            }
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
    } catch (error) {
        console.error('❌ Error finding similar patterns:', error);
        updateAvatarStatus("⚠️ Pattern Search Failed");
        showNotification('error', 'Search Failed', 'Could not search for similar patterns.');
    }
    
    setButtonState('find-similar-btn', true);
}

async function getAvatarMovement() {
    if (!currentScenario) return;
    
    try {
        const response = await fetch(`${API_BASE}${API_ENDPOINTS.avatarMovements}/${currentScenario.emotion}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const result = await response.json();
            if (result.success) {
                applyAvatarMovement(result.movement);
                showNotification('success', 'Avatar Movement', `Applied ${currentScenario.emotion} movement.`);
            }
        }
    } catch (error) {
        console.error('❌ Error getting avatar movement:', error);
    }
}

async function completeWorkflow() {
    updateAvatarStatus("⚡ Running Complete Workflow...");
    setButtonState('complete-workflow-btn', false);
    
    try {
        const response = await fetch(`${API_BASE}${API_ENDPOINTS.completeWorkflow}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                context: "Complete therapy workflow",
                include_movement: true,
                include_captions: true
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('⚡ Complete workflow result:', result);
            
            if (result.success) {
                // Update scenario
                const scenario = result.scenario;
                const enhancedScenario = {
                    id: scenario.id,
                    emotion: scenario.emotion,
                    direction: scenario.direction,
                    emotionConfidence: scenario.emotion_confidence,
                    directionConfidence: scenario.direction_confidence,
                    speech: scenario.speech,
                    context: scenario.context || "",
                    avatarMovement: result.avatar_movement,
                    captionStyle: result.captions.style,
                    speechDuration: result.audio.duration || 3000,
                    generatedAt: scenario.generated_at
                };
                
                await updateCurrentScenario(enhancedScenario);
                
                // Apply movements and captions
                if (result.avatar_movement) {
                    applyAvatarMovement(result.avatar_movement);
                }
                
                if (result.captions.success && result.captions.chunks) {
                    showCaptionChunks(result.captions.chunks, result.captions.timing);
                }
                
                // Handle audio
                if (result.audio.success && result.audio.url) {
                    await playAudio(result.audio.url, result.audio.duration);
                }
                
                updateAvatarStatus("✅ Complete Workflow Finished");
                showNotification('success', 'Workflow Complete', 'Full therapy workflow executed successfully.');
            }
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
    } catch (error) {
        console.error('❌ Error in complete workflow:', error);
        updateAvatarStatus("⚠️ Workflow Failed");
        showNotification('error', 'Workflow Failed', 'Could not complete the full workflow.');
    }
    
    setButtonState('complete-workflow-btn', true);
}

// ===== AVATAR MOVEMENT FUNCTIONS =====
function applyAvatarMovement(movementConfig) {
    if (!avatar || !movementConfig) return;
    
    console.log('💃 Applying avatar movement:', movementConfig);
    
    const duration = movementConfig.duration * 1000 || 3000;
    const action = movementConfig.action || 'idle_breathing';
    
    // Clear any existing animation
    if (avatar.userData.movementInterval) {
        clearInterval(avatar.userData.movementInterval);
    }
    
    // Apply movement based on action type
    switch (action) {
        case 'walk_and_jump':
            animateWalkAndJump(duration, movementConfig);
            break;
        case 'energetic_gestures':
            animateEnergeticGestures(duration, movementConfig);
            break;
        case 'gentle_sway':
            animateGentleSway(duration, movementConfig);
            break;
        case 'sit_and_slump':
            animateSitAndSlump(duration, movementConfig);
            break;
        case 'nervous_fidget':
            animateNervousFidget(duration, movementConfig);
            break;
        case 'idle_breathing':
        default:
            animateIdleBreathing(duration, movementConfig);
            break;
    }
}

function animateWalkAndJump(duration, config) {
    const startTime = Date.now();
    const jumpHeight = config.jump_height || 0.3;
    const speed = config.speed || 1.2;
    
    avatar.userData.movementInterval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const progress = (elapsed % 2000) / 2000; // 2-second cycle
        
        // Walking animation
        avatar.position.x = Math.sin(progress * Math.PI * 2) * 0.5;
        
        // Jumping animation
        if (progress > 0.3 && progress < 0.7) {
            avatar.position.y = Math.sin((progress - 0.3) * Math.PI / 0.4) * jumpHeight;
        }
        
        if (elapsed > duration) {
            clearInterval(avatar.userData.movementInterval);
            avatar.position.set(0, 0, 0);
        }
    }, 16);
}

function animateEnergeticGestures(duration, config) {
    const startTime = Date.now();
    const intensity = config.gesture_intensity || 1.5;
    
    avatar.userData.movementInterval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const time = elapsed * 0.01;
        
        // Energetic arm movements
        avatar.userData.leftArm.rotation.z = Math.PI / 6 + Math.sin(time * 3) * 0.5 * intensity;
        avatar.userData.rightArm.rotation.z = -Math.PI / 6 + Math.sin(time * 3 + Math.PI) * 0.5 * intensity;
        
        // Body movement
        avatar.userData.body.rotation.y = Math.sin(time * 2) * 0.2 * intensity;
        
        if (elapsed > duration) {
            clearInterval(avatar.userData.movementInterval);
            avatar.userData.leftArm.rotation.z = Math.PI / 6;
            avatar.userData.rightArm.rotation.z = -Math.PI / 6;
            avatar.userData.body.rotation.y = 0;
        }
    }, 16);
}

function animateGentleSway(duration, config) {
    const startTime = Date.now();
    const amplitude = config.sway_amplitude || 0.1;
    
    avatar.userData.movementInterval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const time = elapsed * 0.002;
        
        // Gentle swaying
        avatar.rotation.y = Math.sin(time) * amplitude;
        avatar.position.x = Math.sin(time * 0.5) * amplitude * 0.5;
        
        if (elapsed > duration) {
            clearInterval(avatar.userData.movementInterval);
            avatar.rotation.y = 0;
            avatar.position.x = 0;
        }
    }, 16);
}

function animateSitAndSlump(duration, config) {
    const startTime = Date.now();
    const sitHeight = config.sit_height || 0.5;
    const slumpAngle = config.slump_angle || 0.3;
    
    avatar.userData.movementInterval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / 2000, 1); // 2 seconds to complete
        
        // Sitting animation
        avatar.position.y = -sitHeight * progress;
        avatar.userData.body.rotation.x = slumpAngle * progress;
        avatar.userData.head.rotation.x = -0.2 * progress;
        
        if (elapsed > duration) {
            clearInterval(avatar.userData.movementInterval);
        }
    }, 16);
}

function animateNervousFidget(duration, config) {
    const startTime = Date.now();
    const intensity = config.fidget_intensity || 1.2;
    
    avatar.userData.movementInterval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const time = elapsed * 0.02;
        
        // Nervous fidgeting
        avatar.userData.leftHand.position.x = -0.8 + Math.sin(time * 8) * 0.05 * intensity;
        avatar.userData.rightHand.position.x = 0.8 + Math.sin(time * 8 + 1) * 0.05 * intensity;
        avatar.userData.head.rotation.y = Math.sin(time * 4) * 0.1 * intensity;
        
        if (elapsed > duration) {
            clearInterval(avatar.userData.movementInterval);
            avatar.userData.leftHand.position.x = -0.8;
            avatar.userData.rightHand.position.x = 0.8;
            avatar.userData.head.rotation.y = 0;
        }
    }, 16);
}

function animateIdleBreathing(duration, config) {
    const startTime = Date.now();
    const breathDepth = config.breathing_depth || 0.05;
    
    avatar.userData.movementInterval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const time = elapsed * 0.003;
        
        // Subtle breathing
        avatar.userData.body.scale.y = 1 + Math.sin(time) * breathDepth;
        
        if (elapsed > duration) {
            clearInterval(avatar.userData.movementInterval);
            avatar.userData.body.scale.y = 1;
        }
    }, 16);
}

// ===== AUDIO FUNCTIONS =====
async function playAudio(audioUrl, duration) {
    try {
        // Stop any existing audio
        if (currentAudio) {
            currentAudio.pause();
            currentAudio = null;
        }
        
        currentAudio = new Audio(`${API_BASE}${audioUrl}`);
        
        // Animate avatar mouth during speech
        animateAvatarSpeaking(duration || 3000);
        
        currentAudio.onended = () => {
            updateAvatarStatus("✅ Speech Complete");
            stopAvatarSpeaking();
            currentAudio = null;
        };
        
        currentAudio.onerror = () => {
            console.warn('⚠️ Audio playback failed, using visual feedback');
            animateTextSpeech(duration || 3000);
        };
        
        await currentAudio.play();
        updateAvatarStatus("🎵 Playing Neural Speech");
        
    } catch (error) {
        console.error('❌ Audio error:', error);
        animateTextSpeech(duration || 3000);
    }
}

function animateAvatarSpeaking(duration) {
    if (!avatar || !avatar.userData.mouth) return;
    
    const mouth = avatar.userData.mouth;
    const originalScale = avatar.userData.originalMouthScale;
    
    const speakingAnimation = () => {
        const scale = 1 + Math.sin(Date.now() * 0.02) * 0.3;
        mouth.scale.set(
            originalScale.x * scale, 
            originalScale.y, 
            originalScale.z
        );
    };
    
    avatar.userData.speakingInterval = setInterval(speakingAnimation, 50);
    
    setTimeout(() => {
        stopAvatarSpeaking();
    }, duration);
}

function stopAvatarSpeaking() {
    if (avatar && avatar.userData.speakingInterval) {
        clearInterval(avatar.userData.speakingInterval);
        if (avatar.userData.mouth && avatar.userData.originalMouthScale) {
            avatar.userData.mouth.scale.copy(avatar.userData.originalMouthScale);
        }
    }
    
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }
}

function animateTextSpeech(duration) {
    const speechContent = document.getElementById('speech-content');
    if (!speechContent || !currentScenario) return;
    
    speechContent.innerHTML = `<span class="wave-animation">${currentScenario.speech}</span>`;
    
    animateAvatarSpeaking(duration);
    
    setTimeout(() => {
        speechContent.textContent = currentScenario.speech;
        stopAvatarSpeaking();
        updateAvatarStatus("✅ Speech Complete (Visual)");
    }, duration);
}

// ===== CAPTION FUNCTIONS =====
function showCaptions(text, style) {
    const captionDisplay = document.getElementById('caption-display');
    const captionContent = document.getElementById('caption-content');
    
    if (style) {
        captionContent.style.color = style.color || '#ffffff';
        captionContent.style.background = style.background || 'rgba(0, 0, 0, 0.8)';
        captionContent.style.borderColor = style.border_color || 'rgba(255, 255, 255, 0.3)';
    }
    
    captionContent.textContent = text;
    captionDisplay.style.display = 'block';
    
    // Auto-hide after duration
    setTimeout(() => {
        captionDisplay.style.display = 'none';
    }, 5000);
}

function showCaptionChunks(chunks, timing) {
    if (!chunks || chunks.length === 0) return;
    
    const chunkDuration = timing?.chunk_duration * 1000 || 2000;
    
    chunks.forEach((chunk, index) => {
        setTimeout(() => {
            showCaptions(chunk, currentScenario?.captionStyle);
        }, index * chunkDuration);
    });
}

// ===== UI UPDATE FUNCTIONS =====
async function updateCurrentScenario(scenario) {
    currentScenario = scenario;
    
    console.log('📊 Updating scenario:', scenario);
    
    // Update emotion display
    const emotionElement = document.getElementById('current-emotion');
    emotionElement.textContent = scenario.emotion.charAt(0).toUpperCase() + scenario.emotion.slice(1);
    emotionElement.className = `status-value emotion-${scenario.emotion}`;
    
    // Update direction display
    const directionElement = document.getElementById('current-direction');
    directionElement.textContent = scenario.direction.charAt(0).toUpperCase() + scenario.direction.slice(1);
    directionElement.className = `status-value direction-${scenario.direction}`;
    
    // Update confidence bars
    animateConfidenceBar('emotion-confidence', 'emotion-confidence-text', scenario.emotionConfidence * 100);
    animateConfidenceBar('direction-confidence', 'direction-confidence-text', scenario.directionConfidence * 100);
    
    // Update speech display
    const speechDisplay = document.getElementById('speech-display');
    const speechContent = document.getElementById('speech-content');
    const speechMetadata = document.getElementById('speech-metadata');
    
    speechContent.textContent = scenario.speech;
    speechMetadata.innerHTML = `
        <span>Confidence: E${Math.round(scenario.emotionConfidence * 100)}% / D${Math.round(scenario.directionConfidence * 100)}%</span>
        <span>Duration: ${Math.round(scenario.speechDuration / 1000)}s</span>
    `;
    speechDisplay.style.display = 'block';
    
    // Enable buttons
    setButtonState('process-speech-btn', true);
    setButtonState('avatar-movement-btn', true);
    setButtonState('find-similar-btn', true);
    setButtonState('complete-workflow-btn', true);
    
    // Update scenario list
    addScenarioToList(scenario);
}

function animateConfidenceBar(barId, textId, targetWidth) {
    const barElement = document.getElementById(barId);
    const textElement = document.getElementById(textId);
    
    let currentWidth = 0;
    const step = targetWidth / 30;
    
    const animate = () => {
        if (currentWidth < targetWidth) {
            currentWidth += step;
            const width = Math.min(currentWidth, targetWidth);
            barElement.style.width = `${width}%`;
            textElement.textContent = `${Math.round(width)}%`;
            requestAnimationFrame(animate);
        }
    };
    animate();
}

function addScenarioToList(scenario) {
    const scenarioList = document.getElementById('scenario-list');
    
    // Clear loading message if present
    const loadingItem = scenarioList.querySelector('.loading-item');
    if (loadingItem) {
        loadingItem.remove();
    }
    
    const item = document.createElement('div');
    item.className = 'scenario-item active';
    item.onclick = () => selectScenario(scenario);
    
    item.innerHTML = `
        <div class="scenario-emotion emotion-${scenario.emotion}">
            ${scenario.emotion} + ${scenario.direction}
            <span class="scenario-time">${new Date().toLocaleTimeString()}</span>
        </div>
        <div class="scenario-speech">"${scenario.speech}"</div>
        <div class="scenario-metadata">
            <div class="scenario-confidence">
                <span class="confidence-badge">E${Math.round(scenario.emotionConfidence * 100)}%</span>
                <span class="confidence-badge">D${Math.round(scenario.directionConfidence * 100)}%</span>
            </div>
            <span class="scenario-id">${scenario.id}</span>
        </div>
    `;
    
    // Remove active class from other items
    scenarioList.querySelectorAll('.scenario-item').forEach(item => {
        item.classList.remove('active');
    });
    
    scenarioList.insertBefore(item, scenarioList.firstChild);
    
    // Limit to 10 scenarios
    const items = scenarioList.querySelectorAll('.scenario-item');
    if (items.length > 10) {
        items[items.length - 1].remove();
    }
}

function selectScenario(scenario) {
    updateCurrentScenario(scenario);
    
    // Update active state in list
    document.querySelectorAll('.scenario-item').forEach(item => {
        item.classList.remove('active');
    });
    event.currentTarget.classList.add('active');
}

function displaySimilarPatterns(patterns) {
    const similarSection = document.getElementById('similar-patterns');
    const similarList = document.getElementById('similar-list');
    
    similarList.innerHTML = '';
    
    patterns.forEach(pattern => {
        const item = document.createElement('div');
        item.className = 'similar-item';
        item.onclick = () => {
            // Convert pattern to scenario format
            const scenario = {
                id: pattern.id,
                emotion: pattern.emotion,
                direction: pattern.direction,
                emotionConfidence: pattern.emotion_confidence,
                directionConfidence: pattern.direction_confidence,
                speech: pattern.context,
                context: pattern.context,
                speechDuration: 3000,
                generatedAt: pattern.timestamp
            };
            updateCurrentScenario(scenario);
        };
        
        item.innerHTML = `
            <div class="scenario-emotion emotion-${pattern.emotion}">
                ${pattern.emotion} + ${pattern.direction}
                <span class="similar-score">${Math.round(pattern.similarity_score * 100)}%</span>
            </div>
            <div class="scenario-speech">"${pattern.context}"</div>
            <div style="font-size: 11px; color: #4fc3f7; margin-top: 5px;">
                Confidence: E${Math.round(pattern.emotion_confidence * 100)}% / D${Math.round(pattern.direction_confidence * 100)}%
            </div>
        `;
        
        similarList.appendChild(item);
    });
    
    similarSection.style.display = 'block';
    
    // Auto-hide after 15 seconds
    setTimeout(() => {
        similarSection.style.display = 'none';
    }, 15000);
}

function updateMetrics(responseTime) {
    // Update response time
    document.getElementById('response-time').textContent = `${responseTime}ms`;
    apiResponseTimes.push(responseTime);
    
    // Keep only last 10 response times
    if (apiResponseTimes.length > 10) {
        apiResponseTimes.shift();
    }
    
    // Update accuracy based on confidence
    if (currentScenario) {
        const accuracy = Math.round((currentScenario.emotionConfidence + currentScenario.directionConfidence) / 2 * 100);
        document.getElementById('accuracy-score').textContent = `${accuracy}%`;
    }
    
    // Update patterns stored
    document.getElementById('patterns-stored').textContent = patternsStored;
    
    // Update session time
    const sessionTime = Math.floor((Date.now() - sessionStartTime) / 1000);
    const minutes = Math.floor(sessionTime / 60);
    const seconds = sessionTime % 60;
    document.getElementById('session-time').textContent = 
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function updateAvatarStatus(status) {
    document.getElementById('avatar-status').textContent = status;
}

// ===== UTILITY FUNCTIONS =====
function setButtonState(buttonId, enabled) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = !enabled;
    }
}

function createFallbackScenario() {
    const emotions = ['calm', 'happy', 'excited', 'sad', 'anxious', 'neutral'];
    const directions = ['forward', 'backward', 'left', 'right', 'stop', 'up', 'down'];
    
    const emotion = emotions[Math.floor(Math.random() * emotions.length)];
    const direction = directions[Math.floor(Math.random() * directions.length)];
    
    const speechTemplates = {
        calm: "I feel peaceful and centered, ready to move forward in my therapy journey.",
        happy: "I'm feeling joyful and optimistic about my progress and the possibilities ahead.",
        excited: "I'm energized and enthusiastic! This therapy session is going really well today.",
        sad: "I'm feeling down right now, but I know this is part of my healing process.",
        anxious: "I'm feeling nervous and worried, but I'm trying to work through these feelings.",
        neutral: "I'm in a balanced state, neither particularly high nor low right now."
    };
    
    return {
        id: `fallback_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        emotion: emotion,
        direction: direction,
        emotionConfidence: 0.75 + Math.random() * 0.2,
        directionConfidence: 0.70 + Math.random() * 0.25,
        speech: speechTemplates[emotion] || speechTemplates.neutral,
        context: `Fallback scenario - ${emotion} patient with ${direction} intent`,
        speechDuration: 3000,
        generatedAt: new Date().toISOString()
    };
}

function generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// ===== AUTO DEMO FUNCTIONS =====
function toggleAutoDemo() {
    const btn = document.getElementById('auto-demo-btn');
    const status = document.getElementById('demo-status');
    
    if (!isAutoDemo) {
        startAutoDemo(btn, status);
    } else {
        stopAutoDemo(btn, status);
    }
}

function startAutoDemo(btn, status) {
    isAutoDemo = true;
    btn.innerHTML = '<span class="btn-icon">⏸️</span><span class="btn-text">Pause Demo</span>';
    status.textContent = "Auto Demo Running";
    
    // Run demo cycle every 15 seconds
    autoInterval = setInterval(async () => {
        if (isAutoDemo) {
            await runDemoCycle();
        }
    }, 15000);
    
    // Start first cycle immediately
    runDemoCycle();
    
    showNotification('info', 'Auto Demo Started', 'Automatic therapy demonstration is now running.');
}

function stopAutoDemo(btn, status) {
    isAutoDemo = false;
    btn.innerHTML = '<span class="btn-icon">▶️</span><span class="btn-text">Auto Demo</span>';
    status.textContent = "Manual Control";
    
    if (autoInterval) {
        clearInterval(autoInterval);
        autoInterval = null;
    }
    
    showNotification('info', 'Auto Demo Stopped', 'Returned to manual control mode.');
}

async function runDemoCycle() {
    try {
        // Step 1: Generate new scenario
        await generateScenario();
        
        // Wait 3 seconds
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        if (!isAutoDemo) return;
        
        // Step 2: Process speech
        await processSpeech();
        
        // Wait 5 seconds
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        if (!isAutoDemo) return;
        
        // Step 3: Find similar patterns
        await findSimilarPatterns();
        
    } catch (error) {
        console.error('❌ Error in demo cycle:', error);
    }
}

// ===== NOTIFICATION SYSTEM =====
function showNotification(type, title, message, duration = 5000) {
    const container = document.getElementById('notification-container');
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    notification.innerHTML = `
        <div class="notification-header">
            <span>${icons[type] || 'ℹ️'}</span>
            <span>${title}</span>
        </div>
        <div class="notification-body">${message}</div>
    `;
    
    notification.onclick = () => {
        notification.remove();
    };
    
    container.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
    
    // Keep only 5 notifications max
    const notifications = container.querySelectorAll('.notification');
    if (notifications.length > 5) {
        notifications[0].remove();
    }
}

// ===== UI INITIALIZATION =====
function initializeUI() {
    console.log('🎨 Initializing UI components...');
    
    // Set session info
    document.getElementById('patient-id').textContent = `P${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`;
    document.getElementById('session-id').textContent = sessionId.substr(-8);
    
    // Set up event listeners
    setupEventListeners();
    
    // Start session timer
    startSessionTimer();
    
    // Initialize brainwave animation
    if (brainwaveCanvas) {
        setInterval(updateBrainwaveVisualization, 50);
    }
    
    console.log('✅ UI initialization complete');
}

function setupEventListeners() {
    // Main control buttons
    document.getElementById('generate-scenario-btn').addEventListener('click', generateScenario);
    document.getElementById('process-speech-btn').addEventListener('click', processSpeech);
    document.getElementById('avatar-movement-btn').addEventListener('click', getAvatarMovement);
    document.getElementById('find-similar-btn').addEventListener('click', findSimilarPatterns);
    document.getElementById('complete-workflow-btn').addEventListener('click', completeWorkflow);
    document.getElementById('auto-demo-btn').addEventListener('click', toggleAutoDemo);
    document.getElementById('stop-audio-btn').addEventListener('click', stopAudio);
    
    // Scenario controls
    document.getElementById('refresh-scenarios').addEventListener('click', refreshScenarios);
    document.getElementById('clear-patterns').addEventListener('click', clearPatterns);
    
    // Window resize handler
    window.addEventListener('resize', onWindowResize);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

function stopAudio() {
    stopAvatarSpeaking();
    updateAvatarStatus("⏹️ Audio Stopped");
    setButtonState('stop-audio-btn', false);
    showNotification('info', 'Audio Stopped', 'Speech playback has been stopped.');
}

function refreshScenarios() {
    const scenarioList = document.getElementById('scenario-list');
    scenarioList.innerHTML = '<div class="loading-item"><div class="loading-spinner small"></div><span>Refreshing patterns...</span></div>';
    
    setTimeout(() => {
        scenarioList.innerHTML = '<div class="loading-item"><span>No patterns loaded. Generate a new pattern to begin.</span></div>';
        showNotification('info', 'Scenarios Refreshed', 'Scenario list has been refreshed.');
    }, 1000);
}

function clearPatterns() {
    const scenarioList = document.getElementById('scenario-list');
    scenarioList.innerHTML = '<div class="loading-item"><span>No patterns loaded. Generate a new pattern to begin.</span></div>';
    
    const similarSection = document.getElementById('similar-patterns');
    similarSection.style.display = 'none';
    
    patternsStored = 0;
    updateMetrics(0);
    
    showNotification('info', 'Patterns Cleared', 'All scenario patterns have been cleared.');
}

function onWindowResize() {
    if (camera && renderer) {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }
    
    // Reinitialize brainwave canvas
    if (brainwaveCanvas) {
        const rect = brainwaveCanvas.getBoundingClientRect();
        brainwaveCanvas.width = rect.width * window.devicePixelRatio;
        brainwaveCanvas.height = rect.height * window.devicePixelRatio;
        brainwaveCtx.scale(window.devicePixelRatio, window.devicePixelRatio);
    }
}

function handleKeyboardShortcuts(event) {
    // Only handle shortcuts if not typing in an input
    if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
        return;
    }
    
    switch (event.key) {
        case 'g':
        case 'G':
            event.preventDefault();
            generateScenario();
            break;
        case 's':
        case 'S':
            event.preventDefault();
            if (currentScenario) processSpeech();
            break;
        case 'f':
        case 'F':
            event.preventDefault();
            if (currentScenario) findSimilarPatterns();
            break;
        case 'a':
        case 'A':
            event.preventDefault();
            toggleAutoDemo();
            break;
        case 'Escape':
            event.preventDefault();
            stopAudio();
            break;
    }
}

function startSessionTimer() {
    setInterval(() => {
        updateMetrics(0);
    }, 1000);
}

// ===== LOAD INITIAL DATA =====
async function loadInitialData() {
    console.log('📡 Loading initial data...');
    
    try {
        // Try to load available emotions from backend
        const response = await fetch(`${API_BASE}${API_ENDPOINTS.emotions}`);
        if (response.ok) {
            const emotions = await response.json();
            console.log('✅ Available emotions:', emotions);
        }
    } catch (error) {
        console.warn('⚠️ Could not load emotions from backend:', error);
    }
    
    // Set initial scenario list state
    const scenarioList = document.getElementById('scenario-list');
    scenarioList.innerHTML = '<div class="loading-item"><span>No patterns loaded. Generate a new pattern to begin.</span></div>';
    
    console.log('✅ Initial data loading complete');
}

// ===== ERROR HANDLING =====
window.addEventListener('error', (event) => {
    console.error('❌ Global error:', event.error);
    showNotification('error', 'System Error', `An error occurred: ${event.error.message}`);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('❌ Unhandled promise rejection:', event.reason);
    showNotification('error', 'Promise Error', 'A promise was rejected without handling.');
});

// ===== CONSOLE INFORMATION =====
console.log(`
🚀 PixelPeak Enhanced BCI Frontend Initialized!

🎯 Features:
- ✅ Three.js Avatar with emotion-based animations
- ✅ Real-time backend API integration
- ✅ Enhanced speech processing with fallbacks
- ✅ Avatar movement system
- ✅ Caption display system
- ✅ Similar pattern search
- ✅ Auto-demo mode
- ✅ Comprehensive error handling

🔗 Backend Integration:
- API Base: ${API_BASE}
- Health Check: ${API_ENDPOINTS.health}
- Generate Scenario: ${API_ENDPOINTS.generateScenario}
- Process Speech: ${API_ENDPOINTS.processSpeech}
- Avatar Movements: ${API_ENDPOINTS.avatarMovements}
- Similar Patterns: ${API_ENDPOINTS.similarPatterns}

🎮 Controls:
- G: Generate new scenario
- S: Process speech
- F: Find similar patterns  
- A: Toggle auto demo
- ESC: Stop audio

🧠 Avatar Emotions: calm, excited, happy, sad, anxious, neutral
🎭 Movement Types: walk_and_jump, energetic_gestures, gentle_sway, sit_and_slump, nervous_fidget, idle_breathing

Ready for neural interface therapy! 🧠✨
`);