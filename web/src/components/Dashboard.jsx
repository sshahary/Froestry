/** @format */

import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  TreePine,
  MapPin,
  Award,
  Leaf,
  Database,
  Bot,
  Map,
  BarChart3,
  Sparkles,
  ArrowUpRight,
  CheckCircle,
} from "lucide-react";

const Dashboard = () => {
  const navigate = useNavigate();
  const heroStats = [
    {
      label: "Full Analysis",
      value: "114,982",
      color: "text-blue-400",
      description: "Total locations analyzed",
    },
    {
      label: "Fresh Data ✅",
      value: "13,882",
      color: "text-green-400",
      description: "Verified 2020+ data",
      highlight: true,
    },
  ];

  const mainStats = [
    {
      icon: "🆕",
      value: "13,882",
      label: "Verified Fresh Locations",
      sublabel: "✅ 12.1% of total (2020+ data)",
      color: "text-green-400",
    },
    {
      icon: "🗺️",
      value: "1.39 km²",
      label: "Fresh Plantable Area",
      sublabel: "Verified current zones",
      color: "text-blue-400",
    },
    {
      icon: "🏆",
      value: "100/100",
      label: "Top Score",
      sublabel: "5 perfect locations found",
      color: "text-yellow-400",
    },
    {
      icon: "🌱",
      value: "305 tonnes",
      label: "CO₂ Reduction/year",
      sublabel: "Est. 15,000 trees potential",
      color: "text-lime-400",
    },
  ];

  const comparisonData = [
    {
      metric: "Tree Locations",
      fullAnalysis: "114,982",
      freshData: "13,882",
    },
    {
      metric: "Plantable Area",
      fullAnalysis: "11.50 km²",
      freshData: "1.39 km²",
    },
    {
      metric: "Top Score",
      fullAnalysis: "100/100",
      freshData: "100/100",
    },
    {
      metric: "Average Score",
      fullAnalysis: "59.13",
      freshData: "63.93 ⬆️",
    },
    {
      metric: "Data Quality",
      fullAnalysis: "Mixed (2013-2025)",
      freshData: "✅ Verified (2020-2025)",
    },
  ];

  const navigationCards = [
    {
      id: "complete-map",
      icon: Map,
      title: "Interactive Map",
      description:
        "Explore all layers: heat map, exclusion zones, green spaces, and plantable areas.",
      highlight: true,
      color: "from-green-600 to-green-400",
    },
    {
      id: "chat",
      icon: Bot,
      title: "AI Chat Assistant",
      description:
        "Ask questions about tree locations, heat priorities, and environmental impact.",
      highlight: false,
      color: "from-blue-600 to-blue-400",
    },
    {
      id: "data-explorer",
      icon: Database,
      title: "Data & Exclusions",
      description:
        "Explore the 8 datasets analyzed and 32,557 features excluded for safe tree planting.",
      highlight: false,
      color: "from-purple-600 to-purple-400",
    },
    {
      id: "fresh-data",
      icon: Sparkles,
      title: "Fresh Data Locations",
      description:
        "Tree locations verified with current data (2020+) - FIELD TESTED! High accuracy for real-world deployment.",
      highlight: true,
      color: "from-lime-600 to-lime-400",
    },
    {
      id: "fresh-explorer",
      icon: CheckCircle,
      title: "Fresh Data Explorer ✅",
      description:
        "13,882 locations verified with 2020+ data. Scientific discovery: data freshness matters!",
      highlight: true,
      color: "from-emerald-600 to-emerald-400",
    },
    {
      id: "complete-map",
      icon: MapPin,
      title: "Fresh Complete Map 🆕",
      description:
        "All layers visualized: 13,882 verified locations + fresh buildings + roads + trees + water. The WOW factor!",
      highlight: true,
      color: "from-teal-600 to-teal-400",
    },
  ];

  return (
    <div className='min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white overflow-y-auto'>
      <div className='max-w-7xl mx-auto px-6 py-12'>
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className='text-center mb-12'>
          <h1 className='text-6xl font-bold mb-4 bg-gradient-to-r from-green-400 via-lime-400 to-green-500 bg-clip-text text-transparent'>
            🌳 Heilbronn Tree Planting System
          </h1>
          <p className='text-2xl text-gray-300 opacity-90'>
            AI-Powered Urban Forestry Platform
          </p>
        </motion.div>

        {/* Hero Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className='mb-12'>
          <div className='flex justify-center mb-8'>
            <div className='flex gap-6 bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20'>
              {heroStats.map((stat, index) => (
                <div key={index} className='text-center'>
                  <div className='text-sm text-gray-400 mb-1'>{stat.label}</div>
                  <div
                    className={`text-3xl font-bold ${stat.color} ${
                      stat.highlight ? "animate-pulse" : ""
                    }`}>
                    {stat.value}
                  </div>
                  <div className='text-xs text-gray-500 mt-1'>
                    {stat.description}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Main Stats Grid */}
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12'>
            {mainStats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                className='bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20 text-center hover:bg-white/15 transition-all duration-300'>
                <div className='text-4xl mb-4'>{stat.icon}</div>
                <div className={`text-3xl font-bold mb-2 ${stat.color}`}>
                  {stat.value}
                </div>
                <div className='text-white font-medium mb-2'>{stat.label}</div>
                <div className='text-xs text-gray-400'>{stat.sublabel}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Comparison Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className='mb-12'>
          <div className='bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20'>
            <h2 className='text-3xl font-bold text-center mb-8 text-green-400'>
              📊 Key Metrics Comparison
            </h2>

            <div className='overflow-x-auto'>
              <table className='w-full'>
                <thead>
                  <tr className='border-b border-white/20'>
                    <th className='text-left py-4 px-6 font-bold text-gray-300'>
                      Metric
                    </th>
                    <th className='text-center py-4 px-6 font-bold text-gray-300'>
                      Full Analysis
                    </th>
                    <th className='text-center py-4 px-6 font-bold text-green-400 bg-green-500/20 rounded-lg'>
                      Fresh Data ✅
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonData.map((row, index) => (
                    <motion.tr
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.7 + index * 0.1 }}
                      className='border-b border-white/10 hover:bg-white/5 transition-colors'>
                      <td className='py-4 px-6 font-medium'>{row.metric}</td>
                      <td className='py-4 px-6 text-center text-gray-400'>
                        {row.fullAnalysis}
                      </td>
                      <td className='py-4 px-6 text-center font-bold text-green-400 bg-green-500/10'>
                        {row.freshData}
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>

        {/* Navigation Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}>
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
            {navigationCards.map((card, index) => (
              <motion.div
                key={card.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.9 + index * 0.1 }}
                onClick={() => navigate(`/${card.id}`)}
                className={`
                  relative group cursor-pointer rounded-2xl p-8 border transition-all duration-300 hover:scale-105 hover:shadow-2xl
                  ${
                    card.highlight
                      ? `bg-gradient-to-br ${card.color} border-white/30 text-white`
                      : "bg-white/10 backdrop-blur-md border-white/20 hover:bg-white/15"
                  }
                `}>
                <div className='flex items-start justify-between mb-6'>
                  <card.icon className='w-12 h-12 flex-shrink-0' />
                  <ArrowUpRight className='w-5 h-5 opacity-0 group-hover:opacity-100 transition-opacity' />
                </div>

                <h3 className='text-2xl font-bold mb-4'>{card.title}</h3>
                <p
                  className={`text-sm leading-relaxed ${
                    card.highlight ? "text-white/90" : "text-gray-300"
                  }`}>
                  {card.description}
                </p>

                {card.highlight && (
                  <div className='absolute top-4 right-4'>
                    <div className='w-3 h-3 bg-white rounded-full animate-pulse'></div>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className='text-center mt-16 text-gray-400'>
          <p className='text-sm'>
            Powered by AI • Verified with 2020+ Data • Ready for Deployment
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;
