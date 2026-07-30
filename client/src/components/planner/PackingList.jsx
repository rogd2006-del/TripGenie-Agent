import React from 'react';
import { Briefcase, CheckCircle2, ShieldAlert, Phone } from 'lucide-react';

export const PackingList = ({ items = [], emergencyContacts = [] }) => {
  return (
    <div className="glass-panel rounded-3xl p-6 lg:p-8 border border-slate-800 shadow-2xl grid grid-cols-1 md:grid-cols-2 gap-6">
      
      {/* Packing Checklist */}
      <div className="space-y-4">
        <div className="flex items-center gap-2.5 border-b border-slate-800 pb-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
            <Briefcase className="w-4 h-4 text-emerald-400" />
          </div>
          <h4 className="text-sm font-bold text-white uppercase tracking-wider">Suggested Packing Checklist</h4>
        </div>

        <ul className="space-y-2 text-xs">
          {items.map((item, idx) => (
            <li key={idx} className="flex items-center gap-2.5 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80 text-slate-300">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Emergency Contacts */}
      <div className="space-y-4">
        <div className="flex items-center gap-2.5 border-b border-slate-800 pb-3">
          <div className="w-8 h-8 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-center justify-center">
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <h4 className="text-sm font-bold text-white uppercase tracking-wider">Emergency Helplines</h4>
        </div>

        <div className="space-y-2 text-xs">
          {emergencyContacts.map((contact, idx) => (
            <div key={idx} className="flex items-center justify-between bg-rose-950/20 p-3 rounded-xl border border-rose-900/30 text-rose-200">
              <span className="font-semibold">{contact.name}</span>
              <span className="font-mono text-xs font-bold flex items-center gap-1">
                <Phone className="w-3.5 h-3.5" /> {contact.phone}
              </span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
