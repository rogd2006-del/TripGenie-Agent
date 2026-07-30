import React from 'react';
import { Link } from 'react-router-dom';
import { MapPin, Calendar, IndianRupee, ArrowRight, Bookmark, Trash2 } from 'lucide-react';
import { GlassCard } from '../common/GlassCard';

export const TripCard = ({ trip, onSave, onDelete }) => {
  if (!trip) return null;

  const tripId = trip.id || trip._id;

  return (
    <GlassCard className="p-0 flex flex-col justify-between group">
      {/* Cover Image */}
      <div className="h-44 relative overflow-hidden">
        <img
          src={trip.cover_image || 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=800&q=80'}
          alt={trip.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/20 to-transparent"></div>

        {/* Top Badges */}
        <div className="absolute top-3 left-3 right-3 flex items-center justify-between">
          <span className="px-3 py-1 rounded-full bg-slate-950/80 backdrop-blur-md text-[11px] font-bold text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
            <Calendar className="w-3 h-3" /> {trip.duration_days} Days
          </span>
          
          <div className="flex items-center gap-1.5">
            {onSave && (
              <button
                onClick={() => onSave(tripId)}
                className={`p-2 rounded-full backdrop-blur-md transition-all ${
                  trip.is_saved
                    ? 'bg-emerald-500 text-white'
                    : 'bg-slate-950/80 text-slate-300 hover:text-emerald-400'
                }`}
                title="Save Trip"
              >
                <Bookmark className="w-4 h-4" />
              </button>
            )}
            {onDelete && (
              <button
                onClick={() => onDelete(tripId)}
                className="p-2 rounded-full bg-slate-950/80 backdrop-blur-md text-slate-400 hover:text-rose-400 transition-all"
                title="Delete Trip"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Bottom Destination */}
        <div className="absolute bottom-3 left-3 text-xs font-semibold text-slate-200 flex items-center gap-1">
          <MapPin className="w-3.5 h-3.5 text-cyan-400" /> {trip.destination}
        </div>
      </div>

      {/* Card Content */}
      <div className="p-5 space-y-3 flex-1 flex flex-col justify-between">
        <div>
          <h3 className="text-base font-bold text-white group-hover:text-emerald-400 transition-colors line-clamp-1">
            {trip.title}
          </h3>
          <p className="text-xs text-slate-400 line-clamp-2 mt-1 leading-relaxed">
            {trip.summary}
          </p>
        </div>

        <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
          <div>
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Estimated Total</span>
            <span className="text-sm font-extrabold text-emerald-400 flex items-center">
              <IndianRupee className="w-3.5 h-3.5" /> {(trip.estimated_total || trip.budget).toLocaleString()}
            </span>
          </div>

          <Link
            to={`/trip/${tripId}`}
            className="px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-white group-hover:bg-emerald-500 group-hover:border-emerald-500 transition-all flex items-center gap-1.5 shadow-md"
          >
            View Plan <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </GlassCard>
  );
};
