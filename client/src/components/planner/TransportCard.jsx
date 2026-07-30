import React from 'react';
import { Navigation, Plane, Car, Compass } from 'lucide-react';

export const TransportCard = ({ transport }) => {
  if (!transport) return null;

  return (
    <div className="glass-panel rounded-3xl p-6 border border-slate-800 space-y-4">
      <div className="flex items-center gap-2.5 border-b border-slate-800 pb-3">
        <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
          <Plane className="w-4 h-4 text-cyan-400" />
        </div>
        <h4 className="text-sm font-bold text-white uppercase tracking-wider">Transport & Transit Recommendation</h4>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
        <div className="bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
          <span className="text-slate-400 block mb-1 flex items-center gap-1">
            <Car className="w-3.5 h-3.5 text-emerald-400" /> Primary Commute Option
          </span>
          <span className="font-bold text-slate-100">{transport.recommended}</span>
        </div>

        <div className="bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
          <span className="text-slate-400 block mb-1">Estimated Commute Expense</span>
          <span className="font-extrabold text-emerald-400 text-sm">₹{transport.estimated_cost?.toLocaleString()}</span>
        </div>
      </div>

      <p className="text-xs text-slate-400 leading-relaxed bg-slate-950 p-3 rounded-xl border border-slate-900 flex items-start gap-2">
        <Compass className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
        {transport.flight_train_note}
      </p>
    </div>
  );
};
