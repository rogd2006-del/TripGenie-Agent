import React from 'react';
import { Sun, CloudRain, Thermometer } from 'lucide-react';

export const WeatherCard = ({ weather }) => {
  if (!weather) return null;

  return (
    <div className="glass-panel rounded-3xl p-6 border border-slate-800 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center">
            <Sun className="w-4 h-4 text-amber-400" />
          </div>
          <h4 className="text-sm font-bold text-white uppercase tracking-wider">Destination Climate Forecast</h4>
        </div>
        <span className="text-xs font-bold text-amber-400 bg-amber-950/40 px-3 py-1 rounded-full border border-amber-800/40">
          {weather.temp_celsius}°C
        </span>
      </div>

      <div className="bg-slate-900/60 p-4 rounded-2xl border border-slate-800 text-xs space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-slate-400">Condition:</span>
          <span className="font-semibold text-white">{weather.condition}</span>
        </div>
        <div className="pt-2 border-t border-slate-800 space-y-1">
          {weather.forecast?.slice(0, 4).map((fc, i) => (
            <div key={i} className="text-slate-400 text-[11px] flex items-center justify-between">
              <span>{fc}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
