'use client';

import React from 'react';
import { getPriorityBadgeClass } from '@/utils/formatters';

export default function PriorityBadge({ priority }) {
  const badgeClass = getPriorityBadgeClass(priority);
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wide uppercase ${badgeClass}`}>
      {priority || 'UNKNOWN'}
    </span>
  );
}
