'use client';

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Polygon, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

import MapLegend from './MapLegend';
import { getPriorityColor, extractCoordinatesFromGeoJSON } from '@/utils/geo';
import { formatAreaHa, formatDate } from '@/utils/formatters';

function MapRecenter({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, zoom || map.getZoom());
    }
  }, [center, zoom, map]);
  return null;
}

export default function WaterMapInner({
  waterBodies = [],
  selectedId = null,
  onSelectWaterBody,
  center = [17.4248, 78.4680],
  zoom = 12
}) {
  return (
    <div className="relative w-full h-[520px] rounded-xl overflow-hidden border border-slate-800 shadow-2xl">
      <MapContainer center={center} zoom={zoom} scrollWheelZoom={true} className="w-full h-full z-10">
        <TileLayer
          attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a>'
          url="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png"
        />
        <MapRecenter center={center} zoom={zoom} />

        {waterBodies.map((wb) => {
          const isSelected = wb.water_body_id === selectedId;
          const coords = extractCoordinatesFromGeoJSON(wb.geometry);
          const color = getPriorityColor(wb.priority || 'LOW');

          if (!coords) return null;

          return (
            <Polygon
              key={wb.water_body_id}
              positions={coords}
              pathOptions={{
                color: isSelected ? '#38BDF8' : color,
                fillColor: color,
                fillOpacity: isSelected ? 0.6 : 0.4,
                weight: isSelected ? 3 : 2,
              }}
              eventHandlers={{
                click: () => onSelectWaterBody && onSelectWaterBody(wb)
              }}
            >
              <Popup className="custom-leaflet-popup">
                <div className="p-2 space-y-1 font-sans text-slate-800 text-xs">
                  <div className="font-bold text-sm text-cyan-900">{wb.name}</div>
                  <div className="text-[11px] text-slate-600">{wb.district}, {wb.state}</div>
                  <div className="pt-1 border-t border-slate-200 mt-1 space-y-0.5">
                    <div><strong>Area:</strong> {formatAreaHa(wb.area_hectares)}</div>
                    <div><strong>Priority:</strong> <span style={{ color }}>{wb.priority || 'LOW'}</span></div>
                    <div><strong>Obs Date:</strong> {formatDate(wb.latest_observation_date || wb.created_at)}</div>
                  </div>
                </div>
              </Popup>
            </Polygon>
          );
        })}
      </MapContainer>

      <div className="absolute bottom-4 right-4 z-20">
        <MapLegend />
      </div>
    </div>
  );
}
