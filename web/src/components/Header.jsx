/** @format */

import React from "react";
import { motion } from "framer-motion";
import { Sparkles, User, Settings } from "lucide-react";

const Header = () => {
  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className='h-16 bg-dark-800/50 backdrop-blur-md border-b border-white/10 flex items-center justify-between px-6'>
      <div className='flex items-center space-x-4'>
        <div className='flex items-center space-x-2'>
          <Sparkles className='w-8 h-8 text-lime-400' />
          <span className='text-xl font-bold text-green-400'>Forestry</span>
        </div>

        <nav className='hidden md:flex items-center space-x-1'>
          <button className='px-4 py-2 rounded-full bg-white/10 text-sm font-medium'>
            Interactive Map
          </button>
          <button className='px-4 py-2 rounded-full text-sm font-medium hover:bg-white/5 transition-colors'>
            Fresh Data
          </button>
          <button className='px-4 py-2 rounded-full text-sm font-medium hover:bg-white/5 transition-colors flex items-center space-x-1'>
            <span>Locations</span>
            <span className='bg-lime-400 text-black text-xs px-2 py-0.5 rounded-full font-bold'>
              13,882
            </span>
          </button>
        </nav>
      </div>

      <div className='flex items-center space-x-4'>
        <div className='hidden md:flex items-center space-x-2 text-sm'>
          <span className='text-gray-400'>Locations</span>
          <span className='bg-lime-400 text-black px-2 py-1 rounded-full font-bold text-xs'>
            13,882
          </span>
          <span className='text-gray-400 ml-4'>Area</span>
          <span className='text-gray-400 ml-4'>1.39 km²</span>
          <span className='font-bold'>CO₂: 305t/year</span>
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
    </motion.header>
  );
};

export default Header;
