'use client';

import React from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function WaterAreaChart({ dates = [], data = [] }) {
  const chartData = dates.map((date, idx) => ({
    date,
    area_ha: data[idx] !== undefined ? data[idx] : null
  }));

  return (
    <div className="p-5 rounded-xl border border-slate-800 bg-navy-800/60 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="text-sm font-semibold text-slate-200">Historical Water Spread Area</h4>
          <p className="text-xs text-slate-400">Water area trend in hectares (ha)</p>
        </div>
        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
          Area (ha)
        </span>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.4}/>
                <stop offset="95%" stopColor="#06B6D4" stopOpacity={0.0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
            <XAxis dataKey="date" stroke="#64748B" fontSize={11} tickLine={false} />
            <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0B192C', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
              labelStyle={{ color: '#94A3B8' }}
              itemStyle={{ color: '#06B6D4' }}
              formatter={(value) => [`${value} ha`, 'Water Area']}
            />
            <Area type="monotone" dataKey="area_ha" stroke="#06B6D4" strokeWidth={2.5} fillOpacity={1} fill="url(#areaGradient)" connectNulls />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
