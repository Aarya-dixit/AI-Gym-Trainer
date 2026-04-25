# Setup Instructions - Modern React Frontend

## 🎯 Overview

This is a modern React + TypeScript + Tailwind CSS frontend for the AI Gym Trainer application. It includes:
- Landing page with 3D Spline integration
- Dashboard with exercise library
- Real-time training page with webcam

## ⚡ Quick Setup (3 Steps)

### Step 1: Install Node.js

Download and install Node.js 18+ from: https://nodejs.org/

Verify installation:
```bash
node --version
npm --version
```

### Step 2: Install Dependencies

```bash
cd ai-trainer/frontend-react
npm install
```

This will install all required packages (~2-3 minutes).

### Step 3: Start Development Server

```bash
npm run dev
```

Open browser to: **http://localhost:3000**

## 📦 What Gets Installed

The `npm install` command installs:

### Core Dependencies
- `react` & `react-dom` - React framework
- `react-router-dom` - Page routing
- `typescript` - Type safety

### UI & Styling
- `tailwindcss` - Utility-first CSS
- `lucide-react` - Icon library
- `framer-motion` - Animations
- `clsx` & `tailwind-merge` - Class utilities

### 3D & Media
- `@splinetool/react-spline` - 3D scenes
- `@mediapipe/pose` - Pose detection
- `@mediapipe/camera_utils` - Camera utilities

### Build Tools
- `vite` - Fast build tool
- `@vitejs/plugin-react` - React support

Total size: ~500MB (includes all dependencies)

## 🚀 Available Scripts

```bash
# Start development server (with hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## 🔧 Configuration Files

- `package.json` - Dependencies and scripts
- `tsconfig.json` - TypeScript configuration
- `vite.config.ts` - Vite build configuration
- `tailwind.config.js` - Tailwind CSS configuration
- `postcss.config.js` - PostCSS configuration

## 📁 Project Structure

```
src/
├── components/ui/       # Reusable UI components
│   ├── button.tsx
│   ├── card.tsx
│   ├── spotlight.tsx
│   └── splite.tsx
├── lib/
│   └── utils.ts        # Utility functions
├── pages/
│   ├── LandingPage.tsx # Landing page
│   ├── HomePage.tsx    # Dashboard
│   └── TrainerPage.tsx # Training page
├── App.tsx             # Main app with routing
├── main.tsx            # Entry point
└── index.css           # Global styles
```

## 🌐 Backend Connection

The frontend connects to the backend at:
- **HTTP**: `http://localhost:8000`
- **WebSocket**: `ws://localhost:8000/ws/live`

Make sure the backend is running before starting the frontend!

## 🐛 Troubleshooting

### "npm: command not found"
Install Node.js from https://nodejs.org/

### "Cannot find module"
Run `npm install` again

### "Port 3000 already in use"
```bash
npm run dev -- --port 3001
```

### Camera not working
- Allow camera permission in browser
- Use Chrome for best compatibility
- Ensure no other app is using camera

### Backend connection failed
- Start backend: `python backend/main.py`
- Check backend is on port 8000
- Verify no firewall blocking

## 📚 Next Steps

1. ✅ Complete setup (you're here!)
2. ✅ Start backend server
3. ✅ Start frontend server
4. ✅ Open http://localhost:3000
5. ✅ Explore the application

## 📖 Additional Documentation

- **GETTING_STARTED_NEW_UI.md** - Quick start guide
- **MODERN_UI_SETUP.md** - Detailed setup
- **README.md** - Technical documentation
- **UI_COMPARISON.md** - Old vs New comparison

## 🎉 You're Ready!

Once setup is complete, you can:
- Browse the landing page
- Explore the exercise library
- Start training with AI guidance
- Customize the application

Enjoy your modern AI Gym Trainer! 💪
