import { useEffect, useState } from "react";
import { api } from "../api";
import { useApp } from "../context.jsx";
import MapView from "../components/MapView.jsx";
import { Status, Pager, nice } from "../components/Common.jsx";

const LIMIT = 20;

export default function Restaurants() {
  const { city } = useApp();
  const [search, setSearch] = useState("");
  const [cuisine, setCuisine] = useState("");
  const [q, setQ] = useState({ search: "", cuisine: "" });
  const [offset, setOffset] = useState(0);
  const [data, setData] = useState({ total: 0, items: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => { setOffset(0); }, [city, q]);
  useEffect(() => {
    if (!city) return;
    setLoading(true); setError("");
    api.restaurants({ city, search: q.search, cuisine: q.cuisine, limit: LIMIT, offset })
      .then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [city, q, offset]);

  return (
    <>
      <h1>Restaurants in {city}</h1>
      <form className="filters" onSubmit={(e) => { e.preventDefault(); setQ({ search, cuisine }); }}>
        <input placeholder="Restaurant name" value={search} onChange={(e) => setSearch(e.target.value)} />
        <input placeholder="Cuisine (e.g. indian)" value={cuisine} onChange={(e) => setCuisine(e.target.value)} />
        <button className="btn">Search</button>
      </form>
      <Status loading={loading} error={error} empty={!loading && !error && data.items.length === 0} />
      <div className="split">
        <div className="list">
          {data.items.map((r, i) => (
            <div className="card" key={r.OSM_ID || i}>
              <h3>{r.Restaurant_Name}</h3>
              <span className="tag">{nice(r.Category)}</span>{" "}
              {r.Cuisine && <span className="tag alt">{nice(r.Cuisine)}</span>}
            </div>
          ))}
          <Pager total={data.total} offset={offset} limit={LIMIT} onChange={setOffset} />
        </div>
        <MapView markers={data.items.map((r) => ({ lat: r.Latitude, lng: r.Longitude, title: r.Restaurant_Name, subtitle: nice(r.Cuisine || r.Category) }))} />
      </div>
    </>
  );
}
