/** @format */

import { useState } from "react";
import { MapContainer, TileLayer, GeoJSON, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import { motion } from "framer-motion";
import { Layers, Info } from "lucide-react";
import dataService from "../services/dataService";

const RealMapView = ({
  realData,
  center = [49.1427, 9.2109],
  zoom = 13,
  aiLocations = [],
  selectedLocation, // not used yet, but keeps props in sync with MainLayout
}) => {
  const [layerVisibility, setLayerVisibility] = useState({
    // Light layers enabled by default
    waterBodies: true,
    heatPriorityZones: true,
    topLocationsFresh: true,
    topLocations: true,
    // AI locations toggle
    aiLocations: true,
  });
  const [showLegend, setShowLegend] = useState(true);

  // Heilbronn bounds
  const bounds = [
    [49.12, 9.18],
    [49.17, 9.25],
  ];

  const toggleLayer = (layerName) => {
    setLayerVisibility((prev) => ({
      ...prev,
      [layerName]: !prev[layerName],
    }));
  };

  if (!realData) {
    return (
      <div className='h-full flex items-center justify-center bg-gray-800'>
        <div className='text-center'>
          <div className='animate-spin w-8 h-8 border-2 border-lime-400 border-t-transparent rounded-full mx-auto mb-4'></div>
          <p className='text-gray-400'>Loading real map data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className='h-full relative'>
      {/* Legend Panel */}
      {showLegend && (
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className='absolute top-4 left-4 z-[1000] bg-white/95 backdrop-blur-md rounded-xl p-4 border border-white/20 max-w-sm'>
          <h3 className='text-lg font-bold text-green-600 mb-3 flex items-center space-x-2'>
            <span>🌳</span>
            <span>Heilbronn Tree Analysis</span>
          </h3>

          <div className='space-y-3 text-gray-800 text-sm'>
            <div>
              <h4 className='font-bold mb-2'>🔥 Heat Priority:</h4>
              <div className='space-y-1 text-xs'>
                <div className='flex items-center space-x-2'>
                  <div className='w-4 h-4 bg-red-500'></div>
                  <span>Extreme (95-100) - URGENT!</span>
                </div>
                <div className='flex items-center space-x-2'>
                  <div className='w-4 h-4 bg-orange-500'></div>
                  <span>High (85-95)</span>
                </div>
                <div className='flex items-center space-x-2'>
                  <div className='w-4 h-4 bg-yellow-500'></div>
                  <span>Medium (70-85)</span>
                </div>
              </div>
            </div>

            <div className='border-t pt-2'>
              <div className='flex items-center justify-between'>
                <div className='flex items-center space-x-2'>
                  <div className='w-3 h-3 bg-lime-400 rounded-full animate-pulse'></div>
                  <span className='font-bold text-green-600'>
                    TREE LOCATIONS
                  </span>
                </div>
              </div>
              <div className='text-xs mt-1'>
                <div className='font-bold'>11.50 km² total area</div>
                <div className='text-green-600'>1.39 km² fresh verified</div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Controls */}
      <div className='absolute top-4 right-4 z-[1000] flex flex-col space-y-2'>
        <button
          onClick={() => setShowLegend(!showLegend)}
          className='bg-white/10 backdrop-blur-md border border-white/20 text-white p-2 rounded-lg hover:bg-white/20 transition-all'>
          <Info className='w-4 h-4' />
        </button>

        {/* Layer Toggle Panel */}
        <div className='bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-3 text-white text-sm'>
          <div className='font-bold mb-2 flex items-center space-x-1'>
            <Layers className='w-4 h-4' />
            <span>Layers</span>
          </div>
          <div className='space-y-1'>
            {/* Fast Layers */}
            <label className='flex items-center justify-between cursor-pointer'>
              <div className='flex items-center space-x-2'>
                <input
                  type='checkbox'
                  checked={layerVisibility.topLocations}
                  onChange={() => toggleLayer("topLocations")}
                  className='rounded'
                />
                <span>Top 100 Locations</span>
              </div>
              <span className='text-green-400 text-xs'>✓ Fast</span>
            </label>

            <label className='flex items-center justify-between cursor-pointer'>
              <div className='flex items-center space-x-2'>
                <input
                  type='checkbox'
                  checked={layerVisibility.topLocationsFresh}
                  onChange={() => toggleLayer("topLocationsFresh")}
                  className='rounded'
                />
                <span>Fresh Top Locations</span>
              </div>
              <span className='text-green-400 text-xs'>✓ Fast</span>
            </label>

            <label className='flex items-center justify-between cursor-pointer'>
              <div className='flex items-center space-x-2'>
                <input
                  type='checkbox'
                  checked={layerVisibility.heatPriorityZones}
                  onChange={() => toggleLayer("heatPriorityZones")}
                  className='rounded'
                />
                <span>Heat Zones</span>
              </div>
              <span className='text-green-400 text-xs'>✓ Fast</span>
            </label>

            {/* AI Locations Toggle */}
            {aiLocations && aiLocations.length > 0 && (
              <label className='flex items-center justify-between cursor-pointer bg-lime-400/10 border border-lime-400/30 rounded p-2'>
                <div className='flex items-center space-x-2'>
                  <input
                    type='checkbox'
                    checked={layerVisibility.aiLocations}
                    onChange={() => toggleLayer("aiLocations")}
                    className='rounded'
                  />
                  <span className='font-semibold'>AI Locations</span>
                </div>
                <span className='text-lime-400 text-xs font-bold'>
                  🤖 {aiLocations.length}
                </span>
              </label>
            )}
          </div>
        </div>
      </div>

      {/* Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className='absolute bottom-4 left-4 z-[1000] bg-white/10 backdrop-blur-md rounded-lg p-3 border border-white/20'>
        <div className='text-xs space-y-1 text-white'>
          <div className='font-bold text-lime-400'>🎮 REAL DATA LOADED</div>
          <div>
            ✅{" "}
            {realData.statistics?.stats?.totalLocations?.toLocaleString() ||
              "0"}{" "}
            locations analyzed
          </div>
          <div>
            ✅{" "}
            {realData.statistics?.stats?.freshLocations?.toLocaleString() ||
              "0"}{" "}
            fresh verified
          </div>
          <div className='text-orange-400'>
            📊 {realData.statistics?.stats?.perfectLocations || "0"} perfect
            scores!
          </div>
          {aiLocations && aiLocations.length > 0 && (
            <div className='text-lime-400'>
              🤖 {aiLocations.length} AI recommendations
            </div>
          )}
        </div>
      </motion.div>

      {/* Map */}
      <MapContainer
        center={center}
        zoom={zoom}
        key={`${center[0]}-${center[1]}-${zoom}`}
        className='h-full w-full'
        style={{ background: "#1a1a1a" }}
        maxBounds={bounds}
        maxBoundsViscosity={1.0}>
        <TileLayer
          url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        {/* Water Bodies */}
        {layerVisibility.waterBodies && realData.mapLayers?.waterBodies && (
          <GeoJSON
            data={realData.mapLayers.waterBodies}
            style={dataService.getLayerStyle("waterBodies")}
          />
        )}

        {/* Heat Priority Zones */}
        {layerVisibility.heatPriorityZones &&
          realData.mapLayers?.heatPriorityZones && (
            <GeoJSON
              data={realData.mapLayers.heatPriorityZones}
              style={dataService.getLayerStyle("heatPriorityZones")}
            />
          )}

        {/* Top Locations as GeoJSON Points */}
        {layerVisibility.topLocations && realData.mapLayers?.topLocations && (
          <GeoJSON
            data={realData.mapLayers.topLocations}
            style={(feature) =>
              dataService.getFeatureStyle(feature, "topLocations")
            }
            pointToLayer={(feature, latlng) => {
              return L.circleMarker(latlng, {
                ...dataService.getFeatureStyle(feature, "topLocations"),
                radius: 8,
              });
            }}
            onEachFeature={(feature, layer) => {
              layer.bindPopup(`
                <div class="text-gray-900 p-2">
                  <h3 class="font-bold">Top Location #${
                    feature.properties.rank || "N/A"
                  }</h3>
                  <p class="text-sm">Score: ${(
                    feature.properties.final_score || 0
                  ).toFixed(1)}/100</p>
                  <p class="text-sm">Heat: ${(
                    feature.properties.heat_score || 0
                  ).toFixed(1)}/100</p>
                  <p class="text-sm">Spatial: ${(
                    feature.properties.spatial_score || 0
                  ).toFixed(1)}/100</p>
                  <p class="text-sm">Social: ${(
                    feature.properties.social_score || 0
                  ).toFixed(1)}/100</p>
                </div>
              `);
            }}
          />
        )}

        {/* Fresh Top Locations */}
        {layerVisibility.topLocationsFresh &&
          realData.mapLayers?.topLocationsFresh && (
            <GeoJSON
              data={realData.mapLayers.topLocationsFresh}
              style={(feature) =>
                dataService.getFeatureStyle(feature, "topLocationsFresh")
              }
              pointToLayer={(feature, latlng) => {
                return L.circleMarker(latlng, {
                  ...dataService.getFeatureStyle(feature, "topLocationsFresh"),
                  radius: 10,
                });
              }}
              onEachFeature={(feature, layer) => {
                layer.bindPopup(`
                <div class="text-gray-900 p-2">
                  <h3 class="font-bold">Fresh Verified Location</h3>
                  <p class="text-sm">Score: ${(
                    feature.properties.final_score || 0
                  ).toFixed(1)}/100</p>
                  <p class="text-sm text-green-600">✅ 2020+ Data Verified</p>
                  <p class="text-xs">Rank: ${
                    feature.properties.rank || "N/A"
                  }</p>
                </div>
              `);
              }}
            />
          )}

        {/* AI Recommended Locations */}
        {layerVisibility.aiLocations &&
          aiLocations &&
          aiLocations.length > 0 &&
          aiLocations.map((location, index) => {
            if (
              location.lat == null ||
              location.lng == null ||
              Number.isNaN(location.lat) ||
              Number.isNaN(location.lng)
            ) {
              return null;
            }

            // Create custom AI icon
            const aiIcon = L.divIcon({
              className: "ai-location-marker",
              html: `
                <div style="
                  width: 32px;
                  height: 32px;
                  background: linear-gradient(135deg, #a3e635, #84cc16);
                  border: 3px solid white;
                  border-radius: 50%;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  box-shadow: 0 4px 12px rgba(163, 230, 53, 0.4);
                  animation: pulse 2s infinite;
                ">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                    <path d="M12 17h.01"/>
                  </svg>
                </div>
              `,
              iconSize: [32, 32],
              iconAnchor: [16, 16],
            });

            return (
              <Marker
                key={`ai-${location.id || index}`}
                position={[location.lat, location.lng]}
                icon={aiIcon}>
                <Popup>
                  <div className='ai-popup p-3 max-w-sm'>
                    <div className='flex items-center space-x-2 mb-3'>
                      <div className='w-6 h-6 bg-gradient-to-r from-lime-400 to-green-500 rounded-full flex items-center justify-center'>
                        <span className='text-black text-xs font-bold'>AI</span>
                      </div>
                      <h3 className='font-bold text-gray-900'>
                        AI Recommended Location
                      </h3>
                    </div>

                    <div className='space-y-2 text-sm text-gray-700'>
                      <div className='flex justify-between'>
                        <span>Score:</span>
                        <span className='font-semibold text-lime-600'>
                          {location.score}/100
                        </span>
                      </div>

                      <div className='bg-gray-100 p-2 rounded text-xs'>
                        <strong>Location Summary:</strong>
                        <br />
                        {location.info}
                      </div>

                      {location.details && (
                        <div className='space-y-2 text-xs'>
                          <div className='grid grid-cols-2 gap-2'>
                            <div className='text-center bg-green-100 p-1 rounded'>
                              <div className='font-bold text-green-700'>
                                Heat
                              </div>
                              <div>{location.details.heatScore}/100</div>
                            </div>
                            <div className='text-center bg-blue-100 p-1 rounded'>
                              <div className='font-bold text-blue-700'>
                                Spatial
                              </div>
                              <div>{location.details.spatialScore}/100</div>
                            </div>
                            <div className='text-center bg-purple-100 p-1 rounded'>
                              <div className='font-bold text-purple-700'>
                                Social
                              </div>
                              <div>{location.details.socialScore}/100</div>
                            </div>
                            <div className='text-center bg-orange-100 p-1 rounded'>
                              <div className='font-bold text-orange-700'>
                                Maintenance
                              </div>
                              <div>{location.details.maintenanceScore}/100</div>
                            </div>
                          </div>

                          {location.details.species && (
                            <div className='bg-lime-100 p-2 rounded'>
                              <strong>🌳 Species:</strong>{" "}
                              {location.details.species}
                            </div>
                          )}

                          {location.details.cooling && (
                            <div className='bg-blue-100 p-2 rounded'>
                              <strong>❄️ Cooling:</strong>{" "}
                              {location.details.cooling}
                            </div>
                          )}

                          {location.fullSummary && (
                            <details className='bg-gray-50 p-2 rounded'>
                              <summary className='font-bold cursor-pointer'>
                                📋 Full Details
                              </summary>
                              <div className='mt-2 text-xs whitespace-pre-line'>
                                {location.fullSummary}
                              </div>
                            </details>
                          )}
                        </div>
                      )}

                      <div className='text-xs text-gray-500 mt-2'>
                        📍 {location.lat.toFixed(6)}, {location.lng.toFixed(6)}
                      </div>
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })}
      </MapContainer>

      {/* CSS for AI marker animation */}
      <style jsx>{`
        @keyframes pulse {
          0% {
            transform: scale(1);
            box-shadow: 0 4px 12px rgba(163, 230, 53, 0.4);
          }
          50% {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(163, 230, 53, 0.6);
          }
          100% {
            transform: scale(1);
            box-shadow: 0 4px 12px rgba(163, 230, 53, 0.4);
          }
        }

        .ai-location-marker {
          background: transparent !important;
          border: none !important;
        }
      `}</style>
    </div>
  );
};

export default RealMapView;
