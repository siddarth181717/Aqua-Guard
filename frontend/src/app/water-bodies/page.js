'use client';

import React, { useEffect, useState } from 'react';
import { Search, Filter, RefreshCw } from 'lucide-react';
import WaterBodyCard from '@/components/waterbody/WaterBodyCard';
import Loading from '@/components/common/Loading';
import ErrorMessage from '@/components/common/ErrorMessage';
import EmptyState from '@/components/common/EmptyState';
import apiService from '@/services/api';

export default function WaterBodiesPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [waterBodies, setWaterBodies] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [stateFilter, setStateFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');

  const fetchWaterBodies = async () => {
    setLoading(true);
    setError(null);
    try {
      const [wbRes, priorityRes] = await Promise.all([
        apiService.getWaterBodies({ page: 1, page_size: 50, state: stateFilter }),
        apiService.getPriorities()
      ]);

      const items = wbRes?.data?.items || [];
      const priorityItems = priorityRes?.data || [];

      const priorityMap = {};
      priorityItems.forEach(p => { priorityMap[p.water_body_id] = p.priority; });

      const merged = items.map(wb => ({
        ...wb,
        priority: priorityMap[wb.water_body_id] || 'LOW'
      }));

      setWaterBodies(merged);
    } catch (err) {
      console.error('Failed loading water bodies:', err);
      setError(err.message || 'Unable to fetch water bodies from backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWaterBodies();
  }, [stateFilter]);

  const filteredWaterBodies = waterBodies.filter(wb => {
    const matchesSearch =
      wb.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      wb.water_body_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      wb.district.toLowerCase().includes(searchTerm.toLowerCase()) ||
      wb.state.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesPriority = priorityFilter ? wb.priority === priorityFilter : true;
    return matchesSearch && matchesPriority;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight">Water Bodies Directory</h1>
          <p className="text-xs text-slate-400 mt-1">Search, filter, and inspect monitored water bodies across India.</p>
        </div>

        <button
          onClick={fetchWaterBodies}
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-cyan-300 transition-colors border border-slate-700/60 shrink-0"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* Search & Filter Bar */}
      <div className="p-4 rounded-xl border border-slate-800 bg-navy-800/80 shadow-lg flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search by water body name, ID, district, or state..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg bg-slate-900/80 border border-slate-700/60 text-slate-100 placeholder-slate-500 text-xs focus:outline-none focus:border-cyan-500/60"
          />
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 text-xs text-slate-400 shrink-0">
            <Filter className="w-4 h-4 text-cyan-400" />
            <span>Priority:</span>
          </div>
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-900/80 border border-slate-700/60 text-slate-200 text-xs focus:outline-none focus:border-cyan-500/60"
          >
            <option value="">All Priorities</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>
        </div>
      </div>

      {loading ? (
        <Loading message="Fetching water bodies from AquaGuard FastAPI backend..." />
      ) : error ? (
        <ErrorMessage message={error} onRetry={fetchWaterBodies} />
      ) : filteredWaterBodies.length === 0 ? (
        <EmptyState title="No Water Bodies Found" message="Try clearing your search term or adjusting filters." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredWaterBodies.map(wb => (
            <WaterBodyCard key={wb.water_body_id} waterBody={wb} />
          ))}
        </div>
      )}
    </div>
  );
}
