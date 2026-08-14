'use client';

import React from 'react';

export default function StatCard({ title, value, subtext, icon: Icon, color = 'cyan', change }) {
  const colorClasses = {
    cyan: 'border-cyan-500/30 bg-cyan-500/5 text-cyan-400',
    emerald: 'border-emerald-500/30 bg-emerald-500/5 text-emerald-400',
    amber: 'border-amber-500/30 bg-amber-500/5 text-amber-400',
    red: 'border-red-500/30 bg-red-500/5 text-red-400',
    indigo: 'border-indigo-500/30 bg-indigo-500/5 text-indigo-400',
  }[color] || 'border-cyan-500/30 bg-cyan-500/5 text-cyan-400';

  return (
    <div className={`p-5 rounded-xl border backdrop-blur-md ${colorClasses} transition-all duration-200 hover:border-opacity-60 shadow-lg`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        {Icon && <Icon className="w-5 h-5 opacity-80" />}
      </div>
      <div className="mt-3 flex items-baseline justify-between">
        <div className="text-2xl font-bold text-slate-100 tracking-tight">{value}</div>
        {change !== undefined && (
          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
            change >= 0 ? 'bg-emerald-500/20 text-emerald-300' : 'bg-red-500/20 text-red-300'
          }`}>
            {change >= 0 ? `+${change}%` : `${change}%`}
          </span>
        )}
      </div>
      {subtext && <div className="mt-2 text-xs text-slate-400">{subtext}</div>}
    </div>
  );
}
