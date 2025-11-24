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
  Award,
  Target,
  Clock,
} from "lucide-react";

const LocationDetailsPanel = ({
  selectedLocation,
  setSelectedLocation,
  realData,
}) => {
  if (!selectedLocation) return null;

  const isTreeLocation = selectedLocation.score !== undefined;
  const isPostalArea = selectedLocation.code !== undefined;

  const getAreaStats = () => {
    if (!isPostalArea || !realData?.statistics?.topLocations) return null;

    const areaLocations = realData.statistics.topLocations.filter(
      (loc) => loc.postal_code === selectedLocation.code
    );

    if (areaLocations.length === 0) return null;

    const avgScore =
      areaLocations.reduce(
        (sum, loc) => sum + parseFloat(loc.final_score || 0),
        0
      ) / areaLocations.length;

    const perfectScores = areaLocations.filter(
      (loc) => parseFloat(loc.final_score) === 100
    ).length;

    const topLocations = areaLocations
      .sort((a, b) => parseFloat(b.final_score) - parseFloat(a.final_score))
      .slice(0, 5);

    return {
      totalLocations: areaLocations.length,
      averageScore: avgScore.toFixed(1),
      perfectScores,
      topLocations,
    };
  };

  const areaStats = getAreaStats();

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
              <h2 className='text-xl font-bold mb-2 flex items-center space-x-2'>
                {isTreeLocation ? (
                  <TreePine className='w-6 h-6 text-lime-400' />
                ) : (
                  <MapPin className='w-6 h-6 text-lime-400' />
                )}
                <span>
                  {isTreeLocation
                    ? `Top Location #${selectedLocation.rank || "N/A"}`
                    : `${selectedLocation.code} - ${selectedLocation.name}`}
                </span>
              </h2>
              <button
                onClick={() => setSelectedLocation(null)}
                className='absolute top-4 right-4 p-2 hover:bg-white/10 rounded-full transition-colors'>
                <X className='w-5 h-5' />
              </button>
            </div>
          </div>

          {/* Tree Location Details */}
          {isTreeLocation && (
            <div>
              {/* Score Display */}
              <div className='mb-6 p-4 bg-gray-700/50 rounded-xl'>
                <div className='flex items-center justify-between mb-2'>
                  <span className='text-gray-400'>Overall Score</span>
                  <span
                    className={`text-3xl font-bold ${
                      selectedLocation.score === 100
                        ? "text-lime-400"
                        : selectedLocation.score >= 95
                        ? "text-green-400"
                        : selectedLocation.score >= 90
                        ? "text-yellow-400"
                        : "text-orange-400"
                    }`}>
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

              {/* Location Info */}
              <div className='space-y-4 mb-6'>
                <div className='flex items-center space-x-3'>
                  <MapPin className='w-5 h-5 text-blue-400' />
                  <div>
                    <div className='font-medium'>Coordinates</div>
                    <div className='text-gray-400 text-sm'>
                      {selectedLocation.coordinates?.[0]?.toFixed(6)},{" "}
                      {selectedLocation.coordinates?.[1]?.toFixed(6)}
                    </div>
                  </div>
                </div>

                {selectedLocation.cooling && (
                  <div className='flex items-center space-x-3'>
                    <Thermometer className='w-5 h-5 text-red-400' />
                    <div>
                      <div className='font-medium'>Cooling Effect</div>
                      <div className='text-gray-400 text-sm'>
                        {selectedLocation.cooling}
                      </div>
                    </div>
                  </div>
                )}

                {selectedLocation.residents && (
                  <div className='flex items-center space-x-3'>
                    <Users className='w-5 h-5 text-purple-400' />
                    <div>
                      <div className='font-medium'>Community Impact</div>
                      <div className='text-gray-400 text-sm'>
                        {selectedLocation.residents}
                      </div>
                    </div>
                  </div>
                )}

                {selectedLocation.schools && (
                  <div className='flex items-center space-x-3'>
                    <Target className='w-5 h-5 text-yellow-400' />
                    <div>
                      <div className='font-medium'>Nearby Facilities</div>
                      <div className='text-gray-400 text-sm'>
                        {selectedLocation.schools}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Species Recommendation */}
              {selectedLocation.species && (
                <div className='mb-6 p-4 bg-green-500/10 rounded-xl border border-green-500/20'>
                  <h3 className='font-bold mb-2 flex items-center space-x-2'>
                    <Leaf className='w-5 h-5 text-green-400' />
                    <span>Recommended Species</span>
                  </h3>
                  <p className='text-gray-300 text-sm leading-relaxed'>
                    {selectedLocation.species}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Postal Area Details */}
          {isPostalArea && (
            <div>
              <p className='text-gray-400 mb-6'>
                {selectedLocation.description}
              </p>

              {areaStats && (
                <div>
                  {/* Area Statistics */}
                  <div className='grid grid-cols-3 gap-4 mb-6'>
                    <div className='text-center p-3 bg-gray-700/50 rounded-lg'>
                      <div className='text-2xl font-bold text-lime-400'>
                        {areaStats.totalLocations}
                      </div>
                      <div className='text-xs text-gray-400'>
                        Total Locations
                      </div>
                    </div>
                    <div className='text-center p-3 bg-gray-700/50 rounded-lg'>
                      <div className='text-2xl font-bold text-lime-400'>
                        {areaStats.averageScore}
                      </div>
                      <div className='text-xs text-gray-400'>Average Score</div>
                    </div>
                    <div className='text-center p-3 bg-gray-700/50 rounded-lg'>
                      <div className='text-2xl font-bold text-lime-400'>
                        {areaStats.perfectScores}
                      </div>
                      <div className='text-xs text-gray-400'>
                        Perfect Scores
                      </div>
                    </div>
                  </div>

                  {/* Top Locations in Area */}
                  <div className='mb-6'>
                    <h3 className='font-bold mb-4 flex items-center space-x-2'>
                      <Award className='w-5 h-5 text-yellow-400' />
                      <span>Top 5 Locations in {selectedLocation.name}</span>
                    </h3>
                    <div className='space-y-2'>
                      {areaStats.topLocations.map((location, index) => (
                        <div
                          key={index}
                          className='p-3 bg-gray-700/30 rounded-lg'>
                          <div className='flex justify-between items-center mb-1'>
                            <span className='font-medium'>
                              Rank #{location.rank}
                            </span>
                            <span className='text-lime-400 font-bold'>
                              {location.final_score}/100
                            </span>
                          </div>
                          <div className='text-xs text-gray-400'>
                            {location.location_type} •{" "}
                            {location.residents_nearby}
                          </div>
                          {location.cooling_estimate && (
                            <div className='text-xs text-blue-400 mt-1'>
                              {location.cooling_estimate}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className='space-y-3'>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className='w-full bg-lime-400 text-black font-bold py-3 rounded-xl hover:bg-lime-300 transition-colors flex items-center justify-center space-x-2'>
              <Navigation className='w-4 h-4' />
              <span>Navigate to Location</span>
            </motion.button>

            {isTreeLocation && (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className='w-full bg-gray-700 text-white font-medium py-3 rounded-xl hover:bg-gray-600 transition-colors flex items-center justify-center space-x-2'>
                <TreePine className='w-4 h-4' />
                <span>Plan Tree Planting</span>
              </motion.button>
            )}

            {isPostalArea && (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className='w-full bg-gray-700 text-white font-medium py-3 rounded-xl hover:bg-gray-600 transition-colors flex items-center justify-center space-x-2'>
                <Target className='w-4 h-4' />
                <span>Explore All Locations</span>
              </motion.button>
            )}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default LocationDetailsPanel;
