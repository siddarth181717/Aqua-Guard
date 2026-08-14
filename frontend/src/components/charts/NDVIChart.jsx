'use client';

import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function NDVIChart({ dates = [], data = [] }) {
  const chartData = dates.map((date, idx) => ({
    date,
    ndvi: data[idx] !== undefined ? data[idx] : null
  }));

  return (
    <div className="p-5 rounded-xl border border-slate-800 bg-navy-800/60 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="text-sm font-semibold text-slate-200">NDVI Vegetation Index</h4>
          <p className="text-xs text-slate-400">Normalized Difference Vegetation Index (NIR - Red)</p>
        </div>
        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">
          NDVI
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
              itemStyle={{ color: '#F59E0B' }}
              formatter={(value) => [value, 'NDVI']}
            />
            <Line type="monotone" dataKey="ndvi" stroke="#F59E0B" strokeWidth={2.5} dot={{ r: 4, fill: '#F59E0B' }} connectNulls />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
