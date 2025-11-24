/** @format */

import React from "react";
import { motion } from "framer-motion";
import {
  Map,
  Plus,
  Settings,
  Compass,
  BookOpen,
  Clock,
  Target,
} from "lucide-react";

const Sidebar = ({ activeView, setActiveView }) => {
  const menuItems = [
    { id: "map", icon: Map, label: "Interactive Map" },
    { id: "fresh-data", icon: Target, label: "Fresh Data" },
    { id: "data-explorer", icon: Compass, label: "Data & Exclusions" },
    { id: "fresh-explorer", icon: Clock, label: "Fresh Explorer" },
    { id: "complete-map", icon: BookOpen, label: "Complete Map" },
    { id: "documentation", icon: BookOpen, label: "Documentation" },
  ];

  return (
    <motion.aside
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className='w-16 bg-dark-800/30 backdrop-blur-md border-r border-white/10 flex flex-col items-center py-6 space-y-4'>
      <button className='p-3 bg-lime-400 text-black rounded-xl hover:scale-105 transition-transform'>
        <Plus className='w-6 h-6' />
      </button>

      <div className='w-8 h-px bg-white/20 my-4' />

      <nav className='flex flex-col space-y-2'>
        {menuItems.map((item) => (
          <motion.button
            key={item.id}
            onClick={() => setActiveView(item.id)}
            className={`p-3 rounded-xl transition-all duration-200 group relative ${
              activeView === item.id
                ? "bg-lime-400 text-black"
                : "text-gray-400 hover:text-white hover:bg-white/10"
            }`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}>
            <item.icon className='w-6 h-6' />

            {/* Tooltip */}
            <div className='absolute left-full ml-2 px-2 py-1 bg-gray-700 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none'>
              {item.label}
            </div>
          </motion.button>
        ))}
      </nav>

      <div className='flex-1' />

      <button className='p-3 text-gray-400 hover:text-white hover:bg-white/10 rounded-xl transition-all'>
        <Settings className='w-6 h-6' />
      </button>
    </motion.aside>
  );
};

export default Sidebar;
