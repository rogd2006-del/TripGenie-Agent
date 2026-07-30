import React from 'react';
import { Bus, Train, Plane, Clock, Star, Users, ArrowRight, Check } from 'lucide-react';

export const TransportOptionsCard = ({ transport, selectedTransport, onSelectTransport, onBookNow }) => {
  if (!transport || !transport.options || transport.options.length === 0) return null;

  const getIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'flight':
        return <Plane className="w-4 h-4 text-cyan-400" />;
      case 'train':
        return <Train className="w-4 h-4 text-amber-400" />;
      case 'bus':
      default:
        return <Bus className="w-4 h-4 text-emerald-400" />;
    }
  };

  return (
    <div className="glass-panel rounded-3xl p-6 lg:p-8 border border-slate-800 space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            Select Your Transport Option
            <Bus className="w-5 h-5 text-cyan-400" />
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Choose 1 of 3 transport choices for <span className="text-emerald-400 font-semibold">{transport.destination}</span> ({transport.distance_km || 350} km)
          </p>
        </div>

        {onBookNow && (
          <button
            onClick={onBookNow}
            disabled={!selectedTransport}
            className={`px-6 py-3 rounded-2xl font-extrabold text-xs shadow-lg transition-all flex items-center gap-2 shrink-0 self-start sm:self-auto ${
              selectedTransport 
                ? 'bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white shadow-emerald-500/25'
                : 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
            }`}
          >
            <span>{selectedTransport ? 'Proceed to Review & Book' : 'Select Transport First'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* 3 Options Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {transport.options.map((opt, index) => {
          const isSelected = selectedTransport && (selectedTransport.id === opt.id || (selectedTransport.operator_name === opt.operator_name && selectedTransport.transport_type === opt.transport_type));

          return (
            <div
              key={opt.id || index}
              onClick={() => onSelectTransport && onSelectTransport(opt)}
              className={`p-5 rounded-2xl border transition-all flex flex-col justify-between space-y-4 shadow-xl cursor-pointer relative ${
                isSelected
                  ? 'bg-emerald-950/20 border-emerald-500 ring-2 ring-emerald-500/50'
                  : 'bg-slate-900/80 border-slate-800/90 hover:border-emerald-500/40'
              }`}
            >
              {/* Selected Badge */}
              {isSelected && (
                <div className="absolute -top-3 right-3 bg-emerald-500 text-slate-950 px-2.5 py-0.5 rounded-full text-[10px] font-black flex items-center gap-1 shadow-md">
                  <Check className="w-3.5 h-3.5 stroke-[3]" /> Selected
                </div>
              )}

              {/* Top row: Type badge & Rating */}
              <div className="flex items-center justify-between">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-bold text-slate-300">
                  {getIcon(opt.transport_type)}
                  {opt.transport_type}
                </span>
                <span className="flex items-center gap-1 text-xs font-bold text-amber-400 bg-amber-950/40 px-2.5 py-0.5 rounded-lg border border-amber-800/40">
                  <Star className="w-3.5 h-3.5 fill-amber-400" />
                  {opt.rating}
                </span>
              </div>

              {/* Operator & Vehicle */}
              <div>
                <h4 className="text-base font-bold text-white leading-tight">{opt.operator_name}</h4>
                <p className="text-xs text-slate-400 font-mono mt-0.5">
                  Vehicle #: <span className="text-slate-200">{opt.vehicle_number}</span>
                </p>
              </div>

              {/* Departure & Arrival */}
              <div className="bg-slate-950 p-3 rounded-xl border border-slate-900 grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Departure</span>
                  <span className="font-bold text-slate-200">{opt.departure_time}</span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Arrival</span>
                  <span className="font-bold text-slate-200">{opt.arrival_time}</span>
                </div>
              </div>

              {/* Duration & Seats */}
              <div className="flex items-center justify-between text-xs text-slate-400 border-t border-slate-800/60 pt-3">
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-cyan-400" />
                  {opt.travel_duration}
                </span>
                <span className="flex items-center gap-1 text-emerald-400">
                  <Users className="w-3.5 h-3.5" />
                  {opt.available_seats} seats left
                </span>
              </div>

              {/* Price & Selection Button Footer */}
              <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-slate-400 block">Ticket Price</span>
                  <span className="text-base font-extrabold text-emerald-400">
                    ₹{opt.price?.toLocaleString('en-IN')}
                  </span>
                </div>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (onSelectTransport) onSelectTransport(opt);
                  }}
                  className={`px-3 py-1.5 rounded-xl text-xs font-extrabold transition-all flex items-center gap-1 ${
                    isSelected 
                      ? 'bg-emerald-500 text-slate-950 shadow-md'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-200'
                  }`}
                >
                  <Check className="w-3.5 h-3.5" />
                  {isSelected ? 'Chosen' : 'Select'}
                </button>
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
};

