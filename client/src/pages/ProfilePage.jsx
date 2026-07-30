import React from 'react';
import { User, Mail, ShieldCheck, Calendar } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { GlassCard } from '../components/common/GlassCard';

export const ProfilePage = () => {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="max-w-xl mx-auto space-y-8">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">User Profile</h1>
        <p className="text-xs text-slate-400">Account overview & credentials</p>
      </div>

      <GlassCard hover={false} className="p-8 text-center space-y-6">
        <img
          src={user.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80'}
          alt="User Avatar"
          className="w-24 h-24 rounded-full object-cover ring-4 ring-emerald-500/30 mx-auto"
        />

        <div className="space-y-1">
          <h2 className="text-xl font-bold text-white">{user.full_name}</h2>
          <p className="text-xs text-emerald-400 font-medium flex items-center justify-center gap-1">
            <Mail className="w-3.5 h-3.5" /> {user.email}
          </p>
        </div>

        <div className="pt-6 border-t border-slate-800 text-xs grid grid-cols-2 gap-4 text-left">
          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
            <span className="text-slate-400 block text-[10px] uppercase">Account Type</span>
            <span className="font-bold text-white flex items-center gap-1 mt-0.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Pro Planner
            </span>
          </div>

          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
            <span className="text-slate-400 block text-[10px] uppercase">Dietary Preference</span>
            <span className="font-bold text-white mt-0.5 block">{user.preferences?.diet || 'Vegetarian'}</span>
          </div>
        </div>
      </GlassCard>
    </div>
  );
};
