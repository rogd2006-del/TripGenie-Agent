import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Plus, Clock, Bookmark, Search } from 'lucide-react';
import { tripService } from '../services/tripService';
import { StatsOverview } from '../components/dashboard/StatsOverview';
import { TripCard } from '../components/dashboard/TripCard';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const DashboardPage = () => {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterTab, setFilterTab] = useState('all');

  const fetchTrips = async () => {
    try {
      const data = await tripService.getHistory();
      setTrips(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrips();
  }, []);

  const handleSave = async (id) => {
    try {
      await tripService.saveTrip(id);
      fetchTrips();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    try {
      await tripService.deleteTrip(id);
      setTrips(prev => prev.filter(t => (t.id || t._id) !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const filteredTrips = trips.filter(t => {
    const matchesSearch = t.title?.toLowerCase().includes(searchTerm.toLowerCase()) || t.destination?.toLowerCase().includes(searchTerm.toLowerCase());
    if (filterTab === 'saved') return matchesSearch && t.is_saved;
    return matchesSearch;
  });

  const totalBudget = trips.reduce((acc, curr) => acc + (curr.estimated_total || curr.budget || 0), 0);
  const savedCount = trips.filter(t => t.is_saved).length;

  return (
    <div className="space-y-8">
      
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
            TripGenie Control Dashboard
            <Sparkles className="w-6 h-6 text-emerald-400" />
          </h1>
          <p className="text-xs text-slate-400 mt-1">Overview of generated travel plans & autonomous AI history</p>
        </div>

        <Link
          to="/planner"
          className="px-5 py-3 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white font-bold text-xs shadow-lg shadow-emerald-500/20 transition-all flex items-center justify-center gap-2"
        >
          <Plus className="w-4 h-4" /> Create New AI Plan
        </Link>
      </div>

      {/* Stats Cards */}
      <StatsOverview totalTrips={trips.length} savedTrips={savedCount} totalBudget={totalBudget} />

      {/* Search & Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4 border-t border-slate-900">
        <div className="flex items-center gap-2 bg-slate-900/90 p-1.5 rounded-2xl border border-slate-800 self-start">
          <button
            onClick={() => setFilterTab('all')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              filterTab === 'all' ? 'bg-emerald-500 text-white shadow-md' : 'text-slate-400 hover:text-white'
            }`}
          >
            All Plans ({trips.length})
          </button>
          <button
            onClick={() => setFilterTab('saved')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              filterTab === 'saved' ? 'bg-emerald-500 text-white shadow-md' : 'text-slate-400 hover:text-white'
            }`}
          >
            Saved Bookmarks ({savedCount})
          </button>
        </div>

        <div className="relative max-w-xs w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search destination or title..."
            className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
          />
        </div>
      </div>

      {/* Trips Grid */}
      {loading ? (
        <LoadingSpinner label="Retrieving autonomous trip history..." />
      ) : filteredTrips.length === 0 ? (
        <div className="glass-panel rounded-3xl p-12 text-center space-y-4 border border-slate-800">
          <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center mx-auto text-slate-500">
            <Clock className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-white">No Travel Plans Found</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            You haven't created any travel plans yet. Use the autonomous planner to generate your first itinerary!
          </p>
          <Link
            to="/planner"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-emerald-500 text-white font-bold text-xs shadow-md"
          >
            <Sparkles className="w-4 h-4" /> Start AI Planner
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTrips.map((trip) => (
            <TripCard
              key={trip.id || trip._id}
              trip={trip}
              onSave={handleSave}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

    </div>
  );
};
