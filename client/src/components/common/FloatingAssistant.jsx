import React, { useState, useContext } from 'react';
import { Bot, X, Send, Sparkles, User, RefreshCw } from 'lucide-react';
import { plannerService } from '../../services/plannerService';
import { TripContext } from '../../context/TripContext';

export const FloatingAssistant = () => {
  const { currentTrip } = useContext(TripContext);
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { sender: 'agent', message: 'Hello! I am your TripGenie AI assistant. Ask me to refine your travel itinerary, recommend luxury hotels, suggest vegetarian dining spots, or check destination weather!' }
  ]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userText = input;
    setInput('');
    setMessages(prev => [...prev, { sender: 'user', message: userText }]);
    setSending(true);

    try {
      const tripId = currentTrip?.id || currentTrip?._id;
      const res = await plannerService.sendChatMessage(userText, tripId);
      if (res.offline) {
        setMessages(prev => [...prev, { sender: 'agent', message: 'Backend server is offline.' }]);
      } else {
        setMessages(prev => [...prev, { sender: 'agent', message: res.reply || 'Backend server is offline.' }]);
      }
    } catch (err) {
      console.error("[Chatbot Error]", err);
      setMessages(prev => [...prev, { sender: 'agent', message: 'Backend server is offline.' }]);
    } finally {
      setSending(false);
    }
  };


  return (
    <div className="fixed bottom-6 right-6 z-50">
      {!isOpen ? (
        <button
          onClick={() => setIsOpen(true)}
          className="relative group p-4 rounded-full bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 text-white shadow-2xl shadow-emerald-500/40 hover:scale-110 transition-all duration-300 flex items-center justify-center"
          title="Open Floating AI Assistant"
        >
          <Bot className="w-7 h-7 animate-bounce-slow" />
          <span className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-cyan-400 border-2 border-slate-950 animate-ping"></span>
        </button>
      ) : (
        <div className="w-[360px] sm:w-[400px] h-[520px] rounded-3xl glass-panel border border-slate-700/80 shadow-2xl flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-5">
          
          {/* Header */}
          <div className="px-5 py-4 bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/60 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center">
                <Bot className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white flex items-center gap-1.5">
                  TripGenie Assistant <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                </h4>
                <span className="text-[10px] text-emerald-400 font-semibold tracking-wide uppercase">LangGraph Autonomous Swarm</span>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1.5 rounded-full bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-all"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Messages list */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-slate-950/60 text-xs">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.sender === 'agent' && (
                  <div className="w-6 h-6 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center shrink-0">
                    <Bot className="w-3.5 h-3.5 text-emerald-400" />
                  </div>
                )}
                <div
                  className={`p-3 rounded-2xl max-w-[85%] leading-relaxed whitespace-pre-line ${
                    m.sender === 'user'
                      ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-br-none shadow-md'
                      : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-none'
                  }`}
                >
                  {m.message}
                </div>
                {m.sender === 'user' && (
                  <div className="w-6 h-6 rounded-full bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center shrink-0">
                    <User className="w-3.5 h-3.5 text-cyan-400" />
                  </div>
                )}
              </div>
            ))}

            {sending && (
              <div className="flex items-center gap-2 text-slate-400 text-[11px] font-mono">
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-emerald-400" />
                Thinking & updating itinerary...
              </div>
            )}
          </div>

          {/* Input Form */}
          <form onSubmit={handleSend} className="p-3 bg-slate-900/90 border-t border-slate-800 flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Genie e.g., 'Add scuba diving on Day 2'"
              className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
            />
            <button
              type="submit"
              disabled={sending}
              className="p-2 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white disabled:opacity-50 transition-all"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>

        </div>
      )}
    </div>
  );
};
