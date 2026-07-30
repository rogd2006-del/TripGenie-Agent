import React from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from '../common/Navbar';
import { Footer } from '../common/Footer';
import { FloatingAssistant } from '../common/FloatingAssistant';

export const Layout = () => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-emerald-500 selection:text-white relative">
      <Navbar />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 py-8">
        <Outlet />
      </main>
      <Footer />
      <FloatingAssistant />
    </div>
  );
};
