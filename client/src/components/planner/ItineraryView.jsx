import React, { useState } from 'react';
import { Calendar, Clock, MapPin, SunMedium, Sparkles } from 'lucide-react';

export const ItineraryView = ({ itinerary = [] }) => {
  const [activeDay, setActiveDay] = useState(1);

  if (!itinerary || itinerary.length === 0) return null;

  const currentDayData = itinerary.find(d => d.day === activeDay) || itinerary[0];

  return (
    <div className="glass-panel rounded-3xl p-6 lg:p-8 border border-slate-800 shadow-2xl space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            Day-by-Day Master Schedule
            <Calendar className="w-5 h-5 text-emerald-400" />
          </h3>
          <p className="text-xs text-slate-400">Curated hourly timetable created by Itinerary Agent</p>
        </div>

        {/* Day selection tabs */}
        <div className="flex gap-2 overflow-x-auto pb-1">
          {itinerary.map((d) => (
            <button
              key={d.day}
              onClick={() => setActiveDay(d.day)}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
                activeDay === d.day
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/20'
                  : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              Day {d.day}
            </button>
          ))}
        </div>
      </div>

      {/* Selected Day Overview */}
      <div className="bg-slate-900/60 p-4 rounded-2xl border border-slate-800 flex items-center justify-between">
        <div>
          <h4 className="text-sm font-bold text-emerald-300">
            Day {currentDayData.day}: {currentDayData.title}
          </h4>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-cyan-400 font-semibold bg-cyan-950/40 border border-cyan-800/40 px-3 py-1.5 rounded-full">
          <SunMedium className="w-4 h-4" /> {currentDayData.weather}
        </div>
      </div>

      {/* Activities Timeline */}
      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-gradient-to-b before:from-emerald-500 before:via-teal-500 before:to-cyan-500">
        {currentDayData.activities?.map((act, idx) => (
          <div key={idx} className="relative group">
            
            {/* Timeline Dot */}
            <div className="absolute -left-6 top-1.5 w-3 h-3 rounded-full bg-emerald-400 ring-4 ring-slate-950 group-hover:scale-125 transition-transform"></div>

            <div className="bg-slate-900/80 p-4 rounded-2xl border border-slate-800/80 group-hover:border-emerald-500/40 transition-all space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-mono text-emerald-400 font-semibold flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" /> {act.time}
                </span>
                <span className="text-slate-400 flex items-center gap-1 text-[11px]">
                  <MapPin className="w-3.5 h-3.5 text-cyan-400" /> {act.location}
                </span>
              </div>
              <p className="text-xs font-medium text-slate-100">{act.activity}</p>
            </div>

          </div>
        ))}
      </div>

    </div>
  );
};
