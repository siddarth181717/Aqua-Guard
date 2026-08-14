'use client';

import React from 'react';

export default function PageContainer({ children, className = '' }) {
  return (
    <div className={`p-6 max-w-7xl mx-auto space-y-6 ${className}`}>
      {children}
    </div>
  );
}
