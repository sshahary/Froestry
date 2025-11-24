/** @format */

import { useState, useEffect } from "react";
import dataService from "../services/dataService";
import RealMapView from "./RealMapView";
import PostalCodeSearch from "./PostalCodeSearch";
import LocationDetailsPanel from "./LocationDetailsPanel";
import DataExplorer from "./DataExplorer";
import FreshDataExplorer from "./FreshDataExplorer";
import CompleteMap from "./CompleteMap";
import ChatAssistant from "./ChatAssistant";
import Dashboard from "./Dashboard";
import {
  TreePine,
  Map,
  Database,
  Bot,
  Settings,
  User,
  Plus,
  Target,
  Sparkles,
  Layers,
} from "lucide-react";

const MainLayout = () => {
  const [activeView, setActiveView] = useState("dashboard");
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [realData, setRealData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [mapCenter, setMapCenter] = useState([49.1427, 9.2109]);
  const [mapZoom, setMapZoom] = useState(13);
  const [aiLocations, setAiLocations] = useState([]);

  // Load real data on component mount
  useEffect(() => {
    const loadData = async () => {
      try {
        const [mapLayers, statistics] = await Promise.all([
          dataService.loadMapLayers(),
          dataService.loadStatistics(),
        ]);

        setRealData({
          mapLayers,
          statistics,
        });
      } catch (error) {
        console.error("Error loading data:", error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const handleLocationSelect = (locationData) => {
    setMapCenter(locationData.center);
    setMapZoom(locationData.zoom);
    setSelectedLocation(locationData.location || locationData.area);
    setIsSearchOpen(false);
    setActiveView("map");
  };

  // Called by ChatAssistant when user hits "Show X Locations on Map"
  const handleShowLocationsFromAI = (locations) => {
    if (!locations || locations.length === 0) return;

    const first = locations[0];
    const lat = first.lat ?? first.latitude ?? null;
    const lng = first.lng ?? first.longitude ?? null;

    if (lat != null && lng != null) {
      setMapCenter([lat, lng]);
      setMapZoom(16);
    }

    setAiLocations(locations);
    setSelectedLocation({ source: "ai", ...first });
    setActiveView("map");
  };

  // Dynamic stats from real data
  const getStats = () => {
    if (!realData?.statistics?.stats) {
      return {
        locations: loading ? "Loading..." : "0",
        freshLocations: loading ? "Loading..." : "0",
        area: loading ? "Loading..." : "0 km²",
        freshArea: loading ? "Loading..." : "0 km²",
        co2: loading ? "Loading..." : "0t",
        totalArea: loading ? "Loading..." : "0 km²",
        totalLocations: loading ? "Loading..." : "0",
        topScore: loading ? "Loading..." : "0",
        averageScore: loading ? "Loading..." : "0",
        topLocations: loading ? "Loading..." : "0",
        perfectLocations: loading ? "Loading..." : "0",
      };
    }

    const stats = realData.statistics.stats;
    return {
      locations: stats.totalLocations?.toLocaleString() || "0",
      freshLocations: stats.freshLocations?.toLocaleString() || "0",
      area: stats.plantableArea || "0 km²",
      freshArea: stats.freshPlantableArea || "0 km²",
      co2: stats.co2Reduction || "0t",
      totalArea: stats.plantableArea || "0 km²",
      totalLocations: stats.totalLocations?.toLocaleString() || "0",
      topScore: stats.topScore || "0",
      averageScore: stats.averageScore || "0",
      topLocations: stats.topLocations?.toLocaleString() || "0",
      perfectLocations: stats.perfectLocations?.toLocaleString() || "0",
    };
  };

  const currentStats = getStats();

  const menuItems = [
    { id: "dashboard", icon: Target, label: "Dashboard" },
    { id: "map", icon: Map, label: "Interactive Map" },
    { id: "data", icon: Database, label: "Data Explorer" },
    { id: "complete", icon: Layers, label: "Complete Map" },
    { id: "fresh", icon: Sparkles, label: "Fresh Data" },
    { id: "chat", icon: Bot, label: "AI Assistant" },
  ];

  return (
    <div className='h-screen bg-gray-900 text-white flex overflow-hidden'>
      {/* Header */}
      <div className='fixed top-0 left-0 right-0 h-16 bg-gray-800/50 backdrop-blur-md border-b border-white/10 flex items-center justify-between px-6 z-50'>
        <div className='flex items-center space-x-4'>
          <div className='flex items-center space-x-2'>
            <TreePine className='w-8 h-8 text-lime-400' />
            <span className='text-xl font-bold text-green-400'>Forestry</span>
          </div>

          <nav className='hidden md:flex items-center space-x-1'>
            <button
              onClick={() => {
                setMapCenter([49.1427, 9.2109]);
                setMapZoom(13);
                setSelectedLocation(null);
                setActiveView("map");
              }}
              className='px-4 py-2 rounded-full bg-white/10 text-sm font-medium hover:bg-white/20 transition-colors'>
              New Analysis
            </button>
            <button
              onClick={() => setActiveView("complete")}
              className='px-4 py-2 rounded-full text-sm font-medium hover:bg-white/5 transition-colors'>
              Explore
            </button>
            <button
              onClick={() => setActiveView("data")}
              className='px-4 py-2 rounded-full text-sm font-medium hover:bg-white/5 transition-colors flex items-center space-x-1'>
              <span>Top Locations</span>
              <span className='bg-lime-400 text-black text-xs px-2 py-0.5 rounded-full font-bold'>
                {currentStats.topLocations}
              </span>
            </button>
          </nav>
        </div>

        <div className='flex items-center space-x-4'>
          <div className='hidden md:flex items-center space-x-2 text-sm'>
            <span className='text-gray-400'>Total</span>
            <span className='bg-lime-400 text-black px-2 py-1 rounded-full font-bold text-xs'>
              {currentStats.locations}
            </span>
            <span className='text-gray-400 ml-2'>Fresh</span>
            <span className='bg-green-400 text-black px-2 py-1 rounded-full font-bold text-xs'>
              {currentStats.freshLocations}
            </span>
            <span className='text-gray-400 ml-4'>
              Score: {currentStats.averageScore}
            </span>
            <span className='font-bold'>CO₂: {currentStats.co2}/year</span>
            <span className='text-green-400 text-xs ml-2'>⚡ Optimized</span>
          </div>

          <div className='flex items-center space-x-2'>
            <button className='p-2 hover:bg-white/10 rounded-full transition-colors'>
              <Settings className='w-5 h-5' />
            </button>
            <div className='flex items-center space-x-2 bg-white/10 rounded-full px-3 py-1'>
              <div className='w-6 h-6 bg-lime-400 rounded-full flex items-center justify-center'>
                <User className='w-4 h-4 text-black' />
              </div>
              <span className='text-sm font-medium'>Tree Planner</span>
            </div>
          </div>
        </div>
      </div>

      {/* Sidebar */}
      <div className='w-16 bg-gray-800/30 backdrop-blur-md border-r border-white/10 flex flex-col items-center py-6 space-y-4 mt-16'>
        <button
          onClick={() => setIsSearchOpen(true)}
          className='p-3 bg-lime-400 text-black rounded-xl hover:scale-105 transition-transform'
          title='Find Tree Planting Locations'>
          <Plus className='w-6 h-6' />
        </button>

        <div className='w-8 h-px bg-white/20 my-4' />

        <nav className='flex flex-col space-y-2'>
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              className={`p-3 rounded-xl transition-all duration-200 group relative ${
                activeView === item.id
                  ? "bg-lime-400 text-black"
                  : "text-gray-400 hover:text-white hover:bg-white/10"
              }`}>
              <item.icon className='w-6 h-6' />

              <div className='absolute left-full ml-2 px-2 py-1 bg-gray-700 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none'>
                {item.label}
              </div>
            </button>
          ))}
        </nav>

        <div className='flex-1' />

        <button className='p-3 text-gray-400 hover:text-white hover:bg-white/10 rounded-xl transition-all'>
          <Settings className='w-6 h-6' />
        </button>
      </div>

      {/* Main Content Area */}
      <div className='flex-1 flex mt-16'>
        {/* Left panel only for map view */}
        {activeView === "map" && (
          <div className='w-80 bg-gray-800/30 border-r border-white/10 p-4 overflow-y-auto'>
            <div className='mb-4'>
              <div className='text-lg font-bold text-white mb-2'>Live Data</div>
              <div className='space-y-2 text-sm'>
                <div className='flex justify-between'>
                  <span className='text-gray-400'>Total Locations:</span>
                  <span className='text-lime-400'>
                    {currentStats.locations}
                  </span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-gray-400'>Fresh Locations:</span>
                  <span className='text-green-400'>
                    {currentStats.freshLocations}
                  </span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-gray-400'>Top Score:</span>
                  <span className='text-yellow-400'>
                    {currentStats.topScore}
                  </span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-gray-400'>Avg Score:</span>
                  <span className='text-blue-400'>
                    {currentStats.averageScore}
                  </span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-gray-400'>CO₂/year:</span>
                  <span className='text-lime-400'>{currentStats.co2}</span>
                </div>
              </div>
            </div>

            <div className='space-y-2'>
              <button
                onClick={() => setIsSearchOpen(true)}
                className='w-full p-2 bg-lime-400 text-black rounded text-sm font-medium hover:bg-lime-300 transition-colors'>
                Search Location
              </button>
              <button
                onClick={() => {
                  if (realData?.mapLayers?.topLocations?.features?.[0]) {
                    const topLocation =
                      realData.mapLayers.topLocations.features[0];
                    setMapCenter([49.1427, 9.2109]);
                    setMapZoom(15);
                    setSelectedLocation(topLocation);
                  } else {
                    setMapCenter([49.1427, 9.2109]);
                    setMapZoom(13);
                  }
                }}
                className='w-full p-2 bg-gray-700 text-white rounded text-sm hover:bg-gray-600 transition-colors'>
                Best Location
              </button>
            </div>
          </div>
        )}

        {/* Main content */}
        <div className='flex-1 relative bg-gray-900'>
          {activeView === "dashboard" && (
            <div className='h-full p-8 overflow-y-auto'>
              <Dashboard />
            </div>
          )}
          {activeView === "map" && (
            <RealMapView
              realData={realData}
              center={mapCenter}
              zoom={mapZoom}
              selectedLocation={selectedLocation}
              aiLocations={aiLocations}
            />
          )}
          {activeView === "data" && (
            <DataExplorer
              realData={realData}
              center={mapCenter}
              zoom={mapZoom}
              selectedLocation={selectedLocation}
            />
          )}
          {activeView === "complete" && <CompleteMap realData={realData} />}
          {activeView === "fresh" && <FreshDataExplorer realData={realData} />}
          {activeView === "chat" && (
            <ChatAssistant onShowLocations={handleShowLocationsFromAI} />
          )}
          {/* {activeView === "chat" && (
            <ChatAssistant
              variant='full'
              onShowLocations={handleShowLocationsFromAI}
            />
          )} */}
        </div>
      </div>

      <PostalCodeSearch
        isOpen={isSearchOpen}
        setIsOpen={setIsSearchOpen}
        onLocationSelect={handleLocationSelect}
        realData={realData}
      />

      <LocationDetailsPanel
        selectedLocation={selectedLocation}
        setSelectedLocation={setSelectedLocation}
        realData={realData}
      />
    </div>
  );
};

export default MainLayout;
