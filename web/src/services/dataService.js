/** @format */

// Data service to load real GeoJSON and CSV data
class DataService {
  constructor() {
    this.cache = new Map();
  }

  async loadGeoJSON(filename) {
    if (this.cache.has(filename)) {
      return this.cache.get(filename);
    }

    try {
      const response = await fetch(`/data/${filename}`);
      if (!response.ok) {
        throw new Error(`Failed to load ${filename}`);
      }
      const data = await response.json();
      this.cache.set(filename, data);
      return data;
    } catch (error) {
      console.error(`Error loading ${filename}:`, error);
      return { type: "FeatureCollection", features: [] };
    }
  }

  async loadCSV(filename) {
    if (this.cache.has(filename)) {
      return this.cache.get(filename);
    }

    try {
      const response = await fetch(`/data/${filename}`);
      if (!response.ok) {
        throw new Error(`Failed to load ${filename}`);
      }
      const text = await response.text();
      const data = this.parseCSV(text);
      this.cache.set(filename, data);
      return data;
    } catch (error) {
      console.error(`Error loading ${filename}:`, error);
      return [];
    }
  }

  parseCSV(text) {
    const lines = text.trim().split("\n");
    const headers = lines[0].split(",");

    return lines.slice(1).map((line) => {
      const values = line.split(",");
      const obj = {};
      headers.forEach((header, index) => {
        obj[header] = values[index];
      });
      return obj;
    });
  }

  // Load essential map layers only (fast loading)
  async loadMapLayers() {
    // Only load small, essential files initially
    const [topLocations, topLocationsFresh, heatPriorityZones, waterBodies] =
      await Promise.all([
        this.loadGeoJSON("top_100.geojson"), // 29KB
        this.loadGeoJSON("top_100_fresh.geojson"), // 37KB
        this.loadGeoJSON("heat_priority_zones.geojson"), // 22KB
        this.loadGeoJSON("water_bodies.geojson"), // 664KB
      ]);

    return {
      topLocations,
      topLocationsFresh,
      heatPriorityZones,
      waterBodies,
      // Large files loaded on demand
      allLocations: null,
      buildingsFresh: null,
      fire: null,
      roadsFresh: null,
      trees: null,
      scoredLocationsFresh: null,
    };
  }

  // Load large datasets on demand
  async loadLargeDataset(datasetName) {
    const datasets = {
      allLocations: "all_locations.geojson", // 34MB - HUGE!
      scoredLocationsFresh: "scored_locations_fresh.geojson", // 9.7MB
      buildingsFresh: "exclusion_buildings_fresh.geojson", // 2.2MB
      roadsFresh: "exclusion_roads_fresh.geojson", // 1.8MB
      fire: "exclusion_fire.geojson", // 1.3MB
      trees: "exclusion_trees.geojson", // 6.7MB
    };

    if (datasets[datasetName]) {
      console.log(
        `Loading large dataset: ${datasetName} (${datasets[datasetName]})`
      );
      return await this.loadGeoJSON(datasets[datasetName]);
    }
    return null;
  }

  // Load statistics data - FAST loading with cached values
  async loadStatistics() {
    try {
      // Only load small files for statistics - avoid 34MB + 9.7MB monsters!
      const [topLocations, topLocationsFresh] = await Promise.all([
        this.loadGeoJSON("top_100.geojson"), // 29KB - fast!
        this.loadGeoJSON("top_100_fresh.geojson"), // 37KB - fast!
      ]);

      // Use pre-calculated values to avoid loading huge files
      const topCount = topLocations.features?.length || 0;
      const topFreshCount = topLocationsFresh.features?.length || 0;

      // Calculate average scores from top locations
      const topScores =
        topLocations.features?.map((f) => f.properties.final_score) || [];
      const averageScore =
        topScores.length > 0
          ? (
              topScores.reduce((sum, score) => sum + score, 0) /
              topScores.length
            ).toFixed(1)
          : 0;

      // Find highest score
      const topScore =
        topScores.length > 0 ? Math.max(...topScores).toFixed(1) : 0;

      // Use pre-calculated values for performance
      const stats = {
        totalLocations: 114982, // From your analysis - no need to load 34MB file!
        freshLocations: 13882, // From your fresh analysis - no need to load 9.7MB file!
        topLocations: topCount,
        topFreshLocations: topFreshCount,
        plantableArea: "11.50 km²",
        freshPlantableArea: "1.39 km²",
        topScore,
        averageScore,
        co2Reduction: "305t", // Pre-calculated
        perfectLocations: topScores.filter((score) => score >= 80).length,
      };

      return {
        stats,
        rawData: {
          topLocations,
          topLocationsFresh,
        },
      };
    } catch (error) {
      console.error("Error loading statistics:", error);
      // Return fallback stats
      return {
        stats: {
          totalLocations: 114982,
          freshLocations: 13882,
          topLocations: 100,
          topFreshLocations: 100,
          plantableArea: "11.50 km²",
          freshPlantableArea: "1.39 km²",
          topScore: 83,
          averageScore: 65,
          co2Reduction: "305t",
          perfectLocations: 25,
        },
        rawData: null,
      };
    }
  }

  // Get layer styling for available data
  getLayerStyle(layerType) {
    const styles = {
      allLocations: {
        color: "#FFD23F",
        fillColor: "#FFD23F",
        fillOpacity: 0.6,
        weight: 2,
        radius: 4,
      },
      buildingsFresh: {
        color: "#ff4444",
        fillColor: "#ff4444",
        fillOpacity: 0.4,
        weight: 1,
      },
      fire: {
        color: "#ff8800",
        fillColor: "#ff8800",
        fillOpacity: 0.3,
        weight: 2,
      },
      roadsFresh: {
        color: "#888888",
        fillColor: "#888888",
        fillOpacity: 0.4,
        weight: 2,
      },
      trees: {
        color: "#8B4513",
        fillColor: "#8B4513",
        fillOpacity: 0.4,
        weight: 1,
      },
      heatPriorityZones: {
        color: "#ff0000",
        fillColor: "#ff0000",
        fillOpacity: 0.3,
        weight: 2,
      },
      scoredLocationsFresh: {
        color: "#CCFF00",
        fillColor: "#CCFF00",
        fillOpacity: 0.8,
        weight: 2,
        radius: 6,
      },
      topLocationsFresh: {
        color: "#ADFF2F",
        fillColor: "#ADFF2F",
        fillOpacity: 0.9,
        weight: 3,
        radius: 8,
      },
      topLocations: {
        color: "#DC143C",
        fillColor: "#DC143C",
        fillOpacity: 0.9,
        weight: 4,
        radius: 10,
      },
      waterBodies: {
        color: "#0066cc",
        fillColor: "#0066cc",
        fillOpacity: 0.5,
        weight: 1,
      },
    };

    return styles[layerType] || styles.allLocations;
  }

  // Get dynamic styling based on feature properties
  getFeatureStyle(feature, layerType) {
    const baseStyle = this.getLayerStyle(layerType);

    // For scored locations, color by score
    if (feature.properties && feature.properties.final_score !== undefined) {
      const score = feature.properties.final_score;
      let color = "#FFD23F"; // Default yellow

      if (score >= 80) color = "#DC143C"; // Red for high scores
      else if (score >= 60) color = "#FF6B35"; // Orange for medium-high
      else if (score >= 40) color = "#CCFF00"; // Yellow-green for medium
      else color = "#90EE90"; // Light green for low

      return {
        ...baseStyle,
        color,
        fillColor: color,
      };
    }

    return baseStyle;
  }
}

export default new DataService();
