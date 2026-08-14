'use client';

import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function RainfallChart({ dates = [], data = [] }) {
  const chartData = dates.map((date, idx) => ({
    date,
    rainfall: data[idx] !== undefined ? data[idx] : null
  }));

  const hasData = data.some(val => val !== null && val !== undefined);

  return (
    <div className="p-5 rounded-xl border border-slate-800 bg-navy-800/60 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="text-sm font-semibold text-slate-200">Antecedent Rainfall Context</h4>
          <p className="text-xs text-slate-400">Precipitation context in millimeters (mm)</p>
        </div>
        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
          Rainfall (mm)
        </span>
      </div>

      {!hasData ? (
        <div className="h-56 flex items-center justify-center text-xs text-slate-400 bg-slate-800/30 rounded-lg">
          Rainfall data unavailable for this period.
        </div>
      ) : (
        <div className="h-56 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
              <XAxis dataKey="date" stroke="#64748B" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0B192C', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                labelStyle={{ color: '#94A3B8' }}
                itemStyle={{ color: '#818CF8' }}
                formatter={(value) => [`${value} mm`, 'Rainfall']}
              />
              <Bar dataKey="rainfall" fill="#6366F1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
