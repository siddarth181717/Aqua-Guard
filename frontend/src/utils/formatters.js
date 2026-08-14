/**
 * AquaGuard Utility Formatters
 */

export function formatAreaHa(ha) {
  if (ha === null || ha === undefined || isNaN(ha)) return 'N/A';
  return `${Number(ha).toLocaleString('en-IN', { maximumFractionDigits: 2 })} ha`;
}

export function formatAreaM2(m2) {
  if (m2 === null || m2 === undefined || isNaN(m2)) return 'N/A';
  return `${Number(m2).toLocaleString('en-IN', { maximumFractionDigits: 0 })} m²`;
}

export function formatDate(dateStr) {
  if (!dateStr || dateStr === 'UNAVAILABLE') return 'Unavailable';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  } catch (err) {
    return dateStr;
  }
}

export function formatIndex(val) {
  if (val === null || val === undefined || isNaN(val)) return 'N/A';
  return Number(val).toFixed(4);
}

export function getPriorityBadgeClass(priority) {
  switch (String(priority).toUpperCase()) {
    case 'CRITICAL':
      return 'bg-red-500/20 text-red-400 border border-red-500/30';
    case 'HIGH':
      return 'bg-orange-500/20 text-orange-400 border border-orange-500/30';
    case 'MEDIUM':
    case 'MODERATE':
      return 'bg-amber-500/20 text-amber-400 border border-amber-500/30';
    case 'LOW':
    case 'GOOD':
      return 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
    default:
      return 'bg-slate-500/20 text-slate-400 border border-slate-500/30';
  }
}

export function getHealthBadgeClass(healthClass) {
  switch (String(healthClass).toUpperCase()) {
    case 'CRITICAL':
    case 'CRITICAL_RISK':
      return 'bg-red-500/20 text-red-400 border border-red-500/30';
    case 'HIGH':
    case 'HIGH_RISK':
      return 'bg-orange-500/20 text-orange-400 border border-orange-500/30';
    case 'MEDIUM':
    case 'MEDIUM_RISK':
    case 'MODERATE':
      return 'bg-amber-500/20 text-amber-400 border border-amber-500/30';
    case 'LOW':
    case 'LOW_RISK':
    case 'GOOD':
      return 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
    default:
      return 'bg-slate-500/20 text-slate-400 border border-slate-500/30';
  }
}
