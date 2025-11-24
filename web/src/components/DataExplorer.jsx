/** @format */

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import L from "leaflet";
import {
  Eye,
  EyeOff,
  Layers,
  Info,
  BarChart3,
  TreePine,
  Building,
  Car,
  Droplets,
  Flame,
  Target,
} from "lucide-react";
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

const DataExplorer = ({ realData, center = [49.1427, 9.2109], zoom = 13 }) => {
  const [layerVisibility, setLayerVisibility] = useState({
    allLocations: true,
    buildingsFresh: true,
    roadsFresh: true,
    trees: true,
    fire: false,
    waterBodies: true,
    heatPriorityZones: true,
    scoredLocationsFresh: false,
    topLocations: true,
    topLocationsFresh: true,
  });

  const [showLegend, setShowLegend] = useState(true);
  const [showStats, setShowStats] = useState(true);

  const toggleLayer = (layerName) => {
    setLayerVisibility((prev) => ({
      ...prev,
      [layerName]: !prev[layerName],
    }));
  };

  const layerConfig = [
    {
      key: "buildings",
      name: "Buildings",
      icon: Building,
      color: "#cc0000",
      description: "Building exclusion zones (3m buffer)",
    },
    {
      key: "buildingsFresh",
      name: "Buildings (Fresh)",
      icon: Building,
      color: "#ff4444",
      description: "Fresh building data",
    },
    {
      key: "roads",
      name: "Roads",
      icon: Car,
      color: "#666666",
      description: "Road exclusion zones (2.5m buffer)",
    },
    {
      key: "roadsFresh",
      name: "Roads (Fresh)",
      icon: Car,
      color: "#888888",
      description: "Fresh road data",
    },
    {
      key: "trees",
      name: "Existing Trees",
      icon: TreePine,
      color: "#8B4513",
      description: "Current tree coverage",
    },
    {
      key: "fire",
      name: "Fire Access",
      icon: Flame,
      color: "#ff8800",
      description: "Fire department access zones (5m buffer)",
    },
    {
      key: "water",
      name: "Water Bodies",
      icon: Droplets,
      color: "#0066cc",
      description: "Rivers, lakes, and water features",
    },
    {
      key: "plantable",
      name: "Plantable Areas",
      icon: Target,
      color: "#00ff00",
      description: "Available planting locations",
    },
    {
      key: "plantableFresh",
      name: "Fresh Plantable",
      icon: Target,
      color: "#CCFF00",
      description: "New planting opportunities",
    },
    {
      key: "topLocations",
      name: "Top 100 Locations",
      icon: Target,
      color: "#ff0000",
      description: "Highest priority planting spots",
    },
    {
      key: "topLocationsFresh",
      name: "Fresh Top Locations",
      icon: Target,
      color: "#CCFF00",
      description: "New high-priority locations",
    },
  ];

  const getLayerStats = () => {
    if (!realData?.mapLayers) return {};

    const stats = {};
    Object.entries(realData.mapLayers).forEach(([key, data]) => {
      if (data?.features) {
        stats[key] = {
          count: data.features.length,
          type: data.type,
        };
      }
    });
    return stats;
  };

  const layerStats = getLayerStats();

  return (
    <div className='h-full bg-gray-900 text-white relative flex'>
      {/* Left Panel - Layer Controls */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className='w-80 bg-gray-800/30 backdrop-blur-md border-r border-white/10 p-4 overflow-y-auto'>
        {/* Header */}
        <div className='flex items-center justify-between mb-6'>
          <div className='flex items-center space-x-2'>
            <Layers className='w-6 h-6 text-lime-400' />
            <h2 className='text-xl font-bold'>Data Layers</h2>
          </div>
          <div className='flex space-x-2'>
            <button
              onClick={() => setShowStats(!showStats)}
              className='p-2 hover:bg-white/10 rounded-lg transition-colors'>
              <BarChart3 className='w-5 h-5' />
            </button>
            <button
              onClick={() => setShowLegend(!showLegend)}
              className='p-2 hover:bg-white/10 rounded-lg transition-colors'>
              <Info className='w-5 h-5' />
            </button>
          </div>
        </div>

        {/* Layer Controls */}
        <div className='space-y-2'>
          {layerConfig.map((layer) => {
            const IconComponent = layer.icon;
            const isVisible = layerVisibility[layer.key];
            const hasData =
              realData?.mapLayers?.[layer.key]?.features?.length > 0;
            const featureCount = layerStats[layer.key]?.count || 0;

            return (
              <motion.div
                key={layer.key}
                whileHover={{ scale: 1.02 }}
                className={`p-3 rounded-lg border transition-all ${
                  hasData
                    ? isVisible
                      ? "bg-white/10 border-lime-400/50"
                      : "bg-white/5 border-white/10 hover:border-white/20"
                    : "bg-gray-700/30 border-gray-600/30 opacity-50"
                }`}>
                <div className='flex items-center justify-between'>
                  <div className='flex items-center space-x-3'>
                    <div
                      className='w-4 h-4 rounded-full'
                      style={{ backgroundColor: layer.color }}
                    />
                    <IconComponent className='w-5 h-5 text-gray-300' />
                    <div>
                      <div className='font-medium text-sm'>{layer.name}</div>
                      {hasData && (
                        <div className='text-xs text-gray-400'>
                          {featureCount.toLocaleString()} features
                        </div>
                      )}
                    </div>
                  </div>

                  <button
                    onClick={() => hasData && toggleLayer(layer.key)}
                    disabled={!hasData}
                    className={`p-1 rounded transition-colors ${
                      hasData
                        ? "hover:bg-white/10"
                        : "cursor-not-allowed opacity-50"
                    }`}>
                    {isVisible && hasData ? (
                      <Eye className='w-4 h-4 text-lime-400' />
                    ) : (
                      <EyeOff className='w-4 h-4 text-gray-500' />
                    )}
                  </button>
                </div>

                {showLegend && (
                  <div className='mt-2 text-xs text-gray-400'>
                    {layer.description}
                  </div>
                )}
              </motion.div>
            );
          })}
        </div>

        {/* Statistics Panel */}
        {showStats && realData?.statistics && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className='mt-6 p-4 bg-gray-700/50 rounded-lg'>
            <h3 className='font-bold text-lg mb-3 flex items-center space-x-2'>
              <BarChart3 className='w-5 h-5 text-lime-400' />
              <span>Live Statistics</span>
            </h3>

            <div className='space-y-2 text-sm'>
              <div className='flex justify-between'>
                <span className='text-gray-400'>Total Locations:</span>
                <span className='text-white font-medium'>
                  {realData.statistics.stats.totalLocations?.toLocaleString()}
                </span>
              </div>
              <div className='flex justify-between'>
                <span className='text-gray-400'>Fresh Locations:</span>
                <span className='text-lime-400 font-medium'>
                  {realData.statistics.stats.freshLocations?.toLocaleString()}
                </span>
              </div>
              <div className='flex justify-between'>
                <span className='text-gray-400'>Plantable Area:</span>
                <span className='text-white font-medium'>
                  {realData.statistics.stats.plantableArea}
                </span>
              </div>
              <div className='flex justify-between'>
                <span className='text-gray-400'>CO₂ Reduction:</span>
                <span className='text-green-400 font-medium'>
                  {realData.statistics.stats.co2Reduction}
                </span>
              </div>
            </div>
          </motion.div>
        )}

        {/* Quick Actions */}
        <div className='mt-6 space-y-2'>
          <button
            onClick={() => {
              const newVisibility = {};
              layerConfig.forEach((layer) => {
                newVisibility[layer.key] = true;
              });
              setLayerVisibility(newVisibility);
            }}
            className='w-full py-2 px-4 bg-lime-400 text-black font-medium rounded-lg hover:bg-lime-300 transition-colors'>
            Show All Layers
          </button>

          <button
            onClick={() => {
              const newVisibility = {};
              layerConfig.forEach((layer) => {
                newVisibility[layer.key] = false;
              });
              setLayerVisibility(newVisibility);
            }}
            className='w-full py-2 px-4 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-500 transition-colors'>
            Hide All Layers
          </button>
        </div>
      </motion.div>

      {/* Right Panel - Map */}
      <div className='flex-1 relative'>
        <MapContainer
          center={center}
          zoom={zoom}
          className='h-full w-full'
          style={{ background: "#1a1a1a" }}>
          {/* Base Layer */}
          <TileLayer
            url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />

          {/* Render GeoJSON Layers */}
          {realData?.mapLayers &&
            Object.entries(realData.mapLayers).map(([layerKey, layerData]) => {
              if (!layerVisibility[layerKey] || !layerData?.features?.length) {
                return null;
              }

              const style = dataService.getLayerStyle(layerKey);

              return (
                <GeoJSON
                  key={layerKey}
                  data={layerData}
                  style={style}
                  pointToLayer={(feature, latlng) => {
                    return L.circleMarker(latlng, {
                      ...style,
                      radius: style.radius || 6,
                    });
                  }}
                  onEachFeature={(feature, layer) => {
                    if (feature.properties) {
                      const props = feature.properties;
                      let popupContent = `<div class="text-sm">`;

                      if (props.final_score) {
                        popupContent += `<strong>Score:</strong> ${props.final_score}<br>`;
                      }
                      if (props.area_m2) {
                        popupContent += `<strong>Area:</strong> ${props.area_m2} m²<br>`;
                      }
                      if (props.name || props.NAME) {
                        popupContent += `<strong>Name:</strong> ${
                          props.name || props.NAME
                        }<br>`;
                      }

                      popupContent += `<strong>Layer:</strong> ${layerKey}</div>`;
                      layer.bindPopup(popupContent);
                    }
                  }}
                />
              );
            })}
        </MapContainer>

        {/* Loading Overlay */}
        {!realData && (
          <div className='absolute inset-0 bg-gray-900/80 flex items-center justify-center'>
            <div className='text-center'>
              <div className='w-16 h-16 border-4 border-lime-400 border-t-transparent rounded-full animate-spin mx-auto mb-4'></div>
              <p className='text-gray-300'>Loading map data...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DataExplorer;
