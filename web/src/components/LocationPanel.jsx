/** @format */

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X,
  TreePine,
  MapPin,
  Thermometer,
  Users,
  Leaf,
  Navigation,
} from "lucide-react";

const LocationPanel = ({ selectedLocation, setSelectedLocation }) => {
  if (!selectedLocation) return null;

  const locationDetails = {
    1: {
      title: "Top Location #1 - Innenstadt",
      description:
        "This is the highest-ranked tree planting location in Heilbronn with perfect environmental conditions and maximum community impact. Located in the city center with extreme heat priority.",
      image:
        "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=200&fit=crop",
      benefits: [
        {
          icon: Thermometer,
          text: "Reduces temperature by 2.5°C in 20m radius",
          value: "98/100 heat priority",
        },
        {
          icon: Users,
          text: "Benefits 267 residents and 3 schools nearby",
          value: "High social impact",
        },
        {
          icon: Leaf,
          text: "Estimated 15.2 tonnes CO₂ absorption/year",
          value: "Environmental benefit",
        },
        {
          icon: Navigation,
          text: "Easy access for maintenance vehicles",
          value: "Practical deployment",
        },
      ],
      recommendations: [
        {
          species: "Ahornblättrige Platane",
          suitability: "Excellent",
          reason: "Heat resistant, large canopy",
        },
        {
          species: "Winterlinde",
          suitability: "Very Good",
          reason: "Urban pollution tolerant",
        },
        {
          species: "Feldahorn",
          suitability: "Good",
          reason: "Compact growth, low maintenance",
        },
      ],
      coordinates: { lat: 49.1427, lng: 9.2109 },
      exclusions:
        "3m from buildings, 2.5m from roads, no utility conflicts detected",
    },
  };

  const location = locationDetails[selectedLocation.id] || {
    title: selectedLocation.name,
    description: `High-priority tree planting location in ${selectedLocation.district} with excellent environmental and social benefits.`,
    image:
      "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=200&fit=crop",
    benefits: [
      {
        icon: Thermometer,
        text: `Heat Priority: ${selectedLocation.heatPriority}/100`,
        value: "Temperature reduction",
      },
      {
        icon: Users,
        text: "Community benefits",
        value: "Residential area coverage",
      },
      {
        icon: Leaf,
        text: "CO₂ absorption potential",
        value: "Environmental impact",
      },
      {
        icon: Navigation,
        text: "Accessible location",
        value: "Maintenance friendly",
      },
    ],
    recommendations: [
      {
        species: "Platane",
        suitability: "Excellent",
        reason: "Urban conditions",
      },
      { species: "Linde", suitability: "Very Good", reason: "Climate adapted" },
    ],
    coordinates: { lat: selectedLocation.lat, lng: selectedLocation.lng },
    exclusions: "Safety buffers applied, verified clear of utilities",
  };

  const getScoreColor = (score) => {
    if (score >= 95) return "text-green-500";
    if (score >= 90) return "text-yellow-500";
    return "text-orange-500";
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ x: "100%" }}
        animate={{ x: 0 }}
        exit={{ x: "100%" }}
        transition={{ type: "spring", damping: 25, stiffness: 200 }}
        className='absolute right-0 top-0 h-full w-96 bg-gray-800/95 backdrop-blur-md border-l border-white/10 z-[1000] overflow-y-auto'>
        <div className='p-6'>
          {/* Header */}
          <div className='flex items-start justify-between mb-6'>
            <div className='flex-1'>
              <div className='flex items-center space-x-2 mb-2'>
                <h2 className='text-xl font-bold'>{location.title}</h2>
                {selectedLocation.verified && (
                  <span className='bg-lime-400 text-black text-xs px-2 py-1 rounded-full font-bold'>
                    ✅ Verified
                  </span>
                )}
              </div>
              <p className='text-gray-400 text-sm'>
                {selectedLocation.postalCode} • {selectedLocation.district}
              </p>
              <button
                onClick={() => setSelectedLocation(null)}
                className='absolute top-4 right-4 p-2 hover:bg-white/10 rounded-full transition-colors'>
                <X className='w-5 h-5' />
              </button>
            </div>
          </div>

          {/* Score Display */}
          <div className='mb-6 p-4 bg-gray-700/50 rounded-xl'>
            <div className='flex items-center justify-between mb-2'>
              <span className='text-gray-400'>Overall Score</span>
              <span
                className={`text-3xl font-bold ${getScoreColor(
                  selectedLocation.score
                )}`}>
                {selectedLocation.score}/100
              </span>
            </div>
            <div className='w-full bg-gray-600 rounded-full h-2'>
              <div
                className='bg-lime-400 h-2 rounded-full transition-all duration-300'
                style={{ width: `${selectedLocation.score}%` }}
              />
            </div>
          </div>

          {/* Image */}
          <div className='mb-6 rounded-xl overflow-hidden'>
            <img
              src={location.image}
              alt={location.title}
              className='w-full h-48 object-cover'
            />
          </div>

          {/* Description */}
          <p className='text-gray-300 mb-6 leading-relaxed'>
            {location.description}
          </p>

          {/* Benefits */}
          <div className='mb-6'>
            <h3 className='font-bold mb-4 flex items-center space-x-2'>
              <TreePine className='w-5 h-5 text-lime-400' />
              <span>Environmental Benefits</span>
            </h3>
            <div className='space-y-3'>
              {location.benefits.map((benefit, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className='flex items-start space-x-3 p-3 rounded-lg hover:bg-white/5 transition-colors'>
                  <benefit.icon className='w-5 h-5 text-lime-400 mt-0.5 flex-shrink-0' />
                  <div className='flex-1'>
                    <p className='text-sm'>{benefit.text}</p>
                    <p className='text-xs text-gray-400 mt-1'>
                      {benefit.value}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Tree Recommendations */}
          <div className='mb-6'>
            <h3 className='font-bold mb-4 flex items-center space-x-2'>
              <Leaf className='w-5 h-5 text-lime-400' />
              <span>Recommended Species</span>
            </h3>
            <div className='space-y-2'>
              {location.recommendations.map((rec, index) => (
                <div key={index} className='p-3 bg-gray-700/30 rounded-lg'>
                  <div className='flex justify-between items-start mb-1'>
                    <span className='font-medium'>{rec.species}</span>
                    <span className='text-xs text-lime-400'>
                      {rec.suitability}
                    </span>
                  </div>
                  <p className='text-xs text-gray-400'>{rec.reason}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Coordinates */}
          <div className='mb-6 p-3 bg-gray-700/30 rounded-lg'>
            <h4 className='font-medium mb-2 flex items-center space-x-2'>
              <MapPin className='w-4 h-4 text-lime-400' />
              <span>Coordinates</span>
            </h4>
            <p className='text-sm text-gray-300 font-mono'>
              {location.coordinates.lat.toFixed(6)},{" "}
              {location.coordinates.lng.toFixed(6)}
            </p>
            <p className='text-xs text-gray-400 mt-1'>{location.exclusions}</p>
          </div>

          {/* Action Buttons */}
          <div className='space-y-3'>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className='w-full bg-lime-400 text-black font-bold py-3 rounded-xl hover:bg-lime-300 transition-colors'>
              📍 Navigate to Location
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className='w-full bg-gray-700 text-white font-medium py-3 rounded-xl hover:bg-gray-600 transition-colors'>
              📊 View Detailed Analysis
            </motion.button>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default LocationPanel;
