<!-- @format -->

# 🤖 AI Chat Integration Guide

## Overview

The ChatAssistant now integrates with your teammate's AI API to provide intelligent tree planting location recommendations with interactive map display.

## 🔄 Workflow

1. **User asks question** in chat (e.g., "Find me the best tree locations")
2. **Frontend sends request** to your AI API endpoint
3. **AI API returns coordinates** with location data
4. **Chat displays response** with "Show on Map" button
5. **User clicks button** → Map shows AI locations with custom icons
6. **User clicks AI icon** → Detailed popup with location info

## 🛠️ API Integration

### Endpoint Configuration

```bash
# Set your API endpoint in .env file
REACT_APP_AI_ENDPOINT=http://localhost:8000/api/ai-query
```

### Expected API Request Format

```json
{
  "query": "Find me the best tree planting locations",
  "context": {
    "realData": { "totalLocations": 114982, "freshLocations": 13882 },
    "currentView": "fullscreen",
    "timestamp": "2024-11-22T22:30:00.000Z",
    "source": "forestry-chat"
  }
}
```

### Expected API Response Format

```json
{
  "message": "I found 3 optimal locations based on your criteria...",
  "coordinates": [
    {
      "lat": 49.1427,
      "lng": 9.2109,
      "score": 95,
      "info": "Perfect city center location with high heat priority",
      "heat_score": 98,
      "spatial_score": 90,
      "social_score": 100,
      "recommended_species": "Ahornblättrige Platane",
      "benefits": "Near schools, high foot traffic"
    }
  ],
  "metadata": {
    "query_time": "2024-11-22T22:30:00.000Z",
    "confidence": 0.95,
    "analysis_type": "heat_priority"
  }
}
```

## 🗺️ Map Display Features

### AI Location Markers

- **Custom green pulsing icons** with AI symbol
- **Animated appearance** to grab attention
- **Hover effects** and smooth animations

### Interactive Popups

- **AI branding** with gradient background
- **Detailed location info** (score, coordinates, species)
- **Metadata display** (heat/spatial/social scores)
- **Professional styling** with proper typography

### Layer Control

- **AI Locations toggle** in map controls
- **Live counter** showing number of AI locations
- **Highlighted section** to distinguish from other layers

## 🧪 Demo Mode (For Testing)

Currently includes demo responses for testing. Try these phrases:

- "show me locations"
- "find locations"
- "best spots"
- "ai locations"
- "recommend locations"

Demo returns 3 sample coordinates around Heilbronn city center.

## 🔧 Implementation Details

### Files Modified

- `ChatAssistant.jsx` - Added AI integration and coordinate handling
- `RealMapView.jsx` - Added AI marker rendering and popups
- `MainLayout.jsx` - Added coordinate state management
- `aiService.js` - New service for API communication
- `ChatAssistant.css` - Styling for buttons and markers

### Key Functions

- `aiService.queryAI()` - Sends requests to your API
- `handleShowCoordinates()` - Displays coordinates on map
- `MessageContent` - Renders coordinate buttons in chat
- AI marker rendering with custom icons and popups

## 🚀 Production Setup

1. **Replace demo endpoint** with your actual API URL
2. **Remove demo mode** functions from `aiService.js`
3. **Add error handling** for your specific API responses
4. **Configure authentication** if needed
5. **Test with real data** from your AI model

## 📱 User Experience

### Chat Flow

1. User types natural language query
2. Loading indicator shows AI is processing
3. Response appears with coordinate button
4. Click button switches to map view
5. AI locations appear with pulsing animations
6. Click markers for detailed information

### Visual Feedback

- ✅ Loading spinners during AI processing
- ✅ Coordinate buttons with hover effects
- ✅ Animated AI markers on map
- ✅ Professional popups with detailed info
- ✅ Layer controls for easy toggling

## 🔗 Ready for Integration!

The frontend is now ready to connect to your AI API. Just:

1. Set `REACT_APP_AI_ENDPOINT` to your API URL
2. Ensure your API returns the expected JSON format
3. Test with real queries and coordinates

The system will automatically fall back to local responses if your API is unavailable.
