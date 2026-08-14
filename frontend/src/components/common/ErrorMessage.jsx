'use client';

import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export default function ErrorMessage({ message = 'Unable to connect to AquaGuard backend.', onRetry }) {
  return (
    <div className="p-6 rounded-xl border border-red-500/30 bg-red-500/10 text-red-300 flex items-center justify-between shadow-lg">
      <div className="flex items-center space-x-3">
        <AlertTriangle className="w-6 h-6 text-red-400 shrink-0" />
        <div>
          <h4 className="text-sm font-semibold text-red-200">API Connection Notice</h4>
          <p className="text-xs text-red-300/80 mt-0.5">{message}</p>
        </div>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-200 transition-colors border border-red-500/40"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry</span>
        </button>
      )}
    </div>
  );
}
