<!-- @format -->

# QuestAI - Interactive City Explorer

A modern React frontend for an interactive city exploration platform with gamified quests, real-time maps, and AI-powered assistance.

## Features

- 🗺️ **Interactive Map**: Real-time location tracking with custom markers and route visualization
- 🎯 **Quest System**: Gamified exploration with checkpoints, challenges, and stories
- 🤖 **AI Assistant**: Personal guide with chat interface for tips and information
- 🎨 **Modern UI**: Dark theme with smooth animations and glass morphism effects
- 📱 **Responsive Design**: Optimized for desktop and mobile devices

## Tech Stack

- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Smooth animations and transitions
- **React Leaflet** - Interactive maps
- **Lucide React** - Beautiful icons

## Getting Started

1. Install dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
src/
├── components/
│   ├── Header.jsx          # Top navigation bar
│   ├── Sidebar.jsx         # Left navigation menu
│   ├── MapView.jsx         # Interactive map component
│   ├── QuestPanel.jsx      # Quest details sidebar
│   └── ChatAssistant.jsx   # AI chat interface
├── App.jsx                 # Main application component
├── main.jsx               # Application entry point
└── index.css              # Global styles and Tailwind imports
```

## Color Scheme

- **Primary**: Bright lime/yellow accent (#CCFF00)
- **Background**: Dark grays (#0a0a0a, #1a1a1a, #2a2a2a)
- **Glass Effects**: Semi-transparent overlays with backdrop blur
- **Text**: White and gray variants for hierarchy

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Customization

The app is designed to be easily customizable:

- **Colors**: Modify `tailwind.config.js` for theme colors
- **Map**: Update coordinates and locations in `MapView.jsx`
- **Content**: Add new quests and locations in the component data
- **Styling**: Use Tailwind utilities or add custom CSS in `index.css`
