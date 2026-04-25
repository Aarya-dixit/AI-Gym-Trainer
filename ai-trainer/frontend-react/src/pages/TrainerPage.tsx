import { useState, useRef, useEffect, useCallback } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Play, 
  Pause, 
  RotateCcw, 
  ArrowLeft, 
  Video, 
  VideoOff,
  Activity,
  Target,
  Flame,
  TrendingUp
} from 'lucide-react'
import { Pose } from '@mediapipe/pose'
import { Camera } from '@mediapipe/camera_utils'

interface PoseLandmark {
  x: number
  y: number
  z: number
  visibility: number
}

interface ServerResponse {
  rep_count?: number
  phase?: string
  score?: number
  feedback?: string
  exercise?: string
  status?: string
  message?: string
  error?: string
}

export default function TrainerPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const initialExercise = location.state?.exercise || 'squat'

  const [isRunning, setIsRunning] = useState(false)
  const [selectedExercise, setSelectedExercise] = useState(initialExercise)
  const [repCount, setRepCount] = useState(0)
  const [phase, setPhase] = useState('READY')
  const [feedback, setFeedback] = useState('Select an exercise and start your camera to begin!')
  const [statusText, setStatusText] = useState('Ready to start')

  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const poseRef = useRef<Pose | null>(null)
  const cameraRef = useRef<Camera | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  const exercises = [
    { id: 'squat', name: 'Squats', icon: '🏋️', color: 'bg-purple-500' },
    { id: 'boxing', name: 'Boxing', icon: '🥊', color: 'bg-pink-500' },
    { id: 'jumping', name: 'Jumping', icon: '🦘', color: 'bg-indigo-500' },
    { id: 'waving', name: 'Waving', icon: '👋', color: 'bg-green-500' }
  ]

  const instructions = {
    squat: [
      'Stand with feet shoulder-width apart',
      'Keep your back straight',
      'Lower your hips until thighs are parallel to ground',
      'Push through heels to return to start'
    ],
    boxing: [
      'Stand in boxing stance (one foot forward)',
      'Keep hands up near face',
      'Extend arm forward for punch',
      'Retract quickly to guard position'
    ],
    waving: [
      'Stand naturally with arms at sides',
      'Raise one or both hands above shoulder',
      'Wave hand side to side',
      'Lower hand back down'
    ],
    jumping: [
      'Stand with feet together',
      'Bend knees slightly',
      'Jump up explosively',
      'Land softly with bent knees'
    ]
  }

  // Initialize MediaPipe
  useEffect(() => {
    const pose = new Pose({
      locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`
      }
    })

    pose.setOptions({
      modelComplexity: 1,
      smoothLandmarks: true,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5
    })

    pose.onResults(onPoseResults)
    poseRef.current = pose

    return () => {
      stopCamera()
    }
  }, [])

  const connectWebSocket = useCallback(() => {
    return new Promise<void>((resolve, reject) => {
      const ws = new WebSocket('ws://localhost:8000/ws/live')

      ws.onopen = () => {
        console.log('WebSocket connected')
        wsRef.current = ws
        resolve()
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        reject(error)
      }

      ws.onmessage = (event) => {
        const data: ServerResponse = JSON.parse(event.data)
        handleServerResponse(data)
      }

      ws.onclose = () => {
        console.log('WebSocket closed')
        wsRef.current = null
      }
    })
  }, [])

  const handleServerResponse = (data: ServerResponse) => {
    if (data.error) {
      console.error('Server error:', data.error)
      return
    }

    if (data.status === 'buffering') {
      setStatusText(data.message || 'Buffering...')
      return
    }

    if (data.rep_count !== undefined) {
      setRepCount(data.rep_count)
    }

    if (data.phase) {
      setPhase(data.phase.toUpperCase())
    }

    if (data.feedback) {
      setFeedback(data.feedback)
    }
  }

  const onPoseResults = useCallback((results: any) => {
    const canvas = canvasRef.current
    const ctx = canvas?.getContext('2d')
    
    if (!canvas || !ctx) return

    ctx.clearRect(0, 0, canvas.width, canvas.height)

    if (results.poseLandmarks) {
      drawPose(ctx, results.poseLandmarks, canvas.width, canvas.height)

      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        const landmarks = results.poseLandmarks.map((lm: PoseLandmark) => ({
          x: lm.x,
          y: lm.y,
          z: lm.z,
          visibility: lm.visibility
        }))

        wsRef.current.send(JSON.stringify({
          landmarks: landmarks,
          exercise: selectedExercise
        }))
      }
    }
  }, [selectedExercise])

  const drawPose = (
    ctx: CanvasRenderingContext2D,
    landmarks: PoseLandmark[],
    width: number,
    height: number
  ) => {
    const connections = [
      [11, 12], [11, 13], [13, 15], [12, 14], [14, 16],
      [11, 23], [12, 24], [23, 24],
      [23, 25], [25, 27], [24, 26], [26, 28],
      [27, 29], [29, 31], [28, 30], [30, 32]
    ]

    ctx.strokeStyle = '#00ff00'
    ctx.lineWidth = 3

    connections.forEach(([start, end]) => {
      const startLm = landmarks[start]
      const endLm = landmarks[end]

      if (startLm.visibility > 0.5 && endLm.visibility > 0.5) {
        ctx.beginPath()
        ctx.moveTo(startLm.x * width, startLm.y * height)
        ctx.lineTo(endLm.x * width, endLm.y * height)
        ctx.stroke()
      }
    })

    ctx.fillStyle = '#ff0000'
    landmarks.forEach(lm => {
      if (lm.visibility > 0.5) {
        ctx.beginPath()
        ctx.arc(lm.x * width, lm.y * height, 5, 0, 2 * Math.PI)
        ctx.fill()
      }
    })
  }

  const startCamera = async () => {
    try {
      setStatusText('Starting camera...')

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720 }
      })

      if (videoRef.current) {
        videoRef.current.srcObject = stream

        await new Promise((resolve) => {
          if (videoRef.current) {
            videoRef.current.onloadedmetadata = resolve
          }
        })

        if (canvasRef.current && videoRef.current) {
          canvasRef.current.width = videoRef.current.videoWidth
          canvasRef.current.height = videoRef.current.videoHeight
        }

        await connectWebSocket()

        const camera = new Camera(videoRef.current, {
          onFrame: async () => {
            if (poseRef.current && videoRef.current) {
              await poseRef.current.send({ image: videoRef.current })
            }
          },
          width: 1280,
          height: 720
        })

        await camera.start()
        cameraRef.current = camera

        setIsRunning(true)
        setStatusText('Running - analyzing your form')
      }
    } catch (error) {
      console.error('Error starting camera:', error)
      setStatusText('Error: Failed to start camera')
      alert('Failed to start camera. Please check permissions.')
    }
  }

  const stopCamera = () => {
    if (cameraRef.current) {
      cameraRef.current.stop()
      cameraRef.current = null
    }

    if (videoRef.current?.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks()
      tracks.forEach(track => track.stop())
      videoRef.current.srcObject = null
    }

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    setIsRunning(false)
    setStatusText('Stopped')
  }

  const resetCount = async () => {
    try {
      await fetch('http://localhost:8000/reset', { method: 'POST' })
      setRepCount(0)
      setPhase('READY')
      setFeedback('Count reset! Continue exercising...')
      setStatusText('Count reset')
    } catch (error) {
      console.error('Error resetting:', error)
    }
  }

  const changeExercise = (exerciseId: string) => {
    setSelectedExercise(exerciseId)
    setRepCount(0)
    setPhase('READY')
    setFeedback(`Ready for ${exerciseId}! Start moving...`)
    setStatusText(`Exercise changed to ${exerciseId}`)

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ exercise: exerciseId }))
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black/30 backdrop-blur-sm border-b border-white/10 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Button 
              variant="ghost" 
              className="text-white hover:bg-white/10"
              onClick={() => navigate('/home')}
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back to Home
            </Button>
            
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${isRunning ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`} />
              <span className="text-white text-sm">{statusText}</span>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Main Video Section */}
          <div className="lg:col-span-2 space-y-6">
            {/* Exercise Selector */}
            <Card className="bg-white/10 backdrop-blur-sm border-white/20">
              <CardContent className="p-4">
                <div className="flex items-center gap-4 overflow-x-auto">
                  {exercises.map((exercise) => (
                    <button
                      key={exercise.id}
                      onClick={() => changeExercise(exercise.id)}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all whitespace-nowrap ${
                        selectedExercise === exercise.id
                          ? `${exercise.color} text-white shadow-lg scale-105`
                          : 'bg-white/10 text-white hover:bg-white/20'
                      }`}
                    >
                      <span className="text-2xl">{exercise.icon}</span>
                      <span className="font-semibold">{exercise.name}</span>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Video Container */}
            <Card className="bg-black border-white/20 overflow-hidden">
              <div className="relative aspect-video bg-black">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  className="w-full h-full object-cover"
                />
                <canvas
                  ref={canvasRef}
                  className="absolute top-0 left-0 w-full h-full"
                />
                
                {!isRunning && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                    <div className="text-center text-white">
                      <VideoOff className="w-16 h-16 mx-auto mb-4 opacity-50" />
                      <p className="text-lg">Camera is off</p>
                      <p className="text-sm opacity-75">Click Start to begin</p>
                    </div>
                  </div>
                )}
              </div>
            </Card>

            {/* Controls */}
            <Card className="bg-white/10 backdrop-blur-sm border-white/20">
              <CardContent className="p-4">
                <div className="flex items-center justify-center gap-4">
                  {!isRunning ? (
                    <Button
                      size="lg"
                      onClick={startCamera}
                      className="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white px-8"
                    >
                      <Play className="w-5 h-5 mr-2" />
                      Start Camera
                    </Button>
                  ) : (
                    <Button
                      size="lg"
                      onClick={stopCamera}
                      variant="destructive"
                      className="px-8"
                    >
                      <Pause className="w-5 h-5 mr-2" />
                      Stop
                    </Button>
                  )}
                  
                  <Button
                    size="lg"
                    onClick={resetCount}
                    variant="outline"
                    className="border-white/30 text-white hover:bg-white/10"
                  >
                    <RotateCcw className="w-5 h-5 mr-2" />
                    Reset
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Stats Sidebar */}
          <div className="space-y-6">
            {/* Rep Counter */}
            <Card className="bg-gradient-to-br from-purple-500 to-pink-500 text-white border-0">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Rep Count
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-6xl font-bold text-center">{repCount}</div>
              </CardContent>
            </Card>

            {/* Phase */}
            <Card className="bg-white/10 backdrop-blur-sm border-white/20 text-white">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-5 h-5" />
                  Current Phase
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-center">{phase}</div>
              </CardContent>
            </Card>

            {/* Feedback */}
            <Card className="bg-white/10 backdrop-blur-sm border-white/20 text-white">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  💬 Live Feedback
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-relaxed">{feedback}</p>
              </CardContent>
            </Card>

            {/* Instructions */}
            <Card className="bg-white/10 backdrop-blur-sm border-white/20 text-white">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  📋 Instructions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  {instructions[selectedExercise as keyof typeof instructions].map((instruction, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-purple-300 mt-0.5">•</span>
                      <span>{instruction}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {/* Tips */}
            <Card className="bg-yellow-500/20 backdrop-blur-sm border-yellow-500/30 text-white">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  💡 Tips
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-1 text-sm">
                  <li>• Position 6-8 feet from camera</li>
                  <li>• Ensure full body is visible</li>
                  <li>• Good lighting helps detection</li>
                  <li>• Move slowly and controlled</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
