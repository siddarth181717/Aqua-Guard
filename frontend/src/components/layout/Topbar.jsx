'use client';

import React from 'react';

export default function Topbar() {
  return (
    <header className="h-16 bg-navy-800/80 backdrop-blur-md border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-30">
      <div>
        <h2 className="text-sm font-semibold text-slate-200">AquaGuard Geospatial Command</h2>
        <p className="text-xs text-slate-400">AI-Driven Water Body Surveillance & Restoration Intelligence</p>
      </div>

      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 text-xs text-slate-400 bg-slate-800/60 px-3 py-1.5 rounded-lg border border-slate-700/50">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
          <span>FastAPI Backend Connected</span>
        </div>
      </div>
    </header>
  );
}
