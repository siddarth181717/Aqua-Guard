'use client';

import React, { useEffect, useState } from 'react';
import { BarChart3, Filter, ShieldCheck, Waves } from 'lucide-react';
import StatCard from '@/components/common/StatCard';
import Loading from '@/components/common/Loading';
import ErrorMessage from '@/components/common/ErrorMessage';
import apiService from '@/services/api';
import { formatAreaHa } from '@/utils/formatters';

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [waterBodies, setWaterBodies] = useState([]);
  const [priorities, setPriorities] = useState([]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [wbRes, priorityRes] = await Promise.all([
        apiService.getWaterBodies({ page: 1, page_size: 50 }),
        apiService.getPriorities()
      ]);
      setWaterBodies(wbRes?.data?.items || []);
      setPriorities(priorityRes?.data || []);
    } catch (err) {
      console.error('Failed loading analytics:', err);
      setError(err.message || 'Unable to fetch analytics from backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const totalCount = waterBodies.length || 1;
  const criticalCount = priorities.filter(p => p.priority === 'CRITICAL').length;
  const highCount = priorities.filter(p => p.priority === 'HIGH').length;
  const moderateCount = priorities.filter(p => p.priority === 'MEDIUM' || p.priority === 'MODERATE').length;
  const goodCount = priorities.filter(p => p.priority === 'LOW' || p.priority === 'GOOD').length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight">Geospatial Analytics & Regional Trends</h1>
        <p className="text-xs text-slate-400 mt-1">Aggregated statistics, index distributions, and restoration health breakdowns.</p>
      </div>

      {loading ? (
        <Loading message="Processing regional geospatial analytics..." />
      ) : error ? (
        <ErrorMessage message={error} onRetry={fetchData} />
      ) : (
        <>
          {/* Priority Distribution Bar */}
          <div className="p-6 rounded-xl border border-slate-800 bg-navy-800/80 shadow-xl space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">Restoration Priority Distribution Across Monitored Water Bodies</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-center">
                <span className="text-2xl font-bold text-red-400">{criticalCount}</span>
                <span className="text-xs text-slate-300 block font-medium mt-1">CRITICAL Priority</span>
              </div>
              <div className="p-4 rounded-xl border border-orange-500/30 bg-orange-500/10 text-center">
                <span className="text-2xl font-bold text-orange-400">{highCount}</span>
                <span className="text-xs text-slate-300 block font-medium mt-1">HIGH Priority</span>
              </div>
              <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-500/10 text-center">
                <span className="text-2xl font-bold text-amber-400">{moderateCount}</span>
                <span className="text-xs text-slate-300 block font-medium mt-1">MEDIUM Priority</span>
              </div>
              <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-center">
                <span className="text-2xl font-bold text-emerald-400">{goodCount}</span>
                <span className="text-xs text-slate-300 block font-medium mt-1">LOW / GOOD Priority</span>
              </div>
            </div>
          </div>

          {/* Regional Summary Table */}
          <div className="p-6 rounded-xl border border-slate-800 bg-navy-800/60 shadow-xl space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">Monitored Water Bodies Summary</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                  <tr>
                    <th className="p-3">ID</th>
                    <th className="p-3">Water Body</th>
                    <th className="p-3">District / State</th>
                    <th className="p-3">Area (ha)</th>
                    <th className="p-3">Source</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {waterBodies.map(wb => (
                    <tr key={wb.water_body_id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="p-3 font-mono text-cyan-400">{wb.water_body_id}</td>
                      <td className="p-3 font-bold text-slate-100">{wb.name}</td>
                      <td className="p-3 text-slate-400">{wb.district}, {wb.state}</td>
                      <td className="p-3 text-slate-200 font-semibold">{formatAreaHa(wb.area_hectares)}</td>
                      <td className="p-3 text-slate-400">{wb.source || 'Sentinel-2 GEE'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
