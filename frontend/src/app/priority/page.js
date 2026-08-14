'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { AlertOctagon, ArrowRight, ShieldCheck, RefreshCw } from 'lucide-react';
import PriorityBadge from '@/components/waterbody/PriorityBadge';
import HealthIndicator from '@/components/waterbody/HealthIndicator';
import Loading from '@/components/common/Loading';
import ErrorMessage from '@/components/common/ErrorMessage';
import apiService from '@/services/api';
import { formatAreaHa } from '@/utils/formatters';

export default function PriorityPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [priorities, setPriorities] = useState([]);

  const fetchPriorities = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiService.getPriorities();
      setPriorities(res?.data || []);
    } catch (err) {
      console.error('Failed fetching priorities:', err);
      setError(err.message || 'Unable to load restoration priority rankings.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPriorities();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-300 border border-red-500/30 mb-2">
            <AlertOctagon className="w-3.5 h-3.5" />
            <span>AI-Driven Priority Ranking</span>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight">Restoration Priority Queue</h1>
          <p className="text-xs text-slate-400 mt-1">Water bodies ordered by evaluated restoration urgency and environmental degradation severity.</p>
        </div>

        <button
          onClick={fetchPriorities}
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-cyan-300 transition-colors border border-slate-700/60 shrink-0"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Rankings</span>
        </button>
      </div>

      {loading ? (
        <Loading message="Computing AI model priority rankings..." />
      ) : error ? (
        <ErrorMessage message={error} onRetry={fetchPriorities} />
      ) : (
        <div className="p-6 rounded-xl border border-slate-800 bg-navy-800/80 shadow-xl space-y-4">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="p-3">Rank</th>
                  <th className="p-3">Water Body</th>
                  <th className="p-3">District / State</th>
                  <th className="p-3">Health Status</th>
                  <th className="p-3">Priority</th>
                  <th className="p-3">Model Score</th>
                  <th className="p-3">Surface Spread</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {priorities.map((item) => (
                  <tr key={item.water_body_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="p-3 font-bold text-slate-200">#{item.rank}</td>
                    <td className="p-3">
                      <div className="font-bold text-slate-100">{item.name}</div>
                      <div className="font-mono text-[10px] text-cyan-400">{item.water_body_id}</div>
                    </td>
                    <td className="p-3 text-slate-400">{item.district}, {item.state}</td>
                    <td className="p-3"><HealthIndicator healthClass={item.health_class} /></td>
                    <td className="p-3"><PriorityBadge priority={item.priority} /></td>
                    <td className="p-3 font-mono font-semibold text-slate-200">{item.probability ? item.probability.toFixed(4) : 'N/A'}</td>
                    <td className="p-3 font-semibold text-slate-200">{formatAreaHa(item.latest_area_ha)}</td>
                    <td className="p-3 text-right">
                      <Link
                        href={`/water-bodies/${item.water_body_id}`}
                        className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/30 text-xs font-semibold transition-colors border border-cyan-500/40"
                      >
                        <span>Inspect</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
