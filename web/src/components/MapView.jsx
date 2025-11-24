/** @format */

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
} from "react-leaflet";
import L from "leaflet";
import { Clock, MapPin, Route, TreePine, Target } from "lucide-react";

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

const MapView = ({ selectedLocation, setSelectedLocation }) => {
  const [mapData, setMapData] = useState({
    center: [49.1427, 9.2109], // Heilbronn coordinates
    zoom: 13,
    locations: [
      {
        id: 1,
        name: "Top Location #1",
        lat: 49.1427,
        lng: 9.2109,
        type: "top-score",
        score: 100,
        heatPriority: 98,
        postalCode: "74072",
        district: "Innenstadt",
        verified: true,
      },
      {
        id: 2,
        name: "Böckingen High Priority",
        lat: 49.1435,
        lng: 9.2115,
        type: "high-score",
        score: 96.5,
        heatPriority: 95,
        postalCode: "74074",
        district: "Böckingen",
        verified: true,
      },
      {
        id: 3,
        name: "Sontheim Green Zone",
        lat: 49.142,
        lng: 9.2095,
        type: "high-score",
        score: 95.8,
        heatPriority: 92,
        postalCode: "74076",
        district: "Sontheim",
        verified: false,
      },
      {
        id: 4,
        name: "Neckargartach Area",
        lat: 49.1445,
        lng: 9.213,
        type: "medium-score",
        score: 94.2,
        heatPriority: 88,
        postalCode: "74078",
        district: "Neckargartach",
        verified: true,
      },
      {
        id: 5,
        name: "Frankenbach District",
        lat: 49.141,
        lng: 9.208,
        type: "medium-score",
        score: 93.5,
        heatPriority: 85,
        postalCode: "74080",
        district: "Frankenbach",
        verified: false,
      },
      {
        id: 6,
        name: "Fresh Data Verified",
        lat: 49.145,
        lng: 9.214,
        type: "fresh-verified",
        score: 97.2,
        heatPriority: 96,
        postalCode: "74074",
        district: "Böckingen",
        verified: true,
      },
    ],
  });

  const getMarkerColor = (type, verified) => {
    if (verified && type === "fresh-verified") return "#CCFF00";
    if (type === "top-score") return "#FF6B35";
    if (type === "high-score") return "#F7931E";
    if (type === "medium-score") return "#FFD23F";
    return "#6B7280";
  };

  const createCustomIcon = (type, verified, score) => {
    const color = getMarkerColor(type, verified);
    const size = type === "top-score" ? 32 : 24;
    return L.divIcon({
      className: "custom-marker",
      html: `
        <div style="
          width: ${size}px;
          height: ${size}px;
          background-color: ${color};
          border: 3px solid white;
          border-radius: 50%;
          box-shadow: 0 2px 8px rgba(0,0,0,0.3);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: ${size === 32 ? "12px" : "10px"};
          color: ${color === "#CCFF00" ? "#000" : "#fff"};
          ${type === "top-score" ? "animation: pulse 2s infinite;" : ""}
        ">
          ${Math.round(score)}
        </div>
      `,
      iconSize: [size, size],
      iconAnchor: [size / 2, size / 2],
    });
  };

  return (
    <div className='h-full relative'>
      {/* Map Stats Overlay */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className='absolute top-6 left-6 z-[1000] glass-effect rounded-2xl p-4 min-w-[350px]'>
        <h2 className='text-2xl font-bold mb-2'>🌳 Heilbronn Tree Planting</h2>
        <p className='text-gray-400 text-sm mb-4'>
          AI-powered urban forestry platform with verified locations
        </p>

        <div className='flex items-center space-x-6 text-sm'>
          <div className='flex items-center space-x-2'>
            <TreePine className='w-4 h-4 text-accent' />
            <span className='text-gray-400'>13,882</span>
            <span className='text-white'>verified locations</span>
          </div>
          <div className='flex items-center space-x-2'>
            <Route className='w-4 h-4 text-accent' />
            <span className='text-gray-400'>1.39 km²</span>
            <span className='text-white'>plantable area</span>
          </div>
          <div className='flex items-center space-x-2'>
            <Target className='w-4 h-4 text-accent' />
            <span className='text-gray-400'>305t</span>
            <span className='text-white'>CO₂/year reduction</span>
          </div>
        </div>
      </motion.div>

      {/* Legend */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className='absolute top-6 right-6 z-[1000] glass-effect rounded-xl p-4'>
        <h3 className='font-bold mb-3 text-sm'>Location Types</h3>
        <div className='space-y-2 text-xs'>
          <div className='flex items-center space-x-2'>
            <div className='w-4 h-4 bg-orange-500 rounded-full'></div>
            <span>Top Score (95-100)</span>
          </div>
          <div className='flex items-center space-x-2'>
            <div className='w-4 h-4 bg-yellow-500 rounded-full'></div>
            <span>High Score (90-95)</span>
          </div>
          <div className='flex items-center space-x-2'>
            <div className='w-4 h-4 bg-lime-400 rounded-full'></div>
            <span>Fresh Verified ✅</span>
          </div>
        </div>
      </motion.div>

      {/* Map Container */}
      <MapContainer
        center={mapData.center}
        zoom={mapData.zoom}
        className='h-full w-full'
        style={{ background: "#1a1a1a" }}>
        <TileLayer
          url='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />

        {/* Location Markers */}
        {mapData.locations.map((location) => (
          <Marker
            key={location.id}
            position={[location.lat, location.lng]}
            icon={createCustomIcon(
              location.type,
              location.verified,
              location.score
            )}
            eventHandlers={{
              click: () => setSelectedLocation(location),
            }}>
            <Popup>
              <div className='text-dark-900 p-2'>
                <h3 className='font-bold text-lg'>{location.name}</h3>
                <p className='text-sm text-gray-600 mb-2'>
                  {location.district} ({location.postalCode})
                </p>
                <div className='space-y-1 text-sm'>
                  <div className='flex justify-between'>
                    <span>Score:</span>
                    <span className='font-bold text-green-600'>
                      {location.score}/100
                    </span>
                  </div>
                  <div className='flex justify-between'>
                    <span>Heat Priority:</span>
                    <span className='font-bold text-red-600'>
                      {location.heatPriority}/100
                    </span>
                  </div>
                  <div className='flex justify-between'>
                    <span>Status:</span>
                    <span
                      className={`font-bold ${
                        location.verified ? "text-green-600" : "text-orange-600"
                      }`}>
                      {location.verified ? "✅ Verified" : "⏳ Pending"}
                    </span>
                  </div>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default MapView;
