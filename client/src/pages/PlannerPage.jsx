import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, Download, Bookmark, AlertTriangle } from 'lucide-react';
import { plannerService } from '../services/plannerService';
import { tripService } from '../services/tripService';
import { PlannerForm } from '../components/planner/PlannerForm';
import { AgentStreamVisualizer } from '../components/planner/AgentStreamVisualizer';
import { ItineraryView } from '../components/planner/ItineraryView';
import { BudgetChart } from '../components/planner/BudgetChart';
import { MapView } from '../components/common/MapView';
import { HotelCard } from '../components/planner/HotelCard';
import { TransportCard } from '../components/planner/TransportCard';
import { WeatherCard } from '../components/planner/WeatherCard';
import { RestaurantCard } from '../components/planner/RestaurantCard';
import { PackingList } from '../components/planner/PackingList';

export const PlannerPage = () => {
  const [logs, setLogs] = useState([]);
  const [isPlanning, setIsPlanning] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [generatedTrip, setGeneratedTrip] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const navigate = useNavigate();

  const handleStartPlanning = async (payload) => {
    setIsPlanning(true);
    setIsCompleted(false);
    setLogs([]);
    setGeneratedTrip(null);
    setErrorMessage(null);

    try {
      const res = await plannerService.startPlannerStream(
        payload,
        (event) => {
          setLogs(prev => [...prev, event]);
          if (event.error || event.status === 'failed') {
            setIsPlanning(false);
            setErrorMessage(event.message || 'Backend server is offline.');
          }
          if (event.status === 'completed' && event.trip_data) {
            setGeneratedTrip(event.trip_data);
            setIsCompleted(true);
            setIsPlanning(false);
          }
        },
        (errorLog) => {
          setIsPlanning(false);
          setErrorMessage(errorLog.message || 'Backend server is offline.');
        }
      );

      if (res && !res.success) {
        setIsPlanning(false);
        setErrorMessage(res.error || 'Backend server is offline.');
      }
    } catch (err) {
      console.error("[PlannerPage] Planning stream error caught:", err);
      setIsPlanning(false);
      setErrorMessage('Backend server is offline.');
    }
  };

  const handleSaveTrip = async () => {
    if (!generatedTrip) return;
    const tId = generatedTrip.id || generatedTrip._id;
    try {
      await tripService.saveTrip(tId);
      alert('Trip saved to your bookmarks!');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8">
      
      {/* Top Banner */}
      <div className="space-y-2 text-center max-w-2xl mx-auto">
        <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center justify-center gap-2">
          Autonomous AI Travel Planner
          <Sparkles className="w-6 h-6 text-emerald-400" />
        </h1>
        <p className="text-xs text-slate-400">
          Enter natural language prompt or customized filters to launch the 10 LangGraph sub-agent swarm.
        </p>
      </div>

      {/* Error / Offline Alert Banner */}
      {errorMessage && (
        <div className="max-w-2xl mx-auto bg-rose-500/10 border border-rose-500/30 text-rose-400 p-4 rounded-2xl text-xs flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
            <div>
              <span className="font-bold text-sm block">{errorMessage}</span>
              <p className="text-[11px] text-rose-300/80 mt-0.5">Please ensure the FastAPI backend server is running via `uvicorn main:app --reload` on http://localhost:8000.</p>
            </div>
          </div>
          <button 
            onClick={() => setErrorMessage(null)} 
            className="text-[11px] font-semibold bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 px-3 py-1.5 rounded-xl transition-all shrink-0"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Input Form */}
      <PlannerForm onSubmit={handleStartPlanning} isLoading={isPlanning} />

      {/* Visualizer during execution or upon completion */}
      {(isPlanning || logs.length > 0) && (
        <AgentStreamVisualizer logs={logs} isCompleted={isCompleted} />
      )}

      {/* Generated Trip Plan Output */}
      {generatedTrip && (
        <div className="space-y-8 animate-in fade-in duration-500">
          
          {/* Action Bar */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-extrabold text-white">{generatedTrip.title}</h2>
              <p className="text-xs text-slate-400 mt-0.5">{generatedTrip.summary}</p>
            </div>

            <div className="flex items-center gap-3 shrink-0">
              <button
                onClick={handleSaveTrip}
                className="px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-bold text-slate-200 hover:text-emerald-400 transition-all flex items-center gap-1.5"
              >
                <Bookmark className="w-4 h-4" /> Save Bookmark
              </button>
              
              <a
                href={tripService.getPdfDownloadUrl(generatedTrip.id || generatedTrip._id)}
                download
                className="px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-bold text-xs shadow-md shadow-emerald-500/20 transition-all flex items-center gap-1.5"
              >
                <Download className="w-4 h-4" /> Export PDF Report
              </a>
            </div>
          </div>

          {/* Interactive Map View */}
          <MapView destination={generatedTrip.destination} mapInfo={generatedTrip.destination_details?.map_info} trip={generatedTrip} />

          {/* Itinerary */}
          <ItineraryView itinerary={generatedTrip.itinerary} />

          {/* Budget Allocation */}
          <BudgetChart budgetBreakdown={generatedTrip.budget_breakdown} targetBudget={generatedTrip.budget} />

          {/* Hotels & Transport Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Lodging Recommendations</h3>
              {(!generatedTrip.hotels || generatedTrip.hotels.length === 0) ? (
                <div className="glass-card rounded-2xl p-6 text-center text-slate-400 text-xs border border-slate-800">
                  {generatedTrip.hotel_message || `No hotels were found within your budget of ₹${generatedTrip.budget?.toLocaleString('en-IN') || ''}. Consider increasing your budget or choosing another nearby area.`}
                </div>
              ) : (
                generatedTrip.hotels.map((h, i) => (
                  <HotelCard key={i} hotel={h} />
                ))
              )}
            </div>

            <div className="space-y-6">
              <TransportCard transport={generatedTrip.transport} />
              <WeatherCard weather={generatedTrip.weather} />
            </div>
          </div>

          {/* Dining Spots */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Curated Dining Spots ({generatedTrip.food_preference})</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {generatedTrip.restaurants?.map((r, i) => (
                <RestaurantCard key={i} restaurant={r} />
              ))}
            </div>
          </div>

          {/* Packing & Emergency */}
          <PackingList items={generatedTrip.packing_list} emergencyContacts={generatedTrip.emergency_contacts} />

        </div>
      )}

    </div>
  );
};
