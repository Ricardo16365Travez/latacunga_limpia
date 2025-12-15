import L from 'leaflet';

export type PuntoRuta = { lat: number; lon: number };

export const dibujarRutaRoja = (map: L.Map, puntos: PuntoRuta[]) => {
  if (!puntos || puntos.length < 2) return null;
  const latlngs = puntos.map(p => L.latLng(p.lat, p.lon));
  const polyline = L.polyline(latlngs, { color: 'red', weight: 4 });
  polyline.addTo(map);
  map.fitBounds(polyline.getBounds(), { padding: [20, 20] });
  return polyline;
};

// Si el backend devuelve `polyline` codificado, se podría decodificar con @mapbox/polyline.
// Para evitar agregar dependencias ahora, usamos lat/lon de puntos como fallback.
