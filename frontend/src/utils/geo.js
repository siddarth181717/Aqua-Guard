/**
 * AquaGuard Geospatial & Map Helpers
 */

export function getPriorityColor(priority) {
  switch (String(priority).toUpperCase()) {
    case 'CRITICAL':
      return '#EF4444'; // Red
    case 'HIGH':
      return '#F97316'; // Orange
    case 'MEDIUM':
    case 'MODERATE':
      return '#F59E0B'; // Amber/Yellow
    case 'LOW':
    case 'GOOD':
      return '#10B981'; // Green
    default:
      return '#06B6D4'; // Aqua/Cyan default
  }
}

export function extractCoordinatesFromGeoJSON(geojson) {
  if (!geojson) return null;
  try {
    const geom = geojson.geometry || geojson;
    if (geom.type === 'Polygon' && geom.coordinates && geom.coordinates[0]) {
      return geom.coordinates[0].map(([lon, lat]) => [lat, lon]);
    }
    if (geom.type === 'MultiPolygon' && geom.coordinates) {
      return geom.coordinates.map(poly => poly[0].map(([lon, lat]) => [lat, lon]));
    }
  } catch (err) {
    console.error('GeoJSON parsing error:', err);
  }
  return null;
}
