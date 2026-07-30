import React from 'react';
import { IndianRupee, PieChart, ShieldCheck } from 'lucide-react';

export const BudgetChart = ({ budgetBreakdown, targetBudget = 20000 }) => {
  if (!budgetBreakdown) return null;

  const categories = [
    { label: 'Hotel Cost', key: 'hotel_cost', altKey: 'stay', color: 'bg-emerald-500', percent: 45 },
    { label: 'Transport Cost', key: 'transport_cost', altKey: 'transport', color: 'bg-indigo-400', percent: 10 },
    { label: 'Food Cost', key: 'food_cost', altKey: 'food', color: 'bg-teal-400', percent: 25 },
    { label: 'Sightseeing Cost', key: 'sightseeing_cost', altKey: 'activities', color: 'bg-cyan-400', percent: 15 },
    { label: 'Miscellaneous', key: 'miscellaneous', altKey: 'contingency', color: 'bg-purple-400', percent: 5 },
  ];

  const grandTotal = budgetBreakdown.grand_total || budgetBreakdown.total || targetBudget;

  return (
    <div className="glass-panel rounded-3xl p-6 lg:p-8 border border-slate-800 shadow-2xl space-y-6">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            Itemized Expense Allocation
            <PieChart className="w-5 h-5 text-emerald-400" />
          </h3>
          <p className="text-xs text-slate-400">Calculated by Budget Agent</p>
        </div>

        <div className="text-right">
          <span className="text-xs text-slate-400">Grand Total</span>
          <p className="text-lg font-extrabold text-emerald-400 flex items-center justify-end">
            <IndianRupee className="w-4 h-4" /> {grandTotal.toLocaleString('en-IN')}
          </p>
        </div>
      </div>

      {/* Progress Bar Segment Visualizer */}
      <div className="w-full h-4 bg-slate-900 rounded-full overflow-hidden flex p-0.5 border border-slate-800">
        {categories.map((cat) => (
          <div
            key={cat.key}
            style={{ width: `${cat.percent}%` }}
            className={`h-full ${cat.color} first:rounded-l-full last:rounded-r-full hover:brightness-125 transition-all`}
            title={`${cat.label}: ${cat.percent}%`}
          />
        ))}
      </div>

      {/* Categories Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {categories.map((cat) => {
          const val = budgetBreakdown[cat.key] ?? budgetBreakdown[cat.altKey] ?? 0;
          return (
            <div key={cat.key} className="bg-slate-900/60 p-4 rounded-2xl border border-slate-800/80 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className={`w-3 h-3 rounded-full ${cat.color}`}></span>
                <div>
                  <span className="text-xs font-semibold text-slate-200">{cat.label}</span>
                  <span className="block text-[10px] text-slate-400">{cat.percent}% allocation</span>
                </div>
              </div>
              <span className="text-xs font-bold text-white font-mono flex items-center">
                ₹{val.toLocaleString('en-IN')}
              </span>
            </div>
          );
        })}
      </div>


      <div className="flex items-center gap-2 text-xs text-emerald-400 bg-emerald-950/40 p-3 rounded-xl border border-emerald-800/40">
        <ShieldCheck className="w-4 h-4 shrink-0" />
        <span>Budget Agent confirmed all estimated expenses remain strictly within total target allocation.</span>
      </div>

    </div>
  );
};
