'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Waves, AlertTriangle, ShieldCheck, Activity, ArrowRight } from 'lucide-react';
import StatCard from '@/components/common/StatCard';
import WaterMap from '@/components/map/WaterMap';
import PriorityBadge from '@/components/waterbody/PriorityBadge';
import Loading from '@/components/common/Loading';
import ErrorMessage from '@/components/common/ErrorMessage';
import apiService from '@/services/api';
import { formatAreaHa, formatDate } from '@/utils/formatters';

export default function OverviewPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [waterBodies, setWaterBodies] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [selectedWb, setSelectedWb] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [wbRes, priorityRes] = await Promise.all([
        apiService.getWaterBodies({ page: 1, page_size: 20 }),
        apiService.getPriorities()
      ]);

      const items = wbRes?.data?.items || [];
      const priorityItems = priorityRes?.data || [];

      // Merge priorities into water bodies
      const priorityMap = {};
      priorityItems.forEach(p => { priorityMap[p.water_body_id] = p; });

      const merged = items.map(wb => ({
        ...wb,
        priority: priorityMap[wb.water_body_id]?.priority || 'LOW',
        health_class: priorityMap[wb.water_body_id]?.health_class || 'GOOD'
      }));

      setWaterBodies(merged);
      setPriorities(priorityItems);
      if (merged.length > 0) setSelectedWb(merged[0]);
    } catch (err) {
      console.error('Failed fetching Overview data:', err);
      setError(err.message || 'Unable to connect to AquaGuard backend.');
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
  const totalAreaHa = waterBodies.reduce((acc, wb) => acc + (wb.area_hectares || 0), 0);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="p-6 rounded-2xl border border-cyan-500/30 bg-gradient-to-r from-navy-800 via-navy-800 to-cyan-950/40 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>AquaGuard Environmental Surveillance</span>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-100 mt-2 tracking-tight">Geospatial Water Body Command</h1>
          <p className="text-xs text-slate-400 max-w-2xl mt-1">
            Monitor water bodies, detect environmental degradation, and prioritize restoration using multi-source satellite intelligence.
          </p>
        </div>
        <Link
          href="/priority"
          className="flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl bg-cyan-500 text-slate-950 font-bold text-xs hover:bg-cyan-400 transition-colors shadow-lg shrink-0"
        >
          <span>View Priority Restoration Queue</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {loading ? (
        <Loading message="Loading AquaGuard overview dashboard & satellite layers..." />
      ) : error ? (
        <ErrorMessage message={error} onRetry={fetchData} />
      ) : (
        <>
          {/* Key Statistics Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Monitored Water Bodies"
              value={totalCount}
              subtext="Sentinel-2 & Landsat-9 track"
              icon={Waves}
              color="cyan"
            />
            <StatCard
              title="Critical Priority"
              value={criticalCount}
              subtext="Immediate restoration attention"
              icon={AlertTriangle}
              color="red"
            />
            <StatCard
              title="High Risk Water Bodies"
              value={highCount}
              subtext="Persistent water shrinkage"
              icon={Activity}
              color="amber"
            />
            <StatCard
              title="Total Monitored Spread"
              value={formatAreaHa(totalAreaHa)}
              subtext="Surface water area coverage"
              icon={ShieldCheck}
              color="emerald"
            />
          </div>

          {/* Interactive Map & Selection Panel Split */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-200">Interactive Geospatial Water Map</h3>
                <span className="text-xs text-slate-400">Click a water body polygon to inspect latest observation</span>
              </div>
              <WaterMap
                waterBodies={waterBodies}
                selectedId={selectedWb?.water_body_id}
                onSelectWaterBody={(wb) => setSelectedWb(wb)}
              />
            </div>

            {/* Selected Water Body Inspector Card */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-slate-200">Water Body Inspector</h3>
              {selectedWb ? (
                <div className="p-5 rounded-xl border border-slate-800 bg-navy-800/80 shadow-xl space-y-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest">{selectedWb.water_body_id}</span>
                      <h4 className="text-lg font-bold text-slate-100">{selectedWb.name}</h4>
                      <p className="text-xs text-slate-400 mt-0.5">{selectedWb.district}, {selectedWb.state}</p>
                    </div>
                    <PriorityBadge priority={selectedWb.priority || 'LOW'} />
                  </div>

                  <div className="grid grid-cols-2 gap-3 pt-3 border-t border-slate-800 text-xs">
                    <div className="bg-slate-800/40 p-2.5 rounded-lg">
                      <span className="text-[10px] text-slate-400 uppercase block">Surface Area</span>
                      <span className="font-semibold text-slate-200">{formatAreaHa(selectedWb.area_hectares)}</span>
                    </div>
                    <div className="bg-slate-800/40 p-2.5 rounded-lg">
                      <span className="text-[10px] text-slate-400 uppercase block">Data Source</span>
                      <span className="font-semibold text-slate-200">{selectedWb.source || 'Bhuvan WFS'}</span>
                    </div>
                  </div>

                  <div className="pt-2">
                    <Link
                      href={`/water-bodies/${selectedWb.water_body_id}`}
                      className="w-full flex items-center justify-center space-x-2 py-2.5 rounded-lg bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/30 text-xs font-semibold transition-colors border border-cyan-500/40"
                    >
                      <span>Full Analytics & AI Predictions</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center text-xs text-slate-400 rounded-xl border border-slate-800 bg-navy-800/40">
                  Select a water body on the map to inspect metrics.
                </div>
              )}

              {/* Top Priority Preview */}
              <div className="p-5 rounded-xl border border-slate-800 bg-navy-800/60 shadow-lg space-y-3">
                <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Top Priority Ranking</h4>
                <div className="space-y-2">
                  {priorities.slice(0, 3).map((item) => (
                    <div key={item.water_body_id} className="flex items-center justify-between p-2 rounded-lg bg-slate-800/40 text-xs">
                      <div>
                        <div className="font-medium text-slate-200">{item.name}</div>
                        <div className="text-[10px] text-slate-400">{item.district}</div>
                      </div>
                      <PriorityBadge priority={item.priority} />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
