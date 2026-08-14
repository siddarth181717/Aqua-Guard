'use client';

import React from 'react';
import { MapPin, Calendar, Database, ShieldCheck } from 'lucide-react';
import PriorityBadge from './PriorityBadge';
import HealthIndicator from './HealthIndicator';
import { formatDate } from '@/utils/formatters';

export default function WaterBodyDetails({ waterBody, latestObs, prediction }) {
  if (!waterBody) return null;

  return (
    <div className="p-6 rounded-xl border border-slate-800 bg-navy-800/80 shadow-xl space-y-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              {waterBody.water_body_id}
            </span>
            <span className="text-xs text-slate-400">|</span>
            <div className="flex items-center space-x-1 text-xs text-slate-400">
              <MapPin className="w-3.5 h-3.5 text-cyan-400" />
              <span>{waterBody.district}, {waterBody.state}</span>
            </div>
          </div>
          <h1 className="text-2xl font-bold text-slate-100 mt-1">{waterBody.name}</h1>
        </div>

        <div className="flex items-center space-x-3">
          <div className="text-right">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Health Status</span>
            <HealthIndicator healthClass={prediction?.health_class || 'MODERATE'} />
          </div>
          <div className="text-right">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Restoration Priority</span>
            <PriorityBadge priority={prediction?.priority || 'LOW'} />
          </div>
        </div>
      </div>

      <div className="pt-3 border-t border-slate-800 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-2">
        <div className="flex items-center space-x-1.5">
          <Calendar className="w-4 h-4 text-cyan-400 shrink-0" />
          <span>Latest Available Observation: <strong className="text-slate-200">{formatDate(latestObs?.acquisition_date)}</strong></span>
        </div>
        <div className="flex items-center space-x-1.5">
          <Database className="w-4 h-4 text-cyan-400 shrink-0" />
          <span>Source: <strong className="text-slate-200">{latestObs?.source || waterBody.source || 'Sentinel-2 GEE'}</strong></span>
        </div>
      </div>
    </div>
  );
}
