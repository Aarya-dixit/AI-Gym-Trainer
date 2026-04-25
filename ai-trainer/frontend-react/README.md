# AI Gym Trainer - Modern React Frontend

A beautiful, modern React + TypeScript + Tailwind CSS frontend for the AI Gym Trainer application with shadcn/ui components and 3D Spline integration.

## 🎨 Features

- **Landing Page**: Beautiful hero section with 3D Spline scene, features showcase, and call-to-action
- **Home Dashboard**: Exercise library, stats tracking, recent activity, and quick start
- **Trainer Page**: Real-time webcam analysis with MediaPipe pose detection
- **Modern UI**: Built with shadcn/ui components and Tailwind CSS
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **3D Integration**: Interactive Spline 3D scenes for enhanced user experience

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend server running on `http://localhost:8000`

### Installation

1. **Install dependencies:**
   ```bash
   cd ai-trainer/frontend-react
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open browser:**
   Navigate to `http://localhost:3000`

## 📦 Project Structure

```
frontend-react/
├── src/
│   ├── components/
│   │   └── ui/              # shadcn/ui components
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── spotlight.tsx
│   │       └── splite.tsx
│   ├── lib/
│   │   └── utils.ts         # Utility functions
│   ├── pages/
│   │   ├── LandingPage.tsx  # Landing/marketing page
│   │   ├── HomePage.tsx     # Dashboard/home page
│   │   └── TrainerPage.tsx  # Training session page
│   ├── App.tsx              # Main app with routing
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```

## 🎯 Pages Overview

### Landing Page (`/`)
- Hero section with 3D Spline scene
- Features showcase
- How it works section
- Benefits and testimonials
- Call-to-action

### Home Page (`/home`)
- User dashboard with stats
- Exercise library with cards
- Quick start button
- Recent activity feed
- Navigation header

### Trainer Page (`/trainer`)
- Live webcam feed with pose detection
- Exercise selector
- Real-time rep counting
- Phase detection
- Live feedback
- Instructions and tips

## 🛠️ Technology Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component library
- **Framer Motion** - Animations
- **Spline** - 3D scenes
- **MediaPipe** - Pose detection
- **React Router** - Navigation
- **Lucide React** - Icons

## 🎨 Customization

### Colors
Edit `tailwind.config.js` and `src/index.css` to customize the color scheme.

### Components
All UI components are in `src/components/ui/` and can be customized.

### 3D Scenes
Replace the Spline scene URL in `LandingPage.tsx`:
```tsx
<SplineScene 
  scene="YOUR_SPLINE_URL_HERE"
  className="w-full h-full"
/>
```

## 🔧 Configuration

### Backend Connection
The app connects to the backend at `http://localhost:8000`. To change this, update:
- WebSocket URL in `TrainerPage.tsx`
- API endpoints in `TrainerPage.tsx`
- Vite proxy in `vite.config.ts`

### Exercise Configuration
Add or modify exercises in:
- `HomePage.tsx` - Exercise library
- `TrainerPage.tsx` - Exercise selector and instructions

## 📱 Responsive Design

The app is fully responsive with breakpoints:
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## 🚀 Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## 🔍 Development Tips

1. **Hot Reload**: Changes are reflected immediately during development
2. **Type Safety**: TypeScript catches errors at compile time
3. **Component Reusability**: Use shadcn/ui components for consistency
4. **Tailwind Classes**: Use Tailwind utility classes for styling
5. **Icons**: Import from `lucide-react` for consistent icons

## 📝 Adding New Components

To add a new shadcn/ui component:

1. Create the component in `src/components/ui/`
2. Use the `cn()` utility for className merging
3. Follow the existing component patterns
4. Export from the component file

## 🐛 Troubleshooting

### Camera not working
- Check browser permissions
- Ensure HTTPS or localhost
- Verify MediaPipe CDN is accessible

### WebSocket connection failed
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify WebSocket endpoint

### 3D scene not loading
- Check internet connection (Spline CDN)
- Verify Spline scene URL is valid
- Check browser console for errors

## 📄 License

This project is part of the AI Gym Trainer application.

## 🤝 Contributing

Contributions are welcome! Please follow the existing code style and component patterns.
