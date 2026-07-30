import React, { useEffect } from 'react';
import { MapPin, Navigation } from 'lucide-react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Resolve Leaflet safely (e.g. handle module namespace objects in Vite/ESM)
const Leaflet = L && L.Icon ? L : (L ? (L.default || L) : null);

// Apply prototype fixes safely in try-catch
if (Leaflet && Leaflet.Icon && Leaflet.Icon.Default) {
  try {
    delete Leaflet.Icon.Default.prototype._getIconUrl;
    Leaflet.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
      iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    });
  } catch (e) {
    console.warn("Leaflet default icon patch failed:", e);
  }
}

// Helper to safely instantiate custom HTML/CSS divIcons
const createCustomMarker = (colorClass, glowClass) => {
  if (Leaflet && Leaflet.divIcon) {
    try {
      return Leaflet.divIcon({
        html: `<div class="relative w-7 h-7 flex items-center justify-center">
                <div class="absolute w-full h-full rounded-full ${glowClass} animate-ping opacity-60"></div>
                <div class="w-3.5 h-3.5 rounded-full ${colorClass} border-2 border-white shadow-md z-10"></div>
               </div>`,
        className: 'custom-leaflet-marker',
        iconSize: [28, 28],
        iconAnchor: [14, 14],
      });
    } catch (e) {
      console.warn("Custom divIcon creation failed:", e);
    }
  }
  return null;
};

// Create custom icons lazily/safely
const centerIcon = createCustomMarker('bg-emerald-500', 'bg-emerald-400/30');
const hotelIcon = createCustomMarker('bg-blue-500', 'bg-blue-400/30');
const restaurantIcon = createCustomMarker('bg-amber-500', 'bg-amber-400/30');
const attractionIcon = createCustomMarker('bg-purple-500', 'bg-purple-400/30');
const emergencyIcon = createCustomMarker('bg-red-500', 'bg-red-400/30');

// Component to dynamically update map center when trip coordinates change
const ChangeMapCenter = ({ center }) => {
  const map = useMap();
  useEffect(() => {
    if (center && Array.isArray(center) && center.length === 2) {
      const [lat, lng] = center;
      if (!isNaN(lat) && !isNaN(lng) && lat !== 0 && lng !== 0) {
        try {
          map.flyTo([lat, lng], 12, {
            animate: true,
            duration: 1.5,
          });
        } catch (e) {
          try {
            map.setView([lat, lng], 12);
          } catch (err) {
            console.warn("map.setView / flyTo failed:", err);
          }
        }
      }
    }
  }, [center[0], center[1], map]);
  return null;
};

export const MapView = ({ destination = "Goa, India", trip }) => {
  // Determine map center coordinates dynamically from trip state
  const rawLat = trip?.destination_details?.latitude ?? trip?.destination_lat ?? trip?.latitude;
  const rawLon = trip?.destination_details?.longitude ?? trip?.destination_lng ?? trip?.longitude;

  const lat = parseFloat(rawLat);
  const lon = parseFloat(rawLon);

  const geocodingFailed = trip?.geocoding_failed || isNaN(lat) || isNaN(lon);

  if (geocodingFailed) {
    return (
      <div className="rounded-3xl p-8 border border-rose-900/50 bg-rose-950/20 text-center space-y-3 shadow-2xl">
        <div className="w-12 h-12 rounded-full bg-rose-500/10 border border-rose-500/30 flex items-center justify-center mx-auto">
          <MapPin className="w-6 h-6 text-rose-400 animate-bounce" />
        </div>
        <h4 className="text-base font-bold text-rose-200">Unable to locate the destination.</h4>
        <p className="text-xs text-rose-300/70 max-w-md mx-auto">
          Could not resolve coordinates for "{destination}". Please check the spelling or provide a more specific location.
        </p>
      </div>
    );
  }

  const centerCoords = [lat, lon];

  // Group markers
  const hotels = trip?.hotels || [];
  const restaurants = trip?.restaurants || [];
  const attractions = trip?.places || trip?.attractions || [];
  const routeGeometry = trip?.transport?.route_geometry || [];
  const hospitals = trip?.hospitals || [];
  const pharmacies = trip?.pharmacies || [];

  // Helper to compile props (only pass icon if it is defined and not null)
  const getMarkerProps = (iconObj) => {
    return iconObj ? { icon: iconObj } : {};
  };

  return (
    <div className="rounded-3xl overflow-hidden border border-slate-800 bg-slate-950/60 shadow-2xl relative group">
      {/* Map Header */}
      <div className="px-5 py-3.5 bg-slate-900/80 border-b border-slate-800 flex items-center justify-between backdrop-blur-md">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
            <MapPin className="w-4 h-4 text-emerald-400 animate-pulse" />
          </div>
          <span className="text-xs font-bold text-slate-200 uppercase tracking-wider">
            OSM Routing & Exploration Map
          </span>
        </div>
        <span className="text-xs text-slate-400 font-mono flex items-center gap-1.5 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800">
          <Navigation className="w-3.5 h-3.5 text-cyan-400" /> {destination}
        </span>
      </div>

      {/* React Leaflet Container */}
      <div className="w-full h-[380px] relative z-10">
        <MapContainer
          center={centerCoords}
          zoom={12}
          scrollWheelZoom={false}
          className="w-full h-full"
        >
          {/* Tile layer using CartoDB Dark Matter for sleek premium dark-mode aesthetic */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />

          <ChangeMapCenter center={centerCoords} />

          {/* Destination Center Marker */}
          <Marker position={centerCoords} {...getMarkerProps(centerIcon)}>
            <Popup className="custom-leaflet-popup">
              <div className="p-1 font-sans text-slate-800">
                <h4 className="text-xs font-bold uppercase">{destination}</h4>
                <p className="text-[10px] mt-0.5">Resolved trip center coords.</p>
              </div>
            </Popup>
          </Marker>

          {/* Lodgings/Hotels Markers */}
          {hotels.map((h, idx) => {
            const hLat = parseFloat(h.latitude);
            const hLng = parseFloat(h.longitude);
            if (isNaN(hLat) || isNaN(hLng)) return null;
            return (
              <Marker key={`hotel-${idx}`} position={[hLat, hLng]} {...getMarkerProps(hotelIcon)}>
                <Popup>
                  <div className="p-1 font-sans text-slate-800">
                    <h4 className="text-xs font-bold text-blue-600">🏨 {h.hotel_name || h.name}</h4>
                    <p className="text-[10px] mt-1">{h.address}</p>
                    <p className="text-[10px] font-semibold mt-1">Price: ₹{h.price || h.price_per_night}/night</p>
                  </div>
                </Popup>
              </Marker>
            );
          })}

          {/* Dining / Restaurant Markers */}
          {restaurants.map((r, idx) => {
            const rLat = parseFloat(r.latitude);
            const rLng = parseFloat(r.longitude);
            if (isNaN(rLat) || isNaN(rLng)) return null;
            return (
              <Marker key={`rest-${idx}`} position={[rLat, rLng]} {...getMarkerProps(restaurantIcon)}>
                <Popup>
                  <div className="p-1 font-sans text-slate-800">
                    <h4 className="text-xs font-bold text-amber-600">🍽️ {r.name}</h4>
                    <p className="text-[10px] mt-1">{r.cuisine}</p>
                    <p className="text-[10px] font-semibold mt-1">Rating: {r.rating} ★</p>
                  </div>
                </Popup>
              </Marker>
            );
          })}

          {/* Attraction / Sightseeing Markers */}
          {attractions.map((a, idx) => {
            const aLat = parseFloat(a.latitude);
            const aLng = parseFloat(a.longitude);
            if (isNaN(aLat) || isNaN(aLng)) return null;
            return (
              <Marker key={`attr-${idx}`} position={[aLat, aLng]} {...getMarkerProps(attractionIcon)}>
                <Popup>
                  <div className="p-1 font-sans text-slate-800">
                    <h4 className="text-xs font-bold text-purple-600">✨ {a.name}</h4>
                    <p className="text-[10px] mt-1">{a.address}</p>
                    {a.place_type && <p className="text-[10px] mt-0.5">Category: {a.place_type}</p>}
                  </div>
                </Popup>
              </Marker>
            );
          })}

          {/* Emergency / Hospital Markers */}
          {hospitals.map((h, idx) => {
            const hLat = parseFloat(h.latitude);
            const hLng = parseFloat(h.longitude);
            if (isNaN(hLat) || isNaN(hLng)) return null;
            return (
              <Marker key={`hosp-${idx}`} position={[hLat, hLng]} {...getMarkerProps(emergencyIcon)}>
                <Popup>
                  <div className="p-1 font-sans text-slate-800">
                    <h4 className="text-xs font-bold text-red-600">🏥 {h.name}</h4>
                    <p className="text-[10px] mt-1">{h.address}</p>
                    <p className="text-[10px] mt-0.5">Phone: {h.phone}</p>
                  </div>
                </Popup>
              </Marker>
            );
          })}

          {/* Transit Route Polylines */}
          {routeGeometry && routeGeometry.length > 0 && (
            <Polyline
              positions={routeGeometry}
              pathOptions={{
                color: '#06b6d4',
                weight: 4,
                opacity: 0.8,
                dashArray: '5, 8',
                lineJoin: 'round',
              }}
            />
          )}
        </MapContainer>

        {/* Legend Overlay */}
        <div className="absolute bottom-4 left-4 bg-slate-950/90 backdrop-blur-md px-3.5 py-2.5 rounded-xl border border-slate-800 text-[10px] text-slate-300 space-y-1.5 shadow-xl z-[400]">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 border border-white"></span>
            <span>Trip Center</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-500 border border-white"></span>
            <span>Lodging / Hotels</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500 border border-white"></span>
            <span>Dining Spots</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500 border border-white"></span>
            <span>Attractions & Sights</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 border border-white"></span>
            <span>Medical / Hospitals</span>
          </div>
        </div>
      </div>
    </div>
  );
};
