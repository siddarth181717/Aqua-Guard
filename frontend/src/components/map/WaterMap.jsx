'use client';

import dynamic from 'next/dynamic';
import React from 'react';
import Loading from '../common/Loading';

const WaterMapInner = dynamic(() => import('./WaterMapInner'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[520px] rounded-xl border border-slate-800 bg-navy-800/80 flex items-center justify-center">
      <Loading message="Loading Leaflet geospatial map engine..." />
    </div>
  )
});

export default function WaterMap(props) {
  return <WaterMapInner {...props} />;
}
