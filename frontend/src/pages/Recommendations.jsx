import { useEffect, useState } from "react";
import { api } from "../api";
import { useApp } from "../context.jsx";
import MapView from "../components/MapView.jsx";
import InterestPicker from "../components/InterestPicker.jsx";
import SaveButton from "../components/SaveButton.jsx";
import { Status, nice } from "../components/Common.jsx";

export default function Recommendations() {
  const { city } = useApp();
  const [categories, setCategories] = useState([]);
  const [interests, setInterests] = useState([]);
  const [limit, setLimit] = useState(10);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setInterests([]); setResult(null);
    if (city) api.categories(city).then((d) => setCategories(d.categories)).catch(() => {});
  }, [city]);

  const submit = (e) => {
    e.preventDefault();
    setLoading(true); setError("");
    api.recommend({ city, interests, limit }).then(setResult).catch((e) => setError(e.message)).finally(() => setLoading(false));
  };

  return (
    <>
      <h1>Recommendations for {city}</h1>
      <form className="panel" onSubmit={submit}>
        <label>Interests (optional)</label>
        <InterestPicker options={categories} value={interests} onChange={setInterests} />
        <label>Number of places
          <input type="number" min="1" max="50" value={limit} onChange={(e) => setLimit(Number(e.target.value))} />
        </label>
        <button className="btn">Get recommendations</button>
      </form>
      <Status loading={loading} error={error} />
      {result?.message && <p className="state">{result.message}</p>}
      {result && result.items?.length > 0 && (
        <div className="split">
          <div className="list">
            {result.items.map((p, i) => (
              <div className="card row" key={p.OSM_ID || i}>
                <div>
                  <h3>{i + 1}. {p.Place_Name}</h3>
                  <span className="tag">{nice(p.Category)}</span>
                  {p.Recommendation_Score != null && <span className="tag alt">Score {Number(p.Recommendation_Score).toFixed(2)}</span>}
                  {p.Recommendation_Reason && <p className="hint">{p.Recommendation_Reason}</p>}
                </div>
                <SaveButton place={p} />
              </div>
            ))}
          </div>
          <MapView markers={result.items.map((p) => ({ lat: p.Latitude, lng: p.Longitude, title: p.Place_Name, subtitle: nice(p.Category) }))} />
        </div>
      )}
    </>
  );
}
