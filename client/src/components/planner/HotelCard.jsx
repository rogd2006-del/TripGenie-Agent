import React from 'react';
import { Star, MapPin, Check, Hotel, Navigation, Globe, Phone, ExternalLink } from 'lucide-react';

export const HotelCard = ({ hotel, isSelected = false, onSelect = null }) => {
  if (!hotel) return null;

  const hotelName = hotel.hotel_name || hotel.name || 'Boutique Hotel';
  const priceDisplay = typeof hotel.price === 'number' ? `₹${hotel.price.toLocaleString()}` : (hotel.price ? `₹${hotel.price}` : 'Contact for price');
  const ratingDisplay = hotel.rating || '4.5';
  const reviewsDisplay = hotel.reviews ? `(${hotel.reviews} reviews)` : '';
  const mapsUrl = hotel.maps_url || (hotel.latitude && hotel.longitude 
    ? `https://www.google.com/maps/search/?api=1&query=${hotel.latitude},${hotel.longitude}`
    : `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(hotelName + ' ' + hotel.address)}`);

  return (
    <div 
      onClick={onSelect ? () => onSelect(hotel) : undefined}
      className={`glass-card rounded-2xl overflow-hidden border transition-all flex flex-col md:flex-row shadow-xl relative ${
        isSelected 
          ? 'border-emerald-500 ring-2 ring-emerald-500/50 bg-emerald-950/20' 
          : 'border-slate-800 hover:border-emerald-500/40 cursor-pointer'
      }`}
    >
      {/* Selection Check Badge */}
      {isSelected && (
        <div className="absolute top-3 right-3 z-10 bg-emerald-500 text-slate-950 px-3 py-1 rounded-full text-xs font-black flex items-center gap-1 shadow-lg">
          <Check className="w-4 h-4 stroke-[3]" /> Selected Lodging
        </div>
      )}

      {/* Image Container */}
      <div className="md:w-2/5 h-52 md:h-auto relative overflow-hidden shrink-0">
        <img
          src={hotel.image || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80'}
          alt={hotelName}
          className="w-full h-full object-cover hover:scale-105 transition-transform duration-500"
          onError={(e) => {
            e.target.src = 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80';
          }}
        />
        <div className="absolute top-3 left-3 bg-slate-950/85 backdrop-blur-md px-3 py-1 rounded-full text-xs font-bold text-amber-400 flex items-center gap-1.5 border border-amber-500/30">
          <Star className="w-3.5 h-3.5 fill-amber-400" /> {ratingDisplay} <span className="text-slate-400 font-normal text-[10px]">{reviewsDisplay}</span>
        </div>

        {hotel.distance && (
          <div className="absolute bottom-3 left-3 bg-slate-950/85 backdrop-blur-md px-2.5 py-1 rounded-full text-[11px] font-bold text-cyan-300 flex items-center gap-1 border border-cyan-500/30">
            <Navigation className="w-3 h-3" /> {hotel.distance}
          </div>
        )}
      </div>

      {/* Details Container */}
      <div className="p-5 md:w-3/5 flex flex-col justify-between space-y-4">
        <div>
          <div className="flex items-start justify-between gap-2">
            <div>
              <h4 className="text-base font-bold text-white flex items-center gap-2">
                <Hotel className="w-4 h-4 text-emerald-400 shrink-0" /> {hotelName}
              </h4>
              <p className="text-xs text-slate-400 mt-1 flex items-start gap-1">
                <MapPin className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" /> {hotel.address}
              </p>
            </div>
            
            <div className="text-right shrink-0">
              <span className="text-sm font-extrabold text-emerald-400">{priceDisplay}</span>
              <span className="text-[10px] text-slate-400 block">/ night</span>
            </div>
          </div>

          {/* Contact Info if available */}
          {(hotel.phone || hotel.website) && (
            <div className="mt-2 text-[11px] text-slate-400 flex flex-wrap gap-3">
              {hotel.phone && (
                <span className="flex items-center gap-1">
                  <Phone className="w-3 h-3 text-emerald-400" /> {hotel.phone}
                </span>
              )}
            </div>
          )}
        </div>

        {/* Amenities tags */}
        {hotel.amenities && hotel.amenities.length > 0 && (
          <div className="flex flex-wrap gap-1.5 pt-2 border-t border-slate-800/80">
            {hotel.amenities.slice(0, 4).map((amenity, idx) => (
              <span key={idx} className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-[11px] text-slate-300 flex items-center gap-1">
                <Check className="w-3 h-3 text-emerald-400" /> {amenity}
              </span>
            ))}
          </div>
        )}

        {/* Action Buttons: Select & View on Google Maps */}
        <div className="flex items-center gap-2 pt-3 border-t border-slate-800/80">
          {onSelect && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onSelect(hotel);
              }}
              className={`py-2 px-4 rounded-xl text-xs font-extrabold transition-all flex items-center justify-center gap-1.5 ${
                isSelected 
                  ? 'bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20' 
                  : 'bg-slate-800 hover:bg-slate-700 text-white'
              }`}
            >
              <Check className="w-4 h-4" /> {isSelected ? 'Selected' : 'Select Hotel'}
            </button>
          )}

          <a
            href={mapsUrl}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="flex-1 py-2 px-3 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-bold transition-all flex items-center justify-center gap-1.5"
          >
            <Navigation className="w-3.5 h-3.5" /> View Map
          </a>

          {hotel.website && (
            <a
              href={hotel.website}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="py-2 px-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs font-bold transition-all flex items-center justify-center gap-1.5"
            >
              <Globe className="w-3.5 h-3.5 text-cyan-400" /> Website <ExternalLink className="w-3 h-3 text-slate-500" />
            </a>
          )}
        </div>

      </div>
    </div>
  );
};

