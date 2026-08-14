'use client';

import React from 'react';
import Link from 'next/link';
import { Waves, ArrowRight, MapPin } from 'lucide-react';
import PriorityBadge from './PriorityBadge';
import { formatAreaHa } from '@/utils/formatters';

export default function WaterBodyCard({ waterBody, onSelect }) {
  const { water_body_id, name, state, district, area_hectares, priority } = waterBody;

  return (
    <div className="p-5 rounded-xl border border-slate-800 bg-navy-800/60 hover:border-cyan-500/40 transition-all duration-200 shadow-lg flex flex-col justify-between space-y-4">
      <div>
        <div className="flex items-start justify-between">
          <div>
            <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest">{water_body_id}</span>
            <h3 className="text-base font-bold text-slate-100 mt-0.5">{name}</h3>
          </div>
          <PriorityBadge priority={priority || 'LOW'} />
        </div>

        <div className="mt-3 flex items-center space-x-1.5 text-xs text-slate-400">
          <MapPin className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
          <span>{district}, {state}</span>
        </div>
      </div>

      <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
        <div>
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Water Area</span>
          <span className="text-sm font-semibold text-slate-200">{formatAreaHa(area_hectares)}</span>
        </div>

        <div className="flex items-center space-x-2">
          {onSelect && (
            <button
              onClick={() => onSelect(waterBody)}
              className="px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-800 text-cyan-300 hover:bg-slate-700 transition-colors"
            >
              Locate
            </button>
          )}
          <Link
            href={`/water-bodies/${water_body_id}`}
            className="flex items-center space-x-1 px-3 py-1 text-xs font-semibold rounded-lg bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/30 transition-colors border border-cyan-500/40"
          >
            <span>View Details</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
}
