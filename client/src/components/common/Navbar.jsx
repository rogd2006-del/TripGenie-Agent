import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Compass, Sparkles, LayoutDashboard, Bookmark, Settings, User, LogOut, Moon, Sun, Menu, X } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { useTheme } from '../../hooks/useTheme';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md px-4 lg:px-8 py-3.5 transition-all">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 via-teal-400 to-cyan-500 p-0.5 shadow-lg shadow-emerald-500/20 group-hover:scale-105 transition-transform">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Compass className="w-5 h-5 text-emerald-400 animate-spin-slow" />
            </div>
          </div>
          <div className="flex flex-col">
            <span className="text-xl font-extrabold tracking-tight text-white flex items-center gap-1">
              Trip<span className="text-emerald-400">Genie</span>
              <Sparkles className="w-4 h-4 text-cyan-400 fill-cyan-400/20" />
            </span>
            <span className="text-[10px] font-medium tracking-widest text-slate-400 uppercase -mt-1">Autonomous AI</span>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <div className="hidden md:flex items-center gap-1.5 bg-slate-900/60 p-1.5 rounded-full border border-slate-800/80">
          <Link
            to="/planner"
            className={`px-4 py-2 rounded-full text-sm font-semibold transition-all flex items-center gap-2 ${
              isActive('/planner')
                ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-md shadow-emerald-500/25'
                : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            AI Planner
          </Link>

          <Link
            to="/dashboard"
            className={`px-4 py-2 rounded-full text-sm font-semibold transition-all flex items-center gap-2 ${
              isActive('/dashboard')
                ? 'bg-slate-800 text-emerald-400 border border-emerald-500/30'
                : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <LayoutDashboard className="w-4 h-4" />
            Dashboard
          </Link>

          <Link
            to="/saved"
            className={`px-4 py-2 rounded-full text-sm font-semibold transition-all flex items-center gap-2 ${
              isActive('/saved')
                ? 'bg-slate-800 text-emerald-400 border border-emerald-500/30'
                : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Bookmark className="w-4 h-4" />
            Saved Trips
          </Link>

          <Link
            to="/settings"
            className={`px-4 py-2 rounded-full text-sm font-semibold transition-all flex items-center gap-2 ${
              isActive('/settings')
                ? 'bg-slate-800 text-emerald-400 border border-emerald-500/30'
                : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Settings className="w-4 h-4" />
            Settings
          </Link>
        </div>

        {/* Right Action Icons & Auth */}
        <div className="hidden md:flex items-center gap-3">
          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2.5 rounded-full bg-slate-900 border border-slate-800 text-slate-300 hover:text-amber-400 hover:border-amber-400/30 transition-all"
            title="Toggle theme"
          >
            {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>

          {user ? (
            <div className="flex items-center gap-3">
              <Link to="/profile" className="flex items-center gap-2.5 p-1.5 pr-3 rounded-full bg-slate-900 border border-slate-800 hover:border-emerald-500/40 transition-all">
                <img src={user.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80'} alt="Avatar" className="w-7 h-7 rounded-full object-cover ring-2 ring-emerald-500/40" />
                <span className="text-xs font-semibold text-slate-200">{user.full_name?.split(' ')[0]}</span>
              </Link>
              <button
                onClick={logout}
                className="p-2.5 rounded-full bg-slate-900 border border-slate-800 text-slate-400 hover:text-rose-400 hover:border-rose-500/30 transition-all"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link to="/login" className="px-4 py-2 rounded-full text-xs font-bold text-slate-300 hover:text-white hover:bg-slate-800 transition-all">
                Login
              </Link>
              <Link to="/register" className="px-4 py-2 rounded-full text-xs font-bold bg-emerald-500 hover:bg-emerald-600 text-white shadow-md shadow-emerald-500/20 transition-all">
                Register
              </Link>
            </div>
          )}
        </div>

        {/* Mobile Hamburger Toggle */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-300"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Drawer Navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden pt-4 pb-3 px-2 border-t border-slate-800/80 mt-3 space-y-2">
          <Link to="/planner" onClick={() => setMobileMenuOpen(false)} className="block px-4 py-2.5 rounded-xl font-medium text-slate-200 hover:bg-slate-800">
            AI Planner
          </Link>
          <Link to="/dashboard" onClick={() => setMobileMenuOpen(false)} className="block px-4 py-2.5 rounded-xl font-medium text-slate-200 hover:bg-slate-800">
            Dashboard
          </Link>
          <Link to="/saved" onClick={() => setMobileMenuOpen(false)} className="block px-4 py-2.5 rounded-xl font-medium text-slate-200 hover:bg-slate-800">
            Saved Trips
          </Link>
          <Link to="/settings" onClick={() => setMobileMenuOpen(false)} className="block px-4 py-2.5 rounded-xl font-medium text-slate-200 hover:bg-slate-800">
            Settings
          </Link>
          <Link to="/profile" onClick={() => setMobileMenuOpen(false)} className="block px-4 py-2.5 rounded-xl font-medium text-slate-200 hover:bg-slate-800">
            Profile
          </Link>
        </div>
      )}
    </nav>
  );
};
