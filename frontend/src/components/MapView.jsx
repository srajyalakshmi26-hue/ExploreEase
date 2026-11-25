import { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from "react-leaflet";
import L from "leaflet";
import icon from "leaflet/dist/images/marker-icon.png";
import icon2x from "leaflet/dist/images/marker-icon-2x.png";
import shadow from "leaflet/dist/images/marker-shadow.png";

L.Icon.Default.mergeOptions({ iconUrl: icon, iconRetinaUrl: icon2x, shadowUrl: shadow });

function Fit({ points }) {
  const map = useMap();
  useEffect(() => {
    if (points.length === 1) map.setView(points[0], 14);
    else if (points.length > 1) map.fitBounds(points, { padding: [30, 30] });
  }, [points, map]);
  return null;
}

// markers: [{ lat, lng, title, subtitle, action? }]
export default function MapView({ markers = [], line = false, height = 420 }) {
  const valid = markers
    .map((m) => ({ ...m, lat: Number(m.lat), lng: Number(m.lng) }))
    .filter((m) => Number.isFinite(m.lat) && Number.isFinite(m.lng));
  const points = valid.map((m) => [m.lat, m.lng]);
  return (
    <div className="map" style={{ height }}>
      <MapContainer center={points[0] || [20.59, 78.96]} zoom={points.length ? 12 : 5} style={{ height: "100%", width: "100%" }}>
        <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <Fit points={points} />
        {line && points.length > 1 && <Polyline positions={points} />}
        {valid.map((m, i) => (
          <Marker key={i} position={[m.lat, m.lng]}>
            <Popup>
              <strong>{m.title}</strong>
              {m.subtitle && <div>{m.subtitle}</div>}
              {m.action && <button className="btn small" onClick={m.action.onClick}>{m.action.label}</button>}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
