<!-- @format -->

# 🤖 Backend Integration Guide

## Quick Setup for Your Friend's API

Your web application is **ready to connect** to your friend's backend! Here's what they need to know:

### 1. API Endpoint Requirements

**URL:** Any endpoint your friend prefers (we'll configure it)
**Method:** POST
**Content-Type:** application/json

### 2. Request Format

```json
{
  "query": "Find me the best locations in Heilbronn"
}
```

### 3. Expected Response Format

```json
{
  "summary_of_results": "Here are the best places to plant trees near Heilbronn:",
  "locations": [
    {
      "summary": "Location details with score, species, cooling benefits...",
      "latitude": 49.13220684039029,
      "longitude": 9.225236784881375
    }
  ],
  "tip": "Did you know that native tree species usually have higher survival rates?"
}
```

### 4. Configuration Steps

1. **Get the API URL from your friend**
2. **Update your `.env` file:**
   ```bash
   REACT_APP_AI_ENDPOINT=https://your-friends-api.com/api/endpoint
   ```
3. **Restart your dev server:** `npm run dev`
4. **Test the chat assistant!**

### 5. Testing

- **Demo Mode:** Works right now with realistic test data
- **Test Page:** Open `http://localhost:5173/chat-test.html`
- **Main App:** Chat assistant button in bottom-right corner

### 6. What's Already Working

✅ Chat UI with floating assistant  
✅ Message handling and display  
✅ Location mapping integration  
✅ Error handling and fallbacks  
✅ Demo mode for testing  
✅ Response format processing

### 7. Example Queries That Work

- "Find me the best locations in Heilbronn"
- "Show me 2 tree planting spots"
- "What about postal code 74072?"
- "Tell me about heat islands"

### 8. Current Status

🟢 **Ready for Integration** - Just need your friend's API URL!

The chat assistant will automatically:

- Send user queries to the backend
- Process the responses
- Show locations on the map
- Handle errors gracefully
- Fall back to demo mode if needed

---

**Need help?** The integration is plug-and-play - just update the URL and you're good to go! 🚀
