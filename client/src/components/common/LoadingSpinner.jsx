import React from 'react';
import { Compass, Sparkles } from 'lucide-react';

export const LoadingSpinner = ({ label = 'Loading TripGenie...' }) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="relative w-16 h-16 flex items-center justify-center">
        <div className="absolute inset-0 rounded-full border-4 border-emerald-500/20 border-t-emerald-500 animate-spin"></div>
        <Compass className="w-8 h-8 text-emerald-400 animate-pulse" />
      </div>
      <p className="mt-4 text-sm font-semibold text-slate-300 flex items-center gap-2">
        <Sparkles className="w-4 h-4 text-cyan-400" />
        {label}
      </p>
    </div>
  );
};
