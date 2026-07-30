import React from 'react';
import { Utensils, Star, Flame } from 'lucide-react';

export const RestaurantCard = ({ restaurant }) => {
  if (!restaurant) return null;

  return (
    <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
      <div className="flex items-start justify-between">
        <div>
          <h4 className="text-sm font-bold text-white flex items-center gap-1.5">
            <Utensils className="w-4 h-4 text-emerald-400" /> {restaurant.name}
          </h4>
          <span className="text-[11px] text-slate-400 block mt-0.5">{restaurant.cuisine}</span>
        </div>
        <div className="flex items-center gap-1 bg-amber-500/10 px-2 py-0.5 rounded-full text-xs font-bold text-amber-400 border border-amber-500/20">
          <Star className="w-3 h-3 fill-amber-400" /> {restaurant.rating}
        </div>
      </div>

      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
        <span className="text-slate-400 flex items-center gap-1">
          <Flame className="w-3.5 h-3.5 text-rose-400" /> Specialty: {restaurant.specialty}
        </span>
        <span className="font-mono text-emerald-400 font-bold">~₹{restaurant.avg_cost_two} for two</span>
      </div>
    </div>
  );
};
