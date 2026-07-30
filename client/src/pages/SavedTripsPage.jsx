import React, { useState, useEffect } from 'react';
import { Bookmark } from 'lucide-react';
import { tripService } from '../services/tripService';
import { TripCard } from '../components/dashboard/TripCard';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const SavedTripsPage = () => {
  const [savedTrips, setSavedTrips] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchSaved = async () => {
    try {
      const data = await tripService.getHistory();
      setSavedTrips(data.filter(t => t.is_saved));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSaved();
  }, []);

  const handleDelete = async (id) => {
    try {
      await tripService.deleteTrip(id);
      setSavedTrips(prev => prev.filter(t => (t.id || t._id) !== id));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
          Saved Bookmarks & Saved Trips
          <Bookmark className="w-6 h-6 text-emerald-400" />
        </h1>
        <p className="text-xs text-slate-400">View and manage your bookmarked travel plans.</p>
      </div>

      {loading ? (
        <LoadingSpinner label="Retrieving saved bookmarks..." />
      ) : savedTrips.length === 0 ? (
        <div className="glass-panel rounded-3xl p-12 text-center space-y-4 border border-slate-800">
          <Bookmark className="w-8 h-8 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-white">No Saved Trips Yet</h3>
          <p className="text-xs text-slate-400">Bookmark plans from your dashboard or AI planner to save them here.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {savedTrips.map((trip) => (
            <TripCard key={trip.id || trip._id} trip={trip} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  );
};
