import { useEffect, useState } from "react";
import { api } from "../api";
import { useApp } from "../context.jsx";
import MapView from "../components/MapView.jsx";
import SaveButton, { useSavePlace } from "../components/SaveButton.jsx";
import { Status, Pager, nice } from "../components/Common.jsx";

const LIMIT = 20;

export default function Places() {
  const { city } = useApp();
  const savePlace = useSavePlace();
  const [categories, setCategories] = useState([]);
  const [category, setCategory] = useState("");
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("");
  const [offset, setOffset] = useState(0);
  const [data, setData] = useState({ total: 0, items: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => { if (city) api.categories(city).then((d) => setCategories(d.categories)).catch(() => {}); setCategory(""); setOffset(0); }, [city]);
  useEffect(() => { setOffset(0); }, [category, query]);
  useEffect(() => {
    if (!city) return;
    setLoading(true); setError("");
    api.places({ city, category, search: query, limit: LIMIT, offset })
      .then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [city, category, query, offset]);

  return (
    <>
      <h1>Tourist Places in {city}</h1>
      <form className="filters" onSubmit={(e) => { e.preventDefault(); setQuery(search); }}>
        <input placeholder="Search by place name" value={search} onChange={(e) => setSearch(e.target.value)} />
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">All categories</option>
          {categories.map((c) => <option key={c} value={c}>{nice(c)}</option>)}
        </select>
        <button className="btn">Search</button>
      </form>
      <Status loading={loading} error={error} empty={!loading && !error && data.items.length === 0} />
      <div className="split">
        <div className="list">
          {data.items.map((p, i) => (
            <div className="card row" key={p.OSM_ID || i}>
              <div><h3>{p.Place_Name}</h3><span className="tag">{nice(p.Category)}</span></div>
              <SaveButton place={p} />
            </div>
          ))}
          <Pager total={data.total} offset={offset} limit={LIMIT} onChange={setOffset} />
        </div>
        <MapView markers={data.items.map((p) => ({ lat: p.Latitude, lng: p.Longitude, title: p.Place_Name, subtitle: nice(p.Category),
          action: { label: "Save", onClick: () => savePlace(p) } }))} />
      </div>
    </>
  );
}
