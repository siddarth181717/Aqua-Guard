'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Waves, BarChart3, AlertOctagon, Info, ShieldCheck } from 'lucide-react';

const NAV_ITEMS = [
  { name: 'Overview', href: '/', icon: LayoutDashboard },
  { name: 'Water Bodies', href: '/water-bodies', icon: Waves },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Restoration Priority', href: '/priority', icon: AlertOctagon },
  { name: 'About AquaGuard', href: '/about', icon: Info },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-navy-800 border-r border-slate-800 flex flex-col justify-between shrink-0 h-screen sticky top-0">
      <div>
        {/* Brand Header */}
        <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-100 tracking-tight">AquaGuard</h1>
            <p className="text-[10px] uppercase tracking-wider font-semibold text-cyan-400">Geospatial Surveillance</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-4 space-y-1.5">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 shadow-md'
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800 text-[11px] text-slate-400 space-y-1">
        <div className="flex items-center justify-between">
          <span>Pipeline Status</span>
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            ONLINE
          </span>
        </div>
        <p className="text-slate-400/80">AquaGuard Intelligence v1.0.0</p>
      </div>
    </aside>
  );
}
