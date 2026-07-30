import React from 'react';
import { Cpu, CheckCircle2, Loader2, AlertCircle, Sparkles, Layers } from 'lucide-react';

const ALL_AGENTS = [
  { key: 'supervisor', name: 'Supervisor Agent', icon: '🧠' },
  { key: 'planner', name: 'Planner Agent', icon: '📝' },
  { key: 'destination', name: 'Destination Agent', icon: '📍' },
  { key: 'weather', name: 'Weather Agent', icon: '🌤️' },
  { key: 'hotel', name: 'Hotel Agent', icon: '🏨' },
  { key: 'transport', name: 'Transport Agent', icon: '✈️' },
  { key: 'restaurant', name: 'Restaurant Agent', icon: '🍲' },
  { key: 'budget', name: 'Budget Agent', icon: '💰' },
  { key: 'itinerary', name: 'Itinerary Agent', icon: '📅' },
  { key: 'packing', name: 'Packing Agent', icon: '🎒' },
  { key: 'report', name: 'Report Generator', icon: '📄' },
];

export const AgentStreamVisualizer = ({ logs = [], isCompleted = false }) => {
  const getAgentStatus = (agentName) => {
    if (isCompleted) return 'completed';
    const keyword = agentName.toLowerCase().replace(' agent', '').replace(' generator', '');
    const agentLogs = logs.filter(l => l.agent_name?.toLowerCase().includes(keyword));
    if (agentLogs.length === 0) return 'pending';
    const last = agentLogs[agentLogs.length - 1];
    if (last.status === 'completed') return 'completed';
    if (last.status === 'error') return 'error';
    return 'in_progress';
  };

  return (
    <div className="glass-panel rounded-3xl p-6 lg:p-8 border border-slate-800 shadow-2xl space-y-6">
      
      {/* Visualizer Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
            <Cpu className="w-5 h-5 text-emerald-400 animate-pulse" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              LangGraph Multi-Agent Orchestration Swarm
              <Sparkles className="w-4 h-4 text-cyan-400" />
            </h3>
            <span className="text-xs text-slate-400">10 Autonomous Specialized Agent Nodes Executing</span>
          </div>
        </div>

        {isCompleted ? (
          <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-bold flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4" /> Workflow Executed
          </span>
        ) : (
          <span className="px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 text-xs font-bold flex items-center gap-1.5">
            <Loader2 className="w-4 h-4 animate-spin" /> Thinking Live...
          </span>
        )}
      </div>

      {/* Grid of 11 Swarm Agents */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {ALL_AGENTS.map((agent) => {
          const status = getAgentStatus(agent.name);
          return (
            <div
              key={agent.key}
              className={`p-3 rounded-2xl border transition-all flex flex-col items-center text-center ${
                status === 'completed'
                  ? 'bg-emerald-950/40 border-emerald-500/50 text-emerald-300 shadow-lg shadow-emerald-500/10'
                  : status === 'in_progress'
                  ? 'bg-cyan-950/40 border-cyan-400 text-cyan-200 animate-pulse'
                  : status === 'error'
                  ? 'bg-rose-950/40 border-rose-500 text-rose-300'
                  : 'bg-slate-900/60 border-slate-800/80 text-slate-500 opacity-60'
              }`}
            >
              <span className="text-xl mb-1">{agent.icon}</span>
              <span className="text-[11px] font-bold tracking-tight">{agent.name}</span>
              
              <div className="mt-2 text-[10px] font-mono flex items-center gap-1">
                {status === 'completed' && <CheckCircle2 className="w-3 h-3 text-emerald-400" />}
                {status === 'in_progress' && <Loader2 className="w-3 h-3 text-cyan-400 animate-spin" />}
                {status === 'error' && <AlertCircle className="w-3 h-3 text-rose-400" />}
                {status === 'pending' && <span className="w-2 h-2 rounded-full bg-slate-700"></span>}
                <span className="capitalize">{status.replace('_', ' ')}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Live Stream Terminal Logs */}
      <div className="bg-slate-950 rounded-2xl p-4 border border-slate-900 font-mono text-xs max-h-48 overflow-y-auto space-y-2 text-slate-300 shadow-inner">
        <div className="text-[11px] text-slate-500 uppercase tracking-widest font-bold flex items-center gap-1 mb-2">
          <Layers className="w-3.5 h-3.5" /> Agent Execution Stream Log
        </div>
        {logs.length === 0 ? (
          <p className="text-slate-600 italic">Waiting for Supervisor Agent initialization...</p>
        ) : (
          logs.map((log, idx) => (
            <div key={idx} className="flex items-start gap-2 leading-relaxed">
              <span className="text-emerald-400 font-semibold">[{log.agent_name}]</span>
              <span className={log.status === 'completed' ? 'text-slate-300' : 'text-cyan-300 font-medium'}>
                {log.message}
              </span>
            </div>
          ))
        )}
      </div>

    </div>
  );
};
