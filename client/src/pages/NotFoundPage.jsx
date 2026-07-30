import React from 'react';
import { Link } from 'react-router-dom';
import { Compass, Home } from 'lucide-react';

export const NotFoundPage = () => {
  return (
    <div className="max-w-md mx-auto text-center py-20 space-y-6">
      <div className="w-16 h-16 rounded-3xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center mx-auto text-emerald-400">
        <Compass className="w-8 h-8 animate-spin-slow" />
      </div>

      <div className="space-y-2">
        <h1 className="text-4xl font-extrabold text-white">404 - Off the Map</h1>
        <p className="text-xs text-slate-400">The destination page you are searching for does not exist.</p>
      </div>

      <Link
        to="/"
        className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-emerald-500 hover:bg-emerald-600 text-white font-bold text-xs shadow-lg shadow-emerald-500/20 transition-all"
      >
        <Home className="w-4 h-4" /> Return to Homepage
      </Link>
    </div>
  );
};
