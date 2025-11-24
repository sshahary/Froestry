/** @format */

import { useState } from "react";
import { motion } from "framer-motion";
import { Send, MapPin, Mic, Bot, TreePine } from "lucide-react";
import aiLocationService from "../services/aiLocationService";

const ChatAssistant = ({ onShowLocations }) => {
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: "assistant",
      content:
        "Hello! I'm your AI assistant for Heilbronn Tree Planting. Ask me something like <strong>“2 best locations in Heilbronn for tree planting?”</strong>",
    },
  ]);

  const handleSendMessage = async () => {
    if (!message.trim() || isLoading) return;

    const userQuery = message.trim();

    // add user message
    const userMsg = {
      id: messages.length + 1,
      type: "user",
      content: userQuery,
    };
    setMessages((prev) => [...prev, userMsg]);
    setMessage("");
    setIsLoading(true);

    try {
      // 🔹 ALWAYS call backend AI
      const aiResult = await aiLocationService.getTreeLocations(userQuery);

      const assistantMsg = {
        id: userMsg.id + 1,
        type: "assistant",
        content: aiResult.message || "I received your question from the AI.",
        locations: aiResult.locations || [],
        hasLocations:
          Array.isArray(aiResult.locations) && aiResult.locations.length > 0,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error("Chat error:", err);

      const assistantMsg = {
        id: userMsg.id + 1,
        type: "assistant",
        content:
          "Sorry, I couldn't reach the AI service right now. Please try again in a moment.",
        locations: [],
        hasLocations: false,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleShowLocations = (locations) => {
    if (onShowLocations && locations && locations.length > 0) {
      onShowLocations(locations);
    }
  };

  return (
    <div className='h-full flex flex-col bg-gray-900 text-white'>
      {/* Header */}
      <div className='h-16 border-b border-gray-800 px-6 flex items-center justify-between bg-gray-900/90 backdrop-blur'>
        <div className='flex items-center space-x-3'>
          <div className='flex items-center justify-center w-10 h-10 rounded-full bg-lime-400'>
            <Bot className='w-6 h-6 text-black' />
          </div>
          <div>
            <div className='flex items-center space-x-2'>
              <TreePine className='w-5 h-5 text-lime-400' />
              <h2 className='text-lg font-semibold'>Forestry AI Assistant</h2>
            </div>
            <p className='text-xs text-gray-400'>
              I use the backend AI service to find the best tree planting spots
              in Heilbronn.
            </p>
          </div>
        </div>

        <div className='hidden md:flex items-center space-x-3 text-xs text-gray-400'>
          <span className='flex items-center space-x-1'>
            <span className='w-2 h-2 rounded-full bg-lime-400'></span>
            <span>Connected</span>
          </span>
        </div>
      </div>

      {/* Messages */}
      <div className='flex-1 overflow-y-auto px-6 py-4 space-y-4'>
        {messages.map((msg) => (
          <motion.div
            key={msg.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${
              msg.type === "user" ? "justify-end" : "justify-start"
            }`}>
            <div
              className={`max-w-2xl ${
                msg.type === "user" ? "ml-auto" : "mr-auto"
              }`}>
              <div
                className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.type === "user"
                    ? "bg-lime-400 text-black"
                    : "bg-gray-800 text-white"
                }`}>
                <div dangerouslySetInnerHTML={{ __html: msg.content }} />

                {msg.hasLocations && msg.locations && (
                  <button
                    onClick={() => handleShowLocations(msg.locations)}
                    className='mt-3 w-full bg-lime-400 text-black py-2 px-4 rounded-lg font-semibold hover:bg-lime-300 transition-colors flex items-center justify-center space-x-2'>
                    <MapPin className='w-4 h-4' />
                    <span>🗺️ Show {msg.locations.length} Locations on Map</span>
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        ))}

        {isLoading && (
          <div className='flex items-center space-x-2 text-sm text-gray-400'>
            <div className='w-5 h-5 border-2 border-lime-400 border-t-transparent rounded-full animate-spin' />
            <span>AI is analyzing your request…</span>
          </div>
        )}
      </div>

      {/* Input */}
      <div className='border-t border-gray-800 px-6 py-3 bg-gray-900/95'>
        <div className='max-w-3xl mx-auto flex items-center space-x-2'>
          <input
            type='text'
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
            placeholder='Ask: "2 best locations in Heilbronn for trees"'
            className='flex-1 bg-gray-800 border border-gray-700 rounded-full px-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-lime-400'
          />
          <button className='p-2 text-gray-400 hover:text-white transition-colors'>
            <Mic className='w-5 h-5' />
          </button>
          <button
            onClick={handleSendMessage}
            disabled={!message.trim() || isLoading}
            className='p-2 rounded-full bg-lime-400 text-black hover:bg-lime-300 disabled:opacity-50'>
            <Send className='w-5 h-5' />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatAssistant;
