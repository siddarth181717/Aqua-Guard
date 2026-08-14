'use client';

import React from 'react';

const LEGEND_ITEMS = [
  { label: 'GOOD / LOW RISK', color: '#10B981' },
  { label: 'MODERATE', color: '#F59E0B' },
  { label: 'HIGH RISK', color: '#F97316' },
  { label: 'CRITICAL', color: '#EF4444' },
];

export default function MapLegend() {
  return (
    <div className="p-3 rounded-lg border border-slate-800 bg-navy-800/90 backdrop-blur-md shadow-xl text-xs space-y-2">
      <div className="font-semibold text-slate-300 border-b border-slate-700/60 pb-1 text-[11px] uppercase tracking-wider">
        Restoration Priority Legend
      </div>
      <div className="space-y-1.5">
        {LEGEND_ITEMS.map((item) => (
          <div key={item.label} className="flex items-center space-x-2">
            <span className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
            <span className="text-[11px] text-slate-300 font-medium">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
