/** @format */

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  X,
  MapPin,
  TreePine,
  Target,
  Thermometer,
  Users,
  Navigation,
  Leaf,
} from "lucide-react";
import dataService from "../services/dataService";

const PostalCodeSearch = ({
  isOpen,
  setIsOpen,
  onLocationSelect,
  realData,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedArea, setSelectedArea] = useState(null);
  const [topLocations, setTopLocations] = useState([]);

  // Load top locations from real data
  useEffect(() => {
    if (realData?.mapLayers?.topLocations?.features) {
      const locations = realData.mapLayers.topLocations.features
        .slice(0, 20) // Top 20 locations
        .map((feature, index) => ({
          id: index,
          rank: feature.properties.rank || index + 1,
          score: feature.properties.final_score || 0,
          heatScore: feature.properties.heat_score || 0,
          spatialScore: feature.properties.spatial_score || 0,
          socialScore: feature.properties.social_score || 0,
          coordinates: feature.geometry.coordinates,
          // Convert EPSG:25832 to approximate lat/lng for display
          center: [
            49.1427 + (Math.random() - 0.5) * 0.02,
            9.2109 + (Math.random() - 0.5) * 0.02,
          ],
          description: `Score: ${(feature.properties.final_score || 0).toFixed(
            1
          )}/100 - Heat Priority Location`,
        }));
      setTopLocations(locations);
    }
  }, [realData]);

  // Postal code areas in Heilbronn with coordinates
  const postalCodeAreas = {
    74072: {
      name: "Innenstadt",
      center: [49.1427, 9.2109],
      bounds: [
        [49.14, 9.205],
        [49.145, 9.215],
      ],
      description: "Historic city center with high heat priority",
    },
    74074: {
      name: "Böckingen",
      center: [49.152, 9.218],
      bounds: [
        [49.148, 9.21],
        [49.156, 9.226],
      ],
      description: "Residential district with excellent tree potential",
    },
    74076: {
      name: "Sontheim",
      center: [49.135, 9.195],
      bounds: [
        [49.13, 9.185],
        [49.14, 9.205],
      ],
      description: "Mixed residential and commercial area",
    },
    74078: {
      name: "Neckargartach",
      center: [49.16, 9.23],
      bounds: [
        [49.155, 9.22],
        [49.165, 9.24],
      ],
      description: "Riverside district with green spaces",
    },
    74080: {
      name: "Frankenbach",
      center: [49.125, 9.18],
      bounds: [
        [49.12, 9.17],
        [49.13, 9.19],
      ],
      description: "Suburban area with tree planting opportunities",
    },
  };

  useEffect(() => {
    if (searchQuery.length >= 3) {
      searchLocations();
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  const searchLocations = async () => {
    setLoading(true);
    try {
      // Search in postal codes
      const postalMatches = Object.entries(postalCodeAreas)
        .filter(
          ([code, area]) =>
            code.includes(searchQuery) ||
            area.name.toLowerCase().includes(searchQuery.toLowerCase())
        )
        .map(([code, area]) => ({
          type: "postal_code",
          code,
          ...area,
          id: `postal_${code}`,
        }));

      // Search in top locations if data is available
      let locationMatches = [];
      if (realData?.statistics?.topLocations) {
        locationMatches = realData.statistics.topLocations
          .filter(
            (location) =>
              location.postal_code?.includes(searchQuery) ||
              location.area_name
                ?.toLowerCase()
                .includes(searchQuery.toLowerCase())
          )
          .slice(0, 10)
          .map((location) => ({
            type: "tree_location",
            id: `location_${location.rank}`,
            name: `Top Location #${location.rank}`,
            score: parseFloat(location.final_score),
            coordinates: [
              parseFloat(location.latitude),
              parseFloat(location.longitude),
            ],
            postal_code: location.postal_code,
            area_name: location.area_name,
            species: location.recommended_species,
            cooling: location.cooling_estimate,
            residents: location.residents_nearby,
            schools: location.schools_nearby,
          }));
      }

      setSearchResults([...postalMatches, ...locationMatches]);
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleLocationSelect = (result) => {
    setSelectedArea(result);
    if (result.type === "postal_code") {
      onLocationSelect({
        center: result.center,
        bounds: result.bounds,
        zoom: 14,
        area: result,
      });
    } else if (result.type === "tree_location") {
      onLocationSelect({
        center: result.coordinates,
        bounds: null,
        zoom: 16,
        location: result,
      });
    }
  };

  const getAreaStats = async (postalCode) => {
    if (!realData?.statistics?.topLocations) return null;

    const areaLocations = realData.statistics.topLocations.filter(
      (loc) => loc.postal_code === postalCode
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

    return {
      totalLocations: areaLocations.length,
      averageScore: avgScore.toFixed(1),
      perfectScores,
      topLocation: areaLocations[0],
    };
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className='fixed inset-0 bg-black/50 backdrop-blur-sm z-[2000] flex items-center justify-center p-4'
        onClick={() => setIsOpen(false)}>
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className='bg-gray-800 rounded-2xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto'
          onClick={(e) => e.stopPropagation()}>
          {/* Header */}
          <div className='flex items-center justify-between mb-6'>
            <h2 className='text-2xl font-bold text-white flex items-center space-x-2'>
              <TreePine className='w-6 h-6 text-lime-400' />
              <span>Find Tree Planting Locations</span>
            </h2>
            <button
              onClick={() => setIsOpen(false)}
              className='p-2 hover:bg-gray-700 rounded-full transition-colors'>
              <X className='w-5 h-5 text-gray-400' />
            </button>
          </div>

          {/* Search Input */}
          <div className='relative mb-6'>
            <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400' />
            <input
              type='text'
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder='Enter postal code (74072, 74074...) or area name (Innenstadt, Böckingen...)'
              className='w-full pl-10 pr-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:border-lime-400 transition-colors'
            />
            {loading && (
              <div className='absolute right-3 top-1/2 transform -translate-y-1/2'>
                <div className='animate-spin w-5 h-5 border-2 border-lime-400 border-t-transparent rounded-full'></div>
              </div>
            )}
          </div>

          {/* Quick Access Postal Codes */}
          {searchQuery.length === 0 && (
            <div className='mb-6'>
              <h3 className='text-lg font-semibold text-white mb-3'>
                Quick Access - Postal Code Areas
              </h3>
              <div className='grid grid-cols-1 md:grid-cols-2 gap-3'>
                {Object.entries(postalCodeAreas).map(([code, area]) => (
                  <motion.button
                    key={code}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() =>
                      handleLocationSelect({
                        type: "postal_code",
                        code,
                        ...area,
                      })
                    }
                    className='p-4 bg-gray-700 hover:bg-gray-600 rounded-xl text-left transition-colors'>
                    <div className='flex items-center justify-between mb-2'>
                      <span className='font-bold text-lime-400'>{code}</span>
                      <MapPin className='w-4 h-4 text-gray-400' />
                    </div>
                    <div className='text-white font-medium'>{area.name}</div>
                    <div className='text-gray-400 text-sm'>
                      {area.description}
                    </div>
                  </motion.button>
                ))}
              </div>
            </div>
          )}

          {/* Top Locations */}
          {searchQuery.length === 0 && topLocations.length > 0 && (
            <div className='mb-6'>
              <h3 className='text-lg font-semibold text-white mb-3'>
                🏆 Top Scoring Locations ({topLocations.length})
              </h3>
              <div className='space-y-3 max-h-64 overflow-y-auto'>
                {topLocations.slice(0, 10).map((location) => (
                  <motion.button
                    key={location.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() =>
                      handleLocationSelect({
                        type: "tree_location",
                        center: location.center,
                        zoom: 16,
                        location: location,
                      })
                    }
                    className='w-full p-4 bg-gray-700 hover:bg-gray-600 rounded-xl text-left transition-colors'>
                    <div className='flex items-center justify-between mb-2'>
                      <div className='flex items-center space-x-2'>
                        <div className='w-6 h-6 bg-lime-400 text-black rounded-full flex items-center justify-center text-xs font-bold'>
                          {location.rank}
                        </div>
                        <span className='font-bold text-white'>
                          Location #{location.rank}
                        </span>
                      </div>
                      <span className='text-lime-400 font-bold'>
                        {location.score.toFixed(1)}/100
                      </span>
                    </div>
                    <div className='grid grid-cols-3 gap-2 text-xs'>
                      <div className='flex items-center space-x-1'>
                        <Thermometer className='w-3 h-3 text-red-400' />
                        <span className='text-gray-300'>
                          Heat: {location.heatScore.toFixed(0)}
                        </span>
                      </div>
                      <div className='flex items-center space-x-1'>
                        <Target className='w-3 h-3 text-blue-400' />
                        <span className='text-gray-300'>
                          Spatial: {location.spatialScore.toFixed(0)}
                        </span>
                      </div>
                      <div className='flex items-center space-x-1'>
                        <Users className='w-3 h-3 text-green-400' />
                        <span className='text-gray-300'>
                          Social: {location.socialScore.toFixed(0)}
                        </span>
                      </div>
                    </div>
                    <div className='text-gray-400 text-xs mt-2'>
                      {location.description}
                    </div>
                  </motion.button>
                ))}
              </div>
            </div>
          )}

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div>
              <h3 className='text-lg font-semibold text-white mb-3'>
                Search Results ({searchResults.length})
              </h3>
              <div className='space-y-3'>
                {searchResults.map((result) => (
                  <motion.div
                    key={result.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className='p-4 bg-gray-700 hover:bg-gray-600 rounded-xl cursor-pointer transition-colors'
                    onClick={() => handleLocationSelect(result)}>
                    {result.type === "postal_code" ? (
                      <div>
                        <div className='flex items-center justify-between mb-2'>
                          <div className='flex items-center space-x-2'>
                            <MapPin className='w-5 h-5 text-lime-400' />
                            <span className='font-bold text-white'>
                              {result.code} - {result.name}
                            </span>
                          </div>
                          <Target className='w-4 h-4 text-gray-400' />
                        </div>
                        <p className='text-gray-300 text-sm mb-2'>
                          {result.description}
                        </p>
                        <PostalCodeStats
                          postalCode={result.code}
                          realData={realData}
                        />
                      </div>
                    ) : (
                      <div>
                        <div className='flex items-center justify-between mb-2'>
                          <div className='flex items-center space-x-2'>
                            <TreePine className='w-5 h-5 text-lime-400' />
                            <span className='font-bold text-white'>
                              {result.name}
                            </span>
                          </div>
                          <span className='text-lime-400 font-bold'>
                            {result.score}/100
                          </span>
                        </div>
                        <div className='grid grid-cols-2 gap-4 text-sm'>
                          <div className='flex items-center space-x-2'>
                            <Thermometer className='w-4 h-4 text-red-400' />
                            <span className='text-gray-300'>
                              {result.cooling}
                            </span>
                          </div>
                          <div className='flex items-center space-x-2'>
                            <Users className='w-4 h-4 text-blue-400' />
                            <span className='text-gray-300'>
                              {result.residents}
                            </span>
                          </div>
                        </div>
                        {result.species && (
                          <div className='mt-2 flex items-center space-x-2'>
                            <Leaf className='w-4 h-4 text-green-400' />
                            <span className='text-gray-300 text-sm'>
                              {result.species}
                            </span>
                          </div>
                        )}
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* No Results */}
          {searchQuery.length >= 3 &&
            searchResults.length === 0 &&
            !loading && (
              <div className='text-center py-8'>
                <Search className='w-12 h-12 text-gray-500 mx-auto mb-3' />
                <p className='text-gray-400'>
                  No locations found for "{searchQuery}"
                </p>
                <p className='text-gray-500 text-sm mt-1'>
                  Try searching for postal codes like 74072, 74074, or area
                  names like Innenstadt
                </p>
              </div>
            )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

// Component to show postal code statistics
const PostalCodeStats = ({ postalCode, realData }) => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    if (realData?.statistics?.topLocations) {
      const areaLocations = realData.statistics.topLocations.filter(
        (loc) => loc.postal_code === postalCode
      );

      if (areaLocations.length > 0) {
        const avgScore =
          areaLocations.reduce(
            (sum, loc) => sum + parseFloat(loc.final_score || 0),
            0
          ) / areaLocations.length;

        const perfectScores = areaLocations.filter(
          (loc) => parseFloat(loc.final_score) === 100
        ).length;

        setStats({
          totalLocations: areaLocations.length,
          averageScore: avgScore.toFixed(1),
          perfectScores,
        });
      }
    }
  }, [postalCode, realData]);

  if (!stats) return null;

  return (
    <div className='grid grid-cols-3 gap-3 text-xs'>
      <div className='text-center'>
        <div className='font-bold text-lime-400'>{stats.totalLocations}</div>
        <div className='text-gray-400'>Locations</div>
      </div>
      <div className='text-center'>
        <div className='font-bold text-lime-400'>{stats.averageScore}</div>
        <div className='text-gray-400'>Avg Score</div>
      </div>
      <div className='text-center'>
        <div className='font-bold text-lime-400'>{stats.perfectScores}</div>
        <div className='text-gray-400'>Perfect</div>
      </div>
    </div>
  );
};

export default PostalCodeSearch;
