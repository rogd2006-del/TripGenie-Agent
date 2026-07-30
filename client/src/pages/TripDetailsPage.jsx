import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Sparkles, ArrowLeft, Download, Bookmark, Calendar, MapPin, IndianRupee } from 'lucide-react';
import { tripService } from '../services/tripService';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ItineraryView } from '../components/planner/ItineraryView';
import { BudgetChart } from '../components/planner/BudgetChart';
import { MapView } from '../components/common/MapView';
import { HotelCard } from '../components/planner/HotelCard';
import { TransportCard } from '../components/planner/TransportCard';
import { WeatherCard } from '../components/planner/WeatherCard';
import { RestaurantCard } from '../components/planner/RestaurantCard';
import { PackingList } from '../components/planner/PackingList';
import { TransportOptionsCard } from '../components/planner/TransportOptionsCard';
import { BookingModal } from '../components/planner/BookingModal';


export const TripDetailsPage = () => {
  const { id } = useParams();
  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isBookingOpen, setIsBookingOpen] = useState(false);
  const [selectedHotel, setSelectedHotel] = useState(null);
  const [selectedTransport, setSelectedTransport] = useState(null);

  useEffect(() => {
    tripService.getTripById(id)
      .then(data => {
        setTrip(data);
        if (data?.hotels?.[0]) setSelectedHotel(data.hotels[0]);
        if (data?.transport?.options?.[0]) setSelectedTransport(data.transport.options[0]);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return <LoadingSpinner label="Loading full travel package details..." />;
  }

  if (!trip) {
    return (
      <div className="text-center py-16 space-y-4">
        <h2 className="text-xl font-bold text-white">Trip Not Found</h2>
        <Link to="/dashboard" className="text-xs font-bold text-emerald-400 hover:underline">
          Back to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      
      {/* Back button */}
      <Link to="/dashboard" className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-400 hover:text-white transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </Link>

      {/* Hero Banner */}
      <div className="relative rounded-3xl overflow-hidden h-72 border border-slate-800 shadow-2xl">
        <img
          src={trip.cover_image || 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=800&q=80'}
          alt={trip.title}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent"></div>

        <div className="absolute bottom-6 left-6 right-6 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2 text-xs text-emerald-400 font-bold">
              <MapPin className="w-3.5 h-3.5" /> {trip.destination} | <Calendar className="w-3.5 h-3.5" /> {trip.duration_days} Days
            </div>
            <h1 className="text-2xl sm:text-4xl font-extrabold text-white">{trip.title}</h1>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <button
              onClick={() => setIsBookingOpen(true)}
              className="px-6 py-3 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white font-extrabold text-xs shadow-xl shadow-emerald-500/25 transition-all"
            >
              Book Now
            </button>

            <a
              href={tripService.getPdfDownloadUrl(id)}
              download
              className="px-5 py-3 rounded-2xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs shadow-xl transition-all flex items-center gap-2"
            >
              <Download className="w-4 h-4" /> Download PDF Report
            </a>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 text-xs text-slate-300 leading-relaxed">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-2">Executive Autonomous Summary</h3>
        <p>{trip.summary}</p>
      </div>

      {/* Map View */}
      <MapView destination={trip.destination} mapInfo={trip.destination_details?.map_info} trip={trip} />

      {/* Itinerary */}
      <ItineraryView itinerary={trip.itinerary} />

      {/* Budget Chart */}
      <BudgetChart budgetBreakdown={trip.budget_breakdown} targetBudget={trip.budget} />

      {/* Hotels & Weather Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Hotels</h3>
          {(!trip.hotels || trip.hotels.length === 0) ? (
            <div className="glass-card rounded-2xl p-6 text-center text-slate-400 text-xs border border-slate-800">
              {trip.hotel_message || `No hotels were found within your budget of ₹${trip.budget?.toLocaleString('en-IN') || ''}. Consider increasing your budget or choosing another nearby area.`}
            </div>
          ) : (
            trip.hotels.map((h, i) => (
              <HotelCard 
                key={i} 
                hotel={h} 
                isSelected={selectedHotel && (selectedHotel.name === h.name || selectedHotel.hotel_name === h.hotel_name)}
                onSelect={setSelectedHotel}
              />
            ))
          )}
        </div>

        <div className="space-y-6">
          <WeatherCard weather={trip.weather} />
          <TransportCard transport={trip.transport} />
        </div>
      </div>

      {/* Transport Options Section (Below Hotels) */}
      <TransportOptionsCard
        transport={trip.transport}
        selectedTransport={selectedTransport}
        onSelectTransport={setSelectedTransport}
        onBookNow={() => setIsBookingOpen(true)}
      />

      {/* Booking Modal */}
      <BookingModal
        isOpen={isBookingOpen}
        onClose={() => setIsBookingOpen(false)}
        trip={trip}
        selectedHotel={selectedHotel}
        selectedTransport={selectedTransport}
      />



      {/* Dining Spots */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">Dining Spots</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {trip.restaurants?.map((r, i) => (
            <RestaurantCard key={i} restaurant={r} />
          ))}
        </div>
      </div>

      {/* Packing */}
      <PackingList items={trip.packing_list} emergencyContacts={trip.emergency_contacts} />

    </div>
  );
};
