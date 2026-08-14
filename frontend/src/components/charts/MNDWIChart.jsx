'use client';

import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function MNDWIChart({ dates = [], data = [] }) {
  const chartData = dates.map((date, idx) => ({
    date,
    mndwi: data[idx] !== undefined ? data[idx] : null
  }));

  return (
    <div className="p-5 rounded-xl border border-slate-800 bg-navy-800/60 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="text-sm font-semibold text-slate-200">MNDWI Index Trend</h4>
          <p className="text-xs text-slate-400">Modified Normalized Difference Water Index (Green - SWIR)</p>
        </div>
        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
          MNDWI
        </span>
      </div>

      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
            <XAxis dataKey="date" stroke="#64748B" fontSize={11} tickLine={false} />
            <YAxis stroke="#64748B" fontSize={11} tickLine={false} domain={[-1, 1]} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0B192C', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
              labelStyle={{ color: '#94A3B8' }}
              itemStyle={{ color: '#10B981' }}
              formatter={(value) => [value, 'MNDWI']}
            />
            <Line type="monotone" dataKey="mndwi" stroke="#10B981" strokeWidth={2.5} dot={{ r: 4, fill: '#10B981' }} connectNulls />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
