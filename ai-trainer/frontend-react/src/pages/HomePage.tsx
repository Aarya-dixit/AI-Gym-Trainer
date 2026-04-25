import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dumbbell, Activity, TrendingUp, History, Settings, Play, User } from 'lucide-react'

export default function HomePage() {
  const navigate = useNavigate()

  const exercises = [
    {
      id: 'squat',
      name: 'Squats',
      icon: '🏋️',
      description: 'Lower body strength training',
      difficulty: 'Beginner',
      duration: '10-15 min',
      calories: '50-80',
      image: 'https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=400&h=300&fit=crop'
    },
    {
      id: 'boxing',
      name: 'Boxing',
      icon: '🥊',
      description: 'Upper body cardio workout',
      difficulty: 'Intermediate',
      duration: '15-20 min',
      calories: '100-150',
      image: 'https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=400&h=300&fit=crop'
    },
    {
      id: 'jumping',
      name: 'Jumping Jacks',
      icon: '🦘',
      description: 'Full body cardio exercise',
      difficulty: 'Beginner',
      duration: '5-10 min',
      calories: '40-60',
      image: 'https://images.unsplash.com/photo-1518611012118-696072aa579a?w=400&h=300&fit=crop'
    },
    {
      id: 'waving',
      name: 'Arm Waves',
      icon: '👋',
      description: 'Shoulder mobility exercise',
      difficulty: 'Beginner',
      duration: '5-8 min',
      calories: '20-30',
      image: 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=300&fit=crop'
    }
  ]

  const stats = [
    { label: 'Total Workouts', value: '24', icon: Activity, color: 'bg-purple-500' },
    { label: 'Total Reps', value: '1,234', icon: TrendingUp, color: 'bg-pink-500' },
    { label: 'Calories Burned', value: '2,450', icon: Dumbbell, color: 'bg-indigo-500' },
    { label: 'Streak Days', value: '7', icon: History, color: 'bg-green-500' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-50 backdrop-blur-sm bg-white/90">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Dumbbell className="w-8 h-8 text-purple-600" />
              <span className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                AI Gym Trainer
              </span>
            </div>
            
            <nav className="hidden md:flex items-center gap-6">
              <Button variant="ghost" onClick={() => navigate('/home')}>
                Home
              </Button>
              <Button variant="ghost">
                <History className="w-4 h-4 mr-2" />
                History
              </Button>
              <Button variant="ghost">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </Button>
              <Button variant="outline" className="gap-2">
                <User className="w-4 h-4" />
                Profile
              </Button>
            </nav>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Welcome back! 💪</h1>
          <p className="text-gray-600 text-lg">Ready to crush your workout today?</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
          {stats.map((stat, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <div className={`w-10 h-10 ${stat.color} rounded-lg flex items-center justify-center`}>
                    <stat.icon className="w-5 h-5 text-white" />
                  </div>
                </div>
                <div className="text-3xl font-bold mb-1">{stat.value}</div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Quick Start */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Quick Start</h2>
          <Card className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:shadow-xl transition-shadow cursor-pointer"
                onClick={() => navigate('/trainer')}>
            <CardContent className="p-8">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-2xl font-bold mb-2">Start Training Session</h3>
                  <p className="text-purple-100 mb-4">
                    Jump right into your workout with AI-powered guidance
                  </p>
                  <Button size="lg" className="bg-white text-purple-600 hover:bg-gray-100">
                    <Play className="w-5 h-5 mr-2" />
                    Begin Workout
                  </Button>
                </div>
                <div className="hidden lg:block text-8xl">🏃‍♂️</div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Exercise Library */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold">Exercise Library</h2>
            <Button variant="outline">View All</Button>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {exercises.map((exercise) => (
              <Card 
                key={exercise.id} 
                className="hover:shadow-xl transition-all hover:-translate-y-1 cursor-pointer overflow-hidden"
                onClick={() => navigate('/trainer', { state: { exercise: exercise.id } })}
              >
                <div className="relative h-48 overflow-hidden">
                  <img 
                    src={exercise.image} 
                    alt={exercise.name}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-2 right-2 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-semibold">
                    {exercise.difficulty}
                  </div>
                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
                    <div className="text-4xl mb-2">{exercise.icon}</div>
                  </div>
                </div>
                
                <CardHeader>
                  <CardTitle>{exercise.name}</CardTitle>
                  <CardDescription>{exercise.description}</CardDescription>
                </CardHeader>
                
                <CardContent>
                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <Activity className="w-4 h-4" />
                      {exercise.duration}
                    </div>
                    <div className="flex items-center gap-1">
                      🔥 {exercise.calories} cal
                    </div>
                  </div>
                  
                  <Button className="w-full mt-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
                    Start Exercise
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div>
          <h2 className="text-2xl font-bold mb-4">Recent Activity</h2>
          <Card>
            <CardContent className="p-6">
              <div className="space-y-4">
                {[
                  { exercise: 'Squats', reps: 45, time: '2 hours ago', quality: 'Excellent' },
                  { exercise: 'Boxing', reps: 120, time: 'Yesterday', quality: 'Good' },
                  { exercise: 'Jumping Jacks', reps: 60, time: '2 days ago', quality: 'Excellent' }
                ].map((activity, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                        <Activity className="w-6 h-6 text-purple-600" />
                      </div>
                      <div>
                        <div className="font-semibold">{activity.exercise}</div>
                        <div className="text-sm text-gray-600">{activity.time}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold">{activity.reps} reps</div>
                      <div className={`text-sm ${activity.quality === 'Excellent' ? 'text-green-600' : 'text-blue-600'}`}>
                        {activity.quality}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
