/** @format */

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  MapContainer,
  TileLayer,
  GeoJSON,
  Marker,
  Popup,
  ImageOverlay,
} from "react-leaflet";
import L from "leaflet";
import { Layers, Info, Eye, EyeOff } from "lucide-react";
import { useNavigate } from "react-router-dom";
import dataService from "../services/dataService";

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

const CompleteMap = ({ realData }) => {
  const navigate = useNavigate();
  const [showLegend, setShowLegend] = useState(true);
  const [heatMapBounds, setHeatMapBounds] = useState(null);
  const [layerVisibility, setLayerVisibility] = useState({
    // Heat map
    heatMap: true,
    // Exclusion layers
    buildings: true,
    buildingsFresh: false,
    roads: true,
    roadsFresh: false,
    trees: true,
    fire: true,
    water: true,
    exclusionCombined: false,
    exclusionCombinedFresh: false,

    // Green spaces and plantable areas
    greenSpaces: true,
    plantable: true,
    plantableFresh: true,

    // Location layers
    topLocations: true,
    topLocationsFresh: false,
    topEnhanced: false,
    scoredLocationsAll: false,
    scoredLocationsAllEnhanced: false,
    scoredLocationsFresh: false,
    scoredLocationsFreshEnhanced: false,
    topWithCoordinates: false,
  });

  // Load heat map bounds
  useEffect(() => {
    fetch("/data/heat_map_bounds.json")
      .then((response) => response.json())
      .then((data) => setHeatMapBounds(data))
      .catch((error) =>
        console.error("Failed to load heat map bounds:", error)
      );
  }, []);

  const loading = !realData;

  // Heilbronn coordinates and bounds
  const center = [49.1427, 9.2109];
  const bounds = [
    [49.12, 9.18],
    [49.17, 9.25],
  ];

  // Enhanced styles for better visibility
  const getEnhancedStyle = (layerType) => {
    const baseStyle = dataService.getLayerStyle(layerType);
    return {
      ...baseStyle,
      weight: Math.max(baseStyle.weight || 1, 2),
      fillOpacity: Math.max(baseStyle.fillOpacity || 0.3, 0.6),
      opacity: 1,
    };
  };

  // Create custom marker for top locations
  const createLocationMarker = (feature) => {
    const score = feature.properties.final_score || 100;
    const color =
      score === 100 ? "#CCFF00" : score >= 95 ? "#FF6B35" : "#FFD23F";

    return L.divIcon({
      className: "custom-marker",
      html: `
        <div style="
          width: 20px;
          height: 20px;
          background-color: ${color};
          border: 3px solid white;
          border-radius: 50%;
          box-shadow: 0 3px 6px rgba(0,0,0,0.4);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: 10px;
          color: ${color === "#CCFF00" ? "#000" : "#fff"};
        ">
          ${Math.round(score)}
        </div>
      `,
      iconSize: [20, 20],
      iconAnchor: [10, 10],
    });
  };

  // Get real statistics
  const getStats = () => {
    if (!realData?.statistics?.stats) {
      return {
        totalLocations: "Loading...",
        freshLocations: "Loading...",
        plantableArea: "Loading...",
        co2Reduction: "Loading...",
      };
    }

    const stats = realData.statistics.stats;
    return {
      totalLocations: stats.totalLocations?.toLocaleString() || "0",
      freshLocations: stats.freshLocations?.toLocaleString() || "0",
      plantableArea: stats.plantableArea || "0 km²",
      co2Reduction: stats.co2Reduction || "0t",
    };
  };

  const currentStats = getStats();

  const toggleLayer = (layerName) => {
    setLayerVisibility((prev) => ({
      ...prev,
      [layerName]: !prev[layerName],
    }));
  };

  return (
    <div className='h-full bg-gray-900 text-white relative'>
      {/* Compact Control Panel */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className='absolute top-4 right-4 z-[1000] flex flex-col space-y-2'>
        {/* Main Stats Display */}
        <div className='bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-3 text-white text-sm'>
          <div className='flex items-center space-x-2 mb-2'>
            <span>🌳</span>
            <span className='font-bold text-lime-400'>Heilbronn Trees</span>
          </div>
          {loading ? (
            <div className='text-xs'>🔄 Loading...</div>
          ) : realData ? (
            <div className='space-y-1 text-xs'>
              <div>📍 {currentStats.totalLocations} locations</div>
              <div>✅ {currentStats.freshLocations} verified</div>
              <div>
                🗺️{" "}
                {realData.mapLayers
                  ? Object.keys(realData.mapLayers).length
                  : 0}{" "}
                layers
              </div>
            </div>
          ) : (
            <div className='text-xs text-red-400'>❌ Load failed</div>
          )}
        </div>

        {/* Layer Toggle Buttons */}
        <div className='bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-3'>
          <div className='text-white text-xs font-bold mb-2'>Quick Toggles</div>
          <div className='grid grid-cols-2 gap-1'>
            {[
              { key: "heatMap", label: "🔥", title: "Heat Map" },
              { key: "buildings", label: "🏢", title: "Buildings" },
              { key: "roads", label: "🛣️", title: "Roads" },
              { key: "trees", label: "🌳", title: "Trees" },
              { key: "water", label: "🌊", title: "Water" },
              { key: "plantable", label: "✅", title: "Plantable" },
              { key: "topLocations", label: "🎯", title: "Top Spots" },
              { key: "greenSpaces", label: "🌿", title: "Green Areas" },
            ].map((layer) => (
              <button
                key={layer.key}
                onClick={() => toggleLayer(layer.key)}
                title={layer.title}
                className={`p-2 rounded text-xs transition-all ${
                  layerVisibility[layer.key]
                    ? "bg-lime-400 text-black"
                    : "bg-white/20 text-white hover:bg-white/30"
                }`}>
                {layer.label}
              </button>
            ))}
          </div>
        </div>

        {/* Advanced Controls */}
        <div className='bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-3'>
          <div className='text-white text-xs font-bold mb-2'>Advanced</div>
          <div className='space-y-1'>
            <button
              onClick={() => setShowLegend(!showLegend)}
              className='w-full p-2 bg-white/20 hover:bg-white/30 rounded text-xs text-white transition-all'>
              {showLegend ? "🔽 Hide Details" : "🔼 Show Details"}
            </button>
            <button
              onClick={() => {
                // Toggle all exclusions
                const exclusionLayers = [
                  "buildings",
                  "roads",
                  "trees",
                  "fire",
                  "water",
                ];
                const allVisible = exclusionLayers.every(
                  (layer) => layerVisibility[layer]
                );
                exclusionLayers.forEach((layer) => {
                  setLayerVisibility((prev) => ({
                    ...prev,
                    [layer]: !allVisible,
                  }));
                });
              }}
              className='w-full p-2 bg-white/20 hover:bg-white/30 rounded text-xs text-white transition-all'>
              🚫 Toggle Exclusions
            </button>
            <button
              onClick={() => {
                // Toggle all location layers
                const locationLayers = [
                  "topLocations",
                  "topEnhanced",
                  "topWithCoordinates",
                ];
                const allVisible = locationLayers.every(
                  (layer) => layerVisibility[layer]
                );
                locationLayers.forEach((layer) => {
                  setLayerVisibility((prev) => ({
                    ...prev,
                    [layer]: !allVisible,
                  }));
                });
              }}
              className='w-full p-2 bg-white/20 hover:bg-white/30 rounded text-xs text-white transition-all'>
              📍 Toggle Locations
            </button>
          </div>
        </div>
      </motion.div>

      {/* Detailed Legend (Collapsible) */}
      {showLegend && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className='absolute top-4 left-4 z-[1000] bg-white/95 backdrop-blur-md rounded-xl p-4 border border-white/20 max-w-xs'>
          <div className='text-gray-800 space-y-3'>
            <div>
              <h4 className='font-bold text-sm mb-1'>🔥 Heat Priority</h4>
              <div className='space-y-1 text-xs'>
                <div className='flex items-center space-x-2'>
                  <div className='w-3 h-3 bg-red-500 rounded'></div>
                  <span>Extreme (95-100)</span>
                </div>
                <div className='flex items-center space-x-2'>
                  <div className='w-3 h-3 bg-orange-500 rounded'></div>
                  <span>High (70-95)</span>
                </div>
                <div className='flex items-center space-x-2'>
                  <div className='w-3 h-3 bg-yellow-500 rounded'></div>
                  <span>Medium (40-70)</span>
                </div>
                <div className='flex items-center space-x-2'>
                  <div className='w-3 h-3 bg-green-400 rounded'></div>
                  <span>Low (0-40)</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className='font-bold text-sm mb-1'>🚫 Exclusions</h4>
              <div className='grid grid-cols-2 gap-1 text-xs'>
                <div className='flex items-center space-x-1'>
                  <div className='w-2 h-2 bg-red-600 rounded'></div>
                  <span>Buildings</span>
                </div>
                <div className='flex items-center space-x-1'>
                  <div className='w-2 h-2 bg-gray-600 rounded'></div>
                  <span>Roads</span>
                </div>
                <div className='flex items-center space-x-1'>
                  <div className='w-2 h-2 bg-amber-700 rounded'></div>
                  <span>Trees</span>
                </div>
                <div className='flex items-center space-x-1'>
                  <div className='w-2 h-2 bg-blue-600 rounded'></div>
                  <span>Water</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className='font-bold text-sm mb-1'>✅ Plantable</h4>
              <div className='space-y-1 text-xs'>
                <div className='flex items-center space-x-2'>
                  <div className='w-3 h-3 bg-lime-400 rounded'></div>
                  <span>Available Areas</span>
                </div>
                <div className='flex items-center space-x-2'>
                  <div className='w-3 h-3 bg-green-600 rounded'></div>
                  <span>Green Spaces</span>
                </div>
              </div>
            </div>

            <div className='border-t pt-2'>
              <div className='text-xs'>
                <div className='font-bold text-green-600'>
                  {currentStats.plantableArea}
                </div>
                <div className='text-gray-600'>
                  {currentStats.freshLocations} verified
                </div>
                <div className='text-orange-600'>
                  {currentStats.co2Reduction}/year CO₂
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Compact Status Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className='absolute bottom-4 left-4 z-[1000] bg-white/10 backdrop-blur-md rounded-lg px-3 py-2 border border-white/20'>
        <div className='flex items-center space-x-4 text-xs text-white'>
          {loading ? (
            <div className='flex items-center space-x-2'>
              <div className='w-3 h-3 border border-lime-400 border-t-transparent rounded-full animate-spin'></div>
              <span>Loading...</span>
            </div>
          ) : realData ? (
            <>
              <div className='flex items-center space-x-1'>
                <span className='text-lime-400'>●</span>
                <span>Live Data</span>
              </div>
              <div>{currentStats.totalLocations} locations</div>
              <div>{currentStats.co2Reduction}/year CO₂</div>
              <div>
                {realData.mapLayers
                  ? Object.keys(realData.mapLayers).length
                  : 0}{" "}
                layers
              </div>
            </>
          ) : (
            <div className='flex items-center space-x-2'>
              <span className='text-red-400'>●</span>
              <span>Connection Failed</span>
            </div>
          )}
        </div>
      </motion.div>

      {/* Map Container */}
      <MapContainer
        center={center}
        zoom={14}
        className='h-full w-full'
        style={{ background: "#1a1a1a" }}
        maxBounds={bounds}
        maxBoundsViscosity={1.0}>
        {/* Base Layer - Google-style satellite */}
        <TileLayer
          url='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
          attribution='&copy; Google'
          maxZoom={20}
        />

        {/* Hybrid overlay for labels */}
        <TileLayer
          url='https://mt1.google.com/vt/lyrs=h&x={x}&y={y}&z={z}'
          attribution='&copy; Google'
          maxZoom={20}
        />

        {/* Heat Map Overlay */}
        {layerVisibility.heatMap && heatMapBounds && (
          <ImageOverlay
            url={heatMapBounds.url}
            bounds={heatMapBounds.bounds}
            opacity={heatMapBounds.opacity}
            attribution={heatMapBounds.attribution}
          />
        )}

        {/* Real GeoJSON Layers from Backend */}
        {realData?.mapLayers && (
          <>
            {/* Exclusion Layers */}
            {layerVisibility.buildings && realData.mapLayers.buildings && (
              <GeoJSON
                key='buildings'
                data={realData.mapLayers.buildings}
                style={getEnhancedStyle("buildings")}
              />
            )}

            {layerVisibility.buildingsFresh &&
              realData.mapLayers.buildingsFresh && (
                <GeoJSON
                  key='buildingsFresh'
                  data={realData.mapLayers.buildingsFresh}
                  style={dataService.getLayerStyle("buildingsFresh")}
                />
              )}

            {layerVisibility.roads && realData.mapLayers.roads && (
              <GeoJSON
                key='roads'
                data={realData.mapLayers.roads}
                style={dataService.getLayerStyle("roads")}
              />
            )}

            {layerVisibility.roadsFresh && realData.mapLayers.roadsFresh && (
              <GeoJSON
                key='roadsFresh'
                data={realData.mapLayers.roadsFresh}
                style={dataService.getLayerStyle("roadsFresh")}
              />
            )}

            {layerVisibility.trees && realData.mapLayers.trees && (
              <GeoJSON
                key='trees'
                data={realData.mapLayers.trees}
                style={dataService.getLayerStyle("trees")}
              />
            )}

            {layerVisibility.fire && realData.mapLayers.fire && (
              <GeoJSON
                key='fire'
                data={realData.mapLayers.fire}
                style={dataService.getLayerStyle("fire")}
              />
            )}

            {layerVisibility.water && realData.mapLayers.water && (
              <GeoJSON
                key='water'
                data={realData.mapLayers.water}
                style={dataService.getLayerStyle("water")}
              />
            )}

            {layerVisibility.exclusionCombined &&
              realData.mapLayers.exclusionCombined && (
                <GeoJSON
                  key='exclusionCombined'
                  data={realData.mapLayers.exclusionCombined}
                  style={dataService.getLayerStyle("exclusionCombined")}
                />
              )}

            {layerVisibility.exclusionCombinedFresh &&
              realData.mapLayers.exclusionCombinedFresh && (
                <GeoJSON
                  key='exclusionCombinedFresh'
                  data={realData.mapLayers.exclusionCombinedFresh}
                  style={dataService.getLayerStyle("exclusionCombinedFresh")}
                />
              )}

            {/* Green Areas */}
            {layerVisibility.greenSpaces && realData.mapLayers.greenSpaces && (
              <GeoJSON
                key='greenSpaces'
                data={realData.mapLayers.greenSpaces}
                style={dataService.getLayerStyle("greenSpaces")}
              />
            )}

            {layerVisibility.plantable && realData.mapLayers.plantable && (
              <GeoJSON
                key='plantable'
                data={realData.mapLayers.plantable}
                style={dataService.getLayerStyle("plantable")}
              />
            )}

            {layerVisibility.plantableFresh &&
              realData.mapLayers.plantableFresh && (
                <GeoJSON
                  key='plantableFresh'
                  data={realData.mapLayers.plantableFresh}
                  style={dataService.getLayerStyle("plantableFresh")}
                />
              )}

            {/* Location Points as Markers */}
            {layerVisibility.topWithCoordinates &&
              realData.mapLayers.topWithCoordinates &&
              realData.mapLayers.topWithCoordinates.features?.map(
                (feature, index) => {
                  if (feature.geometry.type === "Point") {
                    const [lng, lat] = feature.geometry.coordinates;
                    return (
                      <Marker
                        key={`coords-${index}`}
                        position={[lat, lng]}
                        icon={createLocationMarker(feature)}>
                        <Popup>
                          <div className='text-gray-900 p-2'>
                            <h3 className='font-bold'>
                              🎯 Top Location with Coordinates
                            </h3>
                            <p className='text-sm'>
                              Score: {feature.properties.final_score || 100}/100
                            </p>
                            <p className='text-sm'>
                              Heat: {feature.properties.heat_score || 100}/100
                            </p>
                            <p className='text-xs'>
                              Lat: {lat.toFixed(6)}, Lng: {lng.toFixed(6)}
                            </p>
                          </div>
                        </Popup>
                      </Marker>
                    );
                  }
                  return null;
                }
              )}

            {layerVisibility.topEnhanced &&
              realData.mapLayers.topEnhanced &&
              realData.mapLayers.topEnhanced.features?.map((feature, index) => {
                if (feature.geometry.type === "Point") {
                  const [lng, lat] = feature.geometry.coordinates;
                  return (
                    <Marker
                      key={`enhanced-${index}`}
                      position={[lat, lng]}
                      icon={createLocationMarker(feature)}>
                      <Popup>
                        <div className='text-gray-900 p-2'>
                          <h3 className='font-bold'>
                            ⭐ Enhanced Top Location
                          </h3>
                          <p className='text-sm'>
                            Score: {feature.properties.final_score || 100}/100
                          </p>
                          <p className='text-sm'>Enhanced Analysis ✨</p>
                        </div>
                      </Popup>
                    </Marker>
                  );
                }
                return null;
              })}

            {layerVisibility.topLocations &&
              realData.mapLayers.topLocations &&
              realData.mapLayers.topLocations.features?.map(
                (feature, index) => {
                  if (feature.geometry.type === "Point") {
                    const [lng, lat] = feature.geometry.coordinates;
                    return (
                      <Marker
                        key={`top-${index}`}
                        position={[lat, lng]}
                        icon={createLocationMarker(feature)}>
                        <Popup>
                          <div className='text-gray-900 p-2'>
                            <h3 className='font-bold'>
                              🔥 Top Location #{index + 1}
                            </h3>
                            <p className='text-sm'>
                              Score: {feature.properties.final_score || 100}/100
                            </p>
                            <p className='text-sm'>
                              Heat: {feature.properties.heat_score || 100}/100
                            </p>
                          </div>
                        </Popup>
                      </Marker>
                    );
                  }
                  return null;
                }
              )}

            {layerVisibility.topLocationsFresh &&
              realData.mapLayers.topLocationsFresh &&
              realData.mapLayers.topLocationsFresh.features?.map(
                (feature, index) => {
                  if (feature.geometry.type === "Point") {
                    const [lng, lat] = feature.geometry.coordinates;
                    return (
                      <Marker
                        key={`fresh-${index}`}
                        position={[lat, lng]}
                        icon={createLocationMarker(feature)}>
                        <Popup>
                          <div className='text-gray-900 p-2'>
                            <h3 className='font-bold'>
                              🔥 Fresh Verified Location
                            </h3>
                            <p className='text-sm'>
                              Score: {feature.properties.final_score || 100}/100
                            </p>
                            <p className='text-sm text-green-600'>
                              ✅ 2020+ Data Verified
                            </p>
                          </div>
                        </Popup>
                      </Marker>
                    );
                  }
                  return null;
                }
              )}

            {/* Scored Locations - render as smaller markers */}
            {layerVisibility.scoredLocationsAllEnhanced &&
              realData.mapLayers.scoredLocationsAllEnhanced &&
              realData.mapLayers.scoredLocationsAllEnhanced.features
                ?.slice(0, 1000)
                .map((feature, index) => {
                  if (feature.geometry.type === "Point") {
                    const [lng, lat] = feature.geometry.coordinates;
                    return (
                      <Marker
                        key={`all-enh-${index}`}
                        position={[lat, lng]}
                        icon={L.circleMarker([lat, lng], {
                          radius: 3,
                          color: "#F7931E",
                        })}>
                        <Popup>
                          <div className='text-gray-900 p-2'>
                            <h3 className='font-bold'>
                              📊 Enhanced Scored Location
                            </h3>
                            <p className='text-sm'>
                              Score: {feature.properties.final_score || "N/A"}
                            </p>
                          </div>
                        </Popup>
                      </Marker>
                    );
                  }
                  return null;
                })}

            {layerVisibility.scoredLocationsFreshEnhanced &&
              realData.mapLayers.scoredLocationsFreshEnhanced &&
              realData.mapLayers.scoredLocationsFreshEnhanced.features
                ?.slice(0, 1000)
                .map((feature, index) => {
                  if (feature.geometry.type === "Point") {
                    const [lng, lat] = feature.geometry.coordinates;
                    return (
                      <Marker
                        key={`fresh-enh-${index}`}
                        position={[lat, lng]}
                        icon={L.circleMarker([lat, lng], {
                          radius: 4,
                          color: "#ADFF2F",
                        })}>
                        <Popup>
                          <div className='text-gray-900 p-2'>
                            <h3 className='font-bold'>
                              📊 Fresh Enhanced Location
                            </h3>
                            <p className='text-sm'>
                              Score: {feature.properties.final_score || "N/A"}
                            </p>
                            <p className='text-sm text-green-600'>
                              ✅ Fresh + Enhanced
                            </p>
                          </div>
                        </Popup>
                      </Marker>
                    );
                  }
                  return null;
                })}
          </>
        )}

        {/* Loading Overlay */}
        {loading && (
          <div className='absolute inset-0 bg-gray-900/80 flex items-center justify-center z-[2000]'>
            <div className='text-center text-white'>
              <div className='w-16 h-16 border-4 border-lime-400 border-t-transparent rounded-full animate-spin mx-auto mb-4'></div>
              <p className='text-gray-300'>Loading real map data...</p>
            </div>
          </div>
        )}
      </MapContainer>
    </div>
  );
};

export default CompleteMap;
