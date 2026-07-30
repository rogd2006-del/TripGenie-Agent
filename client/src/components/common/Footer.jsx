import React from 'react';
import { Compass, Sparkles, Heart, Shield, Cpu, MapPin } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Footer = () => {
  return (
    <footer className="bg-slate-950 border-t border-slate-900 pt-16 pb-12 text-slate-400 text-sm">
      <div className="max-w-7xl mx-auto px-4 lg:px-8 grid grid-cols-1 md:grid-cols-4 gap-10">
        
        {/* Brand Description */}
        <div className="space-y-4 md:col-span-1">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
              <Compass className="w-4 h-4 text-emerald-400" />
            </div>
            <span className="text-lg font-bold text-white tracking-tight">
              Trip<span className="text-emerald-400">Genie</span>
            </span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Autonomous multi-agent AI travel orchestration engine powered by LangGraph, FastAPI, and OpenAI.
          </p>
          <div className="flex items-center gap-2 text-xs text-emerald-400 font-semibold bg-emerald-950/40 border border-emerald-800/40 px-3 py-1.5 rounded-full w-fit">
            <Cpu className="w-3.5 h-3.5" />
            <span>10 Active AI Sub-Agents</span>
          </div>
        </div>

        {/* Quick Links */}
        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 mb-4">Platform</h4>
          <ul className="space-y-2.5 text-xs">
            <li><Link to="/planner" className="hover:text-emerald-400 transition-colors">AI Autonomous Planner</Link></li>
            <li><Link to="/dashboard" className="hover:text-emerald-400 transition-colors">Personal Dashboard</Link></li>
            <li><Link to="/saved" className="hover:text-emerald-400 transition-colors">Saved Travel Plans</Link></li>
            <li><Link to="/settings" className="hover:text-emerald-400 transition-colors">Model & LLM Settings</Link></li>
          </ul>
        </div>

        {/* Core Agent Network */}
        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 mb-4">Multi-Agent Swarm</h4>
          <ul className="space-y-2 text-xs text-slate-400">
            <li className="flex items-center gap-1.5"><Sparkles className="w-3 h-3 text-emerald-400" /> Supervisor & Planner Agent</li>
            <li className="flex items-center gap-1.5"><MapPin className="w-3 h-3 text-teal-400" /> Destination & Maps Agent</li>
            <li className="flex items-center gap-1.5"><Shield className="w-3 h-3 text-cyan-400" /> Hotel, Flight & Budget Agents</li>
            <li className="flex items-center gap-1.5"><Cpu className="w-3 h-3 text-purple-400" /> Itinerary & PDF Generator</li>
          </ul>
        </div>

        {/* Tech Stack */}
        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 mb-4">Architecture</h4>
          <div className="flex flex-wrap gap-2">
            {['LangGraph', 'FastAPI', 'MongoDB', 'React', 'Vite', 'Tailwind', 'JWT', 'ReportLab'].map((tag) => (
              <span key={tag} className="px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-[11px] text-slate-300 font-mono">
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 lg:px-8 mt-12 pt-6 border-t border-slate-900 flex flex-col md:flex-row items-center justify-between text-xs text-slate-400 gap-4">
        <p>© 2026 TripGenie Autonomous Travel Platform. All rights reserved.</p>
        <p className="flex items-center gap-1">
          Built with <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500" /> for AI Autonomous Agents
        </p>
      </div>
    </footer>
  );
};
