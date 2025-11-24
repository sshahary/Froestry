/** @format */

// AI Location Service - Connects to your teammate's API
class AILocationService {
  constructor() {
    // Your teammate's REAL API endpoint
    this.apiEndpoint =
      import.meta.env.VITE_AI_ENDPOINT ||
      "http://localhost:8007/get_tree_locations";
  }

  // Send user query to backend
  async getTreeLocations(userQuery) {
    try {
      console.log("🤖 Sending query to AI backend:", userQuery);

      const response = await fetch(this.apiEndpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: userQuery }),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      const apiData = await response.json();
      console.log("✅ Received AI response:", apiData);

      return this.processAPIResponse(apiData);
    } catch (error) {
      console.error("❌ AI API Error:", error);

      // ❗ No demo fallback — return empty error result
      return {
        success: false,
        message: "AI service unavailable. Please try again.",
        locations: [],
      };
    }
  }

  // Parse backend response
  processAPIResponse(apiData) {
    // Expected format from backend:
    // {
    //   "summary_of_results": "...",
    //   "locations": [
    //     {
    //       "summary": "...",
    //       "latitude": ...,
    //       "longitude": ...
    //     }
    //   ],
    //   "tip": "..."
    // }

    const message = apiData.summary_of_results || "AI found locations for you!";
    const tip = apiData.tip
      ? `<br><br>💡 <strong>Tip:</strong> ${apiData.tip}`
      : "";

    // Build final response object
    return {
      success: true,
      message: message + tip,
      locations: (apiData.locations || []).map((location, index) => {
        const summary = location.summary || "";

        // Parse numeric score if present
        const scoreMatch = summary.match(/(?:Final score:|score)\s*(\d+)/i);
        const score = scoreMatch ? Number(scoreMatch[1]) : 90;

        // Parse species
        const speciesMatch = summary.match(
          /(?:Recommended species:|species:)\s*([^(]+)/i
        );
        const species = speciesMatch ? speciesMatch[1].trim() : "";

        // Parse cooling benefit
        const coolingMatch = summary.match(/([-−]\d+\.?\d*°C)/);
        const cooling = coolingMatch ? coolingMatch[1] : "";

        return {
          id: `ai_${Date.now()}_${index}`,
          lat: location.latitude,
          lng: location.longitude,
          score: score,
          info: summary.split("\n")[0] || "AI recommended location",
          fullSummary: summary,
          details: {
            heatScore: 100,
            spatialScore: 100,
            socialScore: 100,
            maintenanceScore: 100,
            species,
            cooling,
            benefits:
              "Shade, cooling effect, improved air quality, improved microclimate",
          },
        };
      }),
    };
  }
}

export default new AILocationService();
