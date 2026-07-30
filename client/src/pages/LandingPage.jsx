import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Compass, Cpu, MapPin, Shield, Zap, ArrowRight, CheckCircle2, Globe, Heart } from 'lucide-react';
import { GlassCard } from '../components/common/GlassCard';

export const LandingPage = () => {
  return (
    <div className="space-y-24 py-6">
      
      {/* Hero Section */}
      <section className="relative text-center max-w-4xl mx-auto space-y-8 pt-8">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold uppercase tracking-wider animate-bounce-slow">
          <Sparkles className="w-4 h-4" /> Next-Generation Autonomous Multi-Agent AI Architecture
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight leading-tight">
          Plan Your Next Adventure with <br />
          <span className="text-gradient">Autonomous Multi-Agent AI</span>
        </h1>

        <p className="text-slate-300 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
          TripGenie doesn't just chat. Its swarm of 10 specialized LangGraph AI agents autonomously research destinations, calculate budgets, book hotels, recommend restaurants, predict weather, and synthesize complete itineraries.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Link
            to="/planner"
            className="w-full sm:w-auto px-8 py-4 rounded-full bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:scale-105 text-white font-extrabold text-sm shadow-xl shadow-emerald-500/25 transition-all flex items-center justify-center gap-2"
          >
            <Sparkles className="w-5 h-5" /> Start Autonomous AI Planning
          </Link>
          <Link
            to="/dashboard"
            className="w-full sm:w-auto px-8 py-4 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-200 font-bold text-sm transition-all flex items-center justify-center gap-2"
          >
            Explore Dashboard <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {/* Demo prompt sample */}
        <div className="max-w-2xl mx-auto mt-8 p-4 rounded-2xl glass-panel border border-slate-800 text-xs text-slate-300 flex items-center justify-between gap-4">
          <div className="flex items-center gap-2.5 text-left">
            <span className="text-xl">💡</span>
            <div>
              <span className="font-semibold text-white block">Try an example prompt:</span>
              <span className="text-slate-400 italic">"4-day trip to Goa under ₹20,000 with beaches, nightlife, vegetarian food and adventure sports."</span>
            </div>
          </div>
          <Link to="/planner" className="shrink-0 px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 font-bold hover:bg-emerald-500 hover:text-white transition-all">
            Try Now
          </Link>
        </div>
      </section>

      {/* Feature Showcase Grid */}
      <section className="space-y-12">
        <div className="text-center max-w-2xl mx-auto space-y-3">
          <h2 className="text-3xl font-extrabold text-white">
            10 Autonomous Specialized Sub-Agents
          </h2>
          <p className="text-slate-400 text-xs sm:text-sm">
            Coordinated by a master Supervisor Agent using LangGraph logic graph.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <GlassCard className="space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
              <Cpu className="w-6 h-6 text-emerald-400" />
            </div>
            <h3 className="text-base font-bold text-white">Supervisor & Planner Agents</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Deconstructs natural language inputs, formulates strategic timelines, and delegates sub-tasks across specialized agent nodes.
            </p>
          </GlassCard>

          <GlassCard className="space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center">
              <MapPin className="w-6 h-6 text-teal-400" />
            </div>
            <h3 className="text-base font-bold text-white">Destination & Weather Agents</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Researches top attraction sights, maps spatial coordinates, and queries real-time OpenWeather forecasts for travel dates.
            </p>
          </GlassCard>

          <GlassCard className="space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
              <Shield className="w-6 h-6 text-cyan-400" />
            </div>
            <h3 className="text-base font-bold text-white">Budget, Hotel & Flight Agents</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Searches lodging options matching luxury preferences, calculates transport costs, and computes itemized budget allocations.
            </p>
          </GlassCard>
        </div>
      </section>

      {/* Interactive Process Banner */}
      <section className="glass-panel rounded-3xl p-8 lg:p-12 border border-slate-800 text-center space-y-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 via-teal-500/5 to-cyan-500/10 pointer-events-none"></div>

        <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
          Ready to experience the future of travel planning?
        </h2>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs max-w-3xl mx-auto">
          <div className="bg-slate-900/80 p-4 rounded-2xl border border-slate-800">
            <span className="text-lg font-bold text-emerald-400 block mb-1">01</span>
            <span className="text-white font-semibold">Enter Prompt</span>
          </div>
          <div className="bg-slate-900/80 p-4 rounded-2xl border border-slate-800">
            <span className="text-lg font-bold text-teal-400 block mb-1">02</span>
            <span className="text-white font-semibold">Swarm Executes</span>
          </div>
          <div className="bg-slate-900/80 p-4 rounded-2xl border border-slate-800">
            <span className="text-lg font-bold text-cyan-400 block mb-1">03</span>
            <span className="text-white font-semibold">Review Itinerary</span>
          </div>
          <div className="bg-slate-900/80 p-4 rounded-2xl border border-slate-800">
            <span className="text-lg font-bold text-purple-400 block mb-1">04</span>
            <span className="text-white font-semibold">Export PDF Report</span>
          </div>
        </div>

        <Link
          to="/planner"
          className="inline-flex items-center gap-2 px-8 py-4 rounded-full bg-emerald-500 hover:bg-emerald-600 text-white font-bold text-sm shadow-xl shadow-emerald-500/25 transition-all"
        >
          <Sparkles className="w-4 h-4" /> Create Your Autonomous Travel Plan
        </Link>
      </section>

    </div>
  );
};
