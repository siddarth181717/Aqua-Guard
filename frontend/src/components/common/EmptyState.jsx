'use client';

import React from 'react';
import { Database } from 'lucide-react';

export default function EmptyState({ title = 'No Data Available', message = 'No observation or feature records match your search criteria.' }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center rounded-xl border border-slate-700/50 bg-slate-800/30">
      <Database className="w-10 h-10 text-slate-500 mb-3" />
      <h4 className="text-base font-semibold text-slate-200">{title}</h4>
      <p className="text-xs text-slate-400 mt-1 max-w-sm">{message}</p>
    </div>
  );
}
