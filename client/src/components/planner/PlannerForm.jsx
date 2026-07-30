import React, { useState } from 'react';
import { Sparkles, MapPin, IndianRupee, Calendar, Utensils, Zap, Hotel, MessageSquare } from 'lucide-react';

export const PlannerForm = ({ onSubmit, isLoading }) => {
  const [usePrompt, setUsePrompt] = useState(true);

  // Centralized TravelPreferences State
  const [travelPreferences, setTravelPreferences] = useState({
    destination: "Goa, India",
    budget: 20000,
    duration: 4,
    diet: "Vegetarian",
    luxury: "Moderate",
    adventure: "High"
  });

  const [travelers, setTravelers] = useState(2);
  const [hasChildren, setHasChildren] = useState(false);
  const [specialRequirements, setSpecialRequirements] = useState("");

  // Helper to format/generate prompt string from state values
  const generatePromptFromPreferences = (prefs) => {
    const durationStr = `${prefs.duration}-day`;
    const luxuryStr = prefs.luxury === "Luxury" ? "luxury" : (prefs.luxury === "Budget" ? "budget" : "moderate");
    
    let dietStr = "vegetarian food";
    if (prefs.diet === "Vegan") dietStr = "vegan food";
    if (prefs.diet === "Halal") dietStr = "halal food";
    if (prefs.diet === "Non-Vegetarian") dietStr = "non-vegetarian food";
    
    let adventureStr = "adventure sports";
    if (prefs.adventure === "Medium") adventureStr = "balanced sightseeing";
    if (prefs.adventure === "Low") adventureStr = "relaxed leisure";

    return `I want a ${durationStr} ${luxuryStr} trip to ${prefs.destination} under ₹${prefs.budget.toLocaleString('en-IN')} with ${dietStr} and ${adventureStr}.`;
  };

  const [naturalPrompt, setNaturalPrompt] = useState(generatePromptFromPreferences(travelPreferences));

  // Parses natural language string and extracts entities in real-time
  const parsePromptToPreferences = (promptText) => {
    const updates = {};

    // 1. Destination
    const destMatch = promptText.match(/(?:trip\s+to|visit|explore|going\s+to|travel\s+to|go\s+to|reach|to|in|near)\s+([a-zA-Z\s,]+?)(?=\s+(?:under|with|for|budget|₹|\$|\d|day|days)|[.!?]|$)/i);
    if (destMatch) {
      const rawDest = destMatch[1].trim();
      const cleaned = rawDest.replace(/^(in|to|at|around|for|the|reach|from)\s+/i, "").trim();
      if (cleaned.length > 2 && !/^(a|an|the|budget|hotel|food|place|day|days)$/i.test(cleaned)) {
        updates.destination = cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
      }
    }

    // 2. Budget
    const budgetMatch = promptText.match(/(?:budget|under|cost|price|spend|for|with|of|₹|\$|inr|rs\.?)\s*(?:of|is|to|=)?\s*(?:₹|\$)?\s*([\d,]+)/i) ||
                        promptText.match(/([\d,]+)\s*(?:inr|rs|rupees|budget)/i);
    if (budgetMatch) {
      const val = parseInt(budgetMatch[1].replace(/,/g, ''), 10);
      if (!isNaN(val) && val > 50) {
        updates.budget = val;
      }
    }

    // 3. Duration (Days)
    const durationMatch = promptText.match(/(\d+)\s*(?:-| )?day/i);
    if (durationMatch) {
      const val = parseInt(durationMatch[1], 10);
      if (!isNaN(val) && val > 0 && val <= 30) {
        updates.duration = val;
      }
    }

    // 4. Dietary Preference
    if (/vegan/i.test(promptText)) {
      updates.diet = "Vegan";
    } else if (/non-veg|non veg|non-vegetarian/i.test(promptText)) {
      updates.diet = "Non-Vegetarian";
    } else if (/halal/i.test(promptText)) {
      updates.diet = "Halal";
    } else if (/vegetarian|pure veg|veg/i.test(promptText)) {
      updates.diet = "Vegetarian";
    }

    // 5. Luxury Level
    if (/luxury|5-star|premium/i.test(promptText)) {
      updates.luxury = "Luxury";
    } else if (/budget|backpacker|cheap/i.test(promptText)) {
      updates.luxury = "Budget";
    } else if (/moderate|comfortable|mid-range/i.test(promptText)) {
      updates.luxury = "Moderate";
    }

    // 6. Adventure Level
    if (/adventure|high thrill|water sports/i.test(promptText)) {
      updates.adventure = "High";
    } else if (/balanced|sightseeing|medium/i.test(promptText)) {
      updates.adventure = "Medium";
    } else if (/relaxed|leisure|low/i.test(promptText)) {
      updates.adventure = "Low";
    }

    return updates;
  };

  // Called when user edits the text prompt directly
  const handlePromptChange = (val) => {
    setNaturalPrompt(val);
    const updates = parsePromptToPreferences(val);
    if (Object.keys(updates).length > 0) {
      setTravelPreferences(prev => ({
        ...prev,
        ...updates
      }));
    }
  };

  // Called when user changes any granular filter
  const handlePreferenceChange = (key, value) => {
    setTravelPreferences(prev => {
      const updatedPrefs = {
        ...prev,
        [key]: value
      };
      // Regenerate the prompt text using the updated preference set
      const nextPrompt = generatePromptFromPreferences(updatedPrefs);
      setNaturalPrompt(nextPrompt);
      return updatedPrefs;
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Since state is synchronized in real-time, submit payload with all fields
    const payload = {
      prompt: naturalPrompt,
      destination: travelPreferences.destination,
      budget: Number(travelPreferences.budget),
      duration_days: Number(travelPreferences.duration),
      travelers: Number(travelers),
      food_preference: travelPreferences.diet,
      luxury_level: travelPreferences.luxury,
      adventure_level: travelPreferences.adventure,
      has_children: hasChildren,
      special_requirements: specialRequirements
    };
    onSubmit(payload);
  };

  return (
    <div className="glass-panel rounded-3xl p-6 lg:p-8 border border-slate-800 shadow-2xl relative overflow-hidden">
      <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl -z-10"></div>
      
      {/* Form Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            Configure Your Autonomous Travel Genies
            <Sparkles className="w-5 h-5 text-emerald-400" />
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Specify requirements in natural language or customize granular filters.
          </p>
        </div>

        {/* Mode Selector Tabs */}
        <div className="flex bg-slate-900/90 p-1 rounded-xl border border-slate-800 self-start">
          <button
            type="button"
            onClick={() => setUsePrompt(true)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              usePrompt ? 'bg-emerald-500 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Natural Language AI Prompt
          </button>
          <button
            type="button"
            onClick={() => setUsePrompt(false)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              !usePrompt ? 'bg-emerald-500 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Granular Filters
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="mt-6 space-y-6">
        {usePrompt ? (
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2 flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-emerald-400" />
              Describe your dream trip
            </label>
            <textarea
              rows={4}
              value={naturalPrompt}
              onChange={(e) => handlePromptChange(e.target.value)}
              placeholder="e.g. I want a 5-day luxury honeymoon trip to Bali under ₹1,50,000 with sea view villas, vegan organic dining, and temple tours."
              className="w-full bg-slate-950/80 border border-slate-800 rounded-2xl p-4 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors shadow-inner"
            />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Destination */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-emerald-400" /> Destination
              </label>
              <input
                type="text"
                value={travelPreferences.destination}
                onChange={(e) => handlePreferenceChange('destination', e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500"
              />
            </div>

            {/* Budget */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <IndianRupee className="w-3.5 h-3.5 text-emerald-400" /> Budget (INR)
              </label>
              <input
                type="number"
                value={travelPreferences.budget}
                onChange={(e) => handlePreferenceChange('budget', Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500"
              />
            </div>

            {/* Duration Days */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-emerald-400" /> Duration (Days)
              </label>
              <input
                type="number"
                min={1}
                max={30}
                value={travelPreferences.duration}
                onChange={(e) => handlePreferenceChange('duration', Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500"
              />
            </div>

            {/* Food Preference */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <Utensils className="w-3.5 h-3.5 text-emerald-400" /> Dietary Preference
              </label>
              <select
                value={travelPreferences.diet}
                onChange={(e) => handlePreferenceChange('diet', e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500"
              >
                <option value="Vegetarian">Pure Vegetarian</option>
                <option value="Vegan">Vegan</option>
                <option value="Non-Vegetarian">Non-Vegetarian</option>
                <option value="Halal">Halal</option>
              </select>
            </div>

            {/* Luxury Level */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <Hotel className="w-3.5 h-3.5 text-emerald-400" /> Luxury Level
              </label>
              <select
                value={travelPreferences.luxury}
                onChange={(e) => handlePreferenceChange('luxury', e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500"
              >
                <option value="Budget">Backpacker / Budget</option>
                <option value="Moderate">Moderate / Comfortable</option>
                <option value="Luxury">5-Star Luxury</option>
              </select>
            </div>

            {/* Adventure Level */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-emerald-400" /> Adventure Level
              </label>
              <select
                value={travelPreferences.adventure}
                onChange={(e) => handlePreferenceChange('adventure', e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500"
              >
                <option value="Low">Relaxed & Leisure</option>
                <option value="Medium">Balanced Sightseeing</option>
                <option value="High">High Thrill & Water Sports</option>
              </select>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-4 rounded-2xl bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white font-bold text-sm tracking-wide shadow-xl shadow-emerald-500/25 transition-all flex items-center justify-center gap-2.5 disabled:opacity-50"
        >
          <Sparkles className="w-5 h-5 animate-spin-slow" />
          {isLoading ? "Autonomous Agents Thinking..." : "Launch Autonomous Agents & Generate Plan"}
        </button>
      </form>
    </div>
  );
};
