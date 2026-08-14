'use client';

import React from 'react';
import { getHealthBadgeClass } from '@/utils/formatters';

export default function HealthIndicator({ healthClass }) {
  const badgeClass = getHealthBadgeClass(healthClass);
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wide uppercase ${badgeClass}`}>
      {healthClass || 'MODERATE'}
    </span>
  );
}
