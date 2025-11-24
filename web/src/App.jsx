/** @format */

import React, { useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useNavigate,
  useLocation,
} from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import MainLayout from "./components/MainLayout";

const AppContent = () => {
  return <MainLayout />;
};

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
