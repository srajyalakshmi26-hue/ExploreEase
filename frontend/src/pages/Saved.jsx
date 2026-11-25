import { useEffect, useState } from "react";
import { api } from "../api";
import MapView from "../components/MapView.jsx";
import { Status, nice } from "../components/Common.jsx";

export default function Saved() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = () => api.savedPlaces().then((d) => setItems(d.items)).catch((e) => setError(e.message)).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const remove = (id) => api.deleteSaved(id).then(() => setItems((x) => x.filter((i) => i.id !== id))).catch((e) => setError(e.message));

  return (
    <>
      <h1>Saved Places</h1>
      <Status loading={loading} error={error} empty={!loading && !error && items.length === 0} />
      <div className="split">
        <div className="list">
          {items.map((p) => (
            <div className="card row" key={p.id}>
              <div><h3>{p.place_name}</h3><span className="tag">{p.city}</span> {p.category && <span className="tag alt">{nice(p.category)}</span>}</div>
              <button className="btn small ghost" onClick={() => remove(p.id)}>Remove</button>
            </div>
          ))}
        </div>
        {items.length > 0 && <MapView markers={items.map((p) => ({ lat: p.latitude, lng: p.longitude, title: p.place_name, subtitle: p.city }))} />}
      </div>
    </>
  );
}
