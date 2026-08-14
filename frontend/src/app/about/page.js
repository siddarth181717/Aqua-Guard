'use client';

import React from 'react';
import { ShieldCheck, Database, Layers, Brain, CheckCircle2 } from 'lucide-react';

export default function AboutPage() {
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight">About AquaGuard Intelligence</h1>
        <p className="text-xs text-slate-400 mt-1">AI-driven geospatial surveillance for water body restoration and environmental protection.</p>
      </div>

      <div className="p-6 rounded-xl border border-slate-800 bg-navy-800/80 shadow-xl space-y-4">
        <div className="flex items-center space-x-3 text-cyan-400">
          <ShieldCheck className="w-6 h-6" />
          <h2 className="text-lg font-bold text-slate-100">Project Mission & Objectives</h2>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          AquaGuard provides transparent, scalable, end-to-end geospatial surveillance for monitoring lakes, reservoirs, ponds, and river basins. By integrating high-resolution optical satellite imagery (Sentinel-2, Landsat), official Indian geospatial datasets (ISRO Bhuvan, Ministry of Jal Shakti India-WRIS), and daily rainfall context (ERA5 / CHIRPS), AquaGuard quantifies surface water shrinkage, vegetation encroachment, and water quality degradation.
        </p>
      </div>

      {/* Pipeline Architecture Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-5 rounded-xl border border-slate-800 bg-navy-800/60 shadow-lg space-y-2">
          <div className="flex items-center space-x-2 text-cyan-400 font-semibold text-sm">
            <Layers className="w-4 h-4" />
            <span>1. Geospatial Processing Layer</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Preserves standard spatial references (EPSG:4326), clips Sentinel-2 (10m) and Landsat (30m) optical bands to water body boundaries, applies cloud/cloud-shadow masks (SCL / QA_PIXEL), and computes geodesic area (m², ha).
          </p>
        </div>

        <div className="p-5 rounded-xl border border-slate-800 bg-navy-800/60 shadow-lg space-y-2">
          <div className="flex items-center space-x-2 text-emerald-400 font-semibold text-sm">
            <Database className="w-4 h-4" />
            <span>2. Spectral Indices & Water Mask</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Extracts MNDWI ((Green - SWIR) / (Green + SWIR)), NDWI ((Green - NIR) / (Green + NIR)), and NDVI ((NIR - Red) / (NIR + Red)) to classify open water pixels and measure surrounding weed/algal encroachment.
          </p>
        </div>

        <div className="p-5 rounded-xl border border-slate-800 bg-navy-800/60 shadow-lg space-y-2">
          <div className="flex items-center space-x-2 text-amber-400 font-semibold text-sm">
            <Brain className="w-4 h-4" />
            <span>3. AI/ML Restoration Model</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Uses candidate classifiers (Random Forest, Gradient Boosting, Logistic Regression) trained with temporal splits to prevent data leakage, alongside a transparent rule-based baseline priority scorer.
          </p>
        </div>

        <div className="p-5 rounded-xl border border-slate-800 bg-navy-800/60 shadow-lg space-y-2">
          <div className="flex items-center space-x-2 text-indigo-400 font-semibold text-sm">
            <CheckCircle2 className="w-4 h-4" />
            <span>4. Production FastAPI & PostGIS</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Exposes REST APIs backed by PostgreSQL + PostGIS spatial functions (ST_DWithin, ST_Distance) for frontend maps, historical trends, and priority rankings.
          </p>
        </div>
      </div>
    </div>
  );
}
