import React from 'react';
import { Compass, Bookmark, IndianRupee, Cpu } from 'lucide-react';
import { GlassCard } from '../common/GlassCard';

export const StatsOverview = ({ totalTrips = 0, savedTrips = 0, totalBudget = 0 }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      
      {/* Stat 1 */}
      <GlassCard hover={false} className="p-5 flex items-center gap-4">
        <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center shrink-0">
          <Compass className="w-6 h-6 text-emerald-400" />
        </div>
        <div>
          <span className="text-xs text-slate-400 font-medium">Generated Trips</span>
          <h3 className="text-xl font-extrabold text-white mt-0.5">{totalTrips}</h3>
        </div>
      </GlassCard>

      {/* Stat 2 */}
      <GlassCard hover={false} className="p-5 flex items-center gap-4">
        <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center shrink-0">
          <Bookmark className="w-6 h-6 text-cyan-400" />
        </div>
        <div>
          <span className="text-xs text-slate-400 font-medium">Saved Bookmarks</span>
          <h3 className="text-xl font-extrabold text-white mt-0.5">{savedTrips}</h3>
        </div>
      </GlassCard>

      {/* Stat 3 */}
      <GlassCard hover={false} className="p-5 flex items-center gap-4">
        <div className="w-12 h-12 rounded-2xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center shrink-0">
          <IndianRupee className="w-6 h-6 text-teal-400" />
        </div>
        <div>
          <span className="text-xs text-slate-400 font-medium">Total Planned Budget</span>
          <h3 className="text-xl font-extrabold text-white mt-0.5">₹{totalBudget.toLocaleString()}</h3>
        </div>
      </GlassCard>

      {/* Stat 4 */}
      <GlassCard hover={false} className="p-5 flex items-center gap-4">
        <div className="w-12 h-12 rounded-2xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center shrink-0">
          <Cpu className="w-6 h-6 text-purple-400" />
        </div>
        <div>
          <span className="text-xs text-slate-400 font-medium">LangGraph Agents</span>
          <h3 className="text-xl font-extrabold text-white mt-0.5">10 Active Swarm</h3>
        </div>
      </GlassCard>

    </div>
  );
};
