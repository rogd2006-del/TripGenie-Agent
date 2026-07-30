import React, { useState } from 'react';
import { Settings, Cpu, Globe, Utensils, Save, Check } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import api from '../services/api';

export const SettingsPage = () => {
  const { user } = useAuth();
  const [provider, setProvider] = useState(user?.preferences?.model_provider || 'openai');
  const [currency, setCurrency] = useState(user?.preferences?.currency || 'INR');
  const [diet, setDiet] = useState(user?.preferences?.diet || 'Vegetarian');
  const [luxury, setLuxury] = useState(user?.preferences?.luxury_level || 'Moderate');
  const [saved, setSaved] = useState(false);

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      await api.put('/user/preferences', {
        model_provider: provider,
        currency,
        diet,
        luxury_level: luxury
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div className="space-y-2">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
          System & LLM Settings
          <Settings className="w-6 h-6 text-emerald-400" />
        </h1>
        <p className="text-xs text-slate-400">Configure AI model engine, currency, and travel defaults.</p>
      </div>

      <form onSubmit={handleSave} className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 space-y-6">
        
        {/* LLM Engine Selection */}
        <div className="space-y-3 pb-6 border-b border-slate-800">
          <label className="text-sm font-bold text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-emerald-400" /> Default AI Model Provider
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <label
              onClick={() => setProvider('openai')}
              className={`p-4 rounded-2xl border cursor-pointer transition-all flex flex-col justify-between ${
                provider === 'openai' ? 'bg-emerald-950/40 border-emerald-500 text-white' : 'bg-slate-900/60 border-slate-800 text-slate-400'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm">OpenAI GPT-4.1 / GPT-4o</span>
                {provider === 'openai' && <Check className="w-4 h-4 text-emerald-400" />}
              </div>
              <span className="text-[11px] text-slate-400 mt-2">Cloud ultra-fast reasoning multi-agent swarm.</span>
            </label>

            <label
              onClick={() => setProvider('ollama')}
              className={`p-4 rounded-2xl border cursor-pointer transition-all flex flex-col justify-between ${
                provider === 'ollama' ? 'bg-emerald-950/40 border-emerald-500 text-white' : 'bg-slate-900/60 border-slate-800 text-slate-400'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm">Ollama Local LLM</span>
                {provider === 'ollama' && <Check className="w-4 h-4 text-emerald-400" />}
              </div>
              <span className="text-[11px] text-slate-400 mt-2">Runs locally on http://localhost:11434 (Llama 3).</span>
            </label>
          </div>
        </div>

        {/* Currency & Dietary Defaults */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 text-xs">
          <div>
            <label className="block text-slate-300 font-semibold mb-1.5 flex items-center gap-1.5">
              <Globe className="w-3.5 h-3.5 text-cyan-400" /> Default Currency
            </label>
            <select
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="INR">INR (₹)</option>
              <option value="USD">USD ($)</option>
              <option value="EUR">EUR (€)</option>
              <option value="GBP">GBP (£)</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1.5 flex items-center gap-1.5">
              <Utensils className="w-3.5 h-3.5 text-teal-400" /> Dietary Preference
            </label>
            <select
              value={diet}
              onChange={(e) => setDiet(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="Vegetarian">Pure Vegetarian</option>
              <option value="Vegan">Vegan</option>
              <option value="Non-Vegetarian">Non-Vegetarian</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          className="w-full py-3.5 rounded-2xl bg-emerald-500 hover:bg-emerald-600 text-white font-bold text-xs shadow-lg shadow-emerald-500/20 transition-all flex items-center justify-center gap-2"
        >
          <Save className="w-4 h-4" /> Save Preferences
        </button>

        {saved && (
          <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 text-xs text-center font-bold">
            Preferences updated successfully!
          </div>
        )}

      </form>
    </div>
  );
};
