import { useEffect, useState } from "react";
import { api } from "../api";
import { useApp } from "../context.jsx";
import MapView from "../components/MapView.jsx";
import InterestPicker from "../components/InterestPicker.jsx";
import { Status, nice } from "../components/Common.jsx";

export default function TripPlanner() {
  const { city } = useApp();
  const [categories, setCategories] = useState([]);
  const [f, setF] = useState({ budget: 1500, currency: "INR", days: 1, max_places: 8, interests: [] });
  const [start, setStart] = useState(null);
  const [geoMsg, setGeoMsg] = useState("");
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setPlan(null); setF((x) => ({ ...x, interests: [] }));
    if (city) api.categories(city).then((d) => setCategories(d.categories)).catch(() => {});
  }, [city]);

  const set = (k) => (e) => setF({ ...f, [k]: e.target.type === "number" ? Number(e.target.value) : e.target.value });

  const useLocation = () => {
    if (!navigator.geolocation) return setGeoMsg("Location is not supported by this browser.");
    navigator.geolocation.getCurrentPosition(
      (p) => { setStart({ lat: p.coords.latitude, lng: p.coords.longitude }); setGeoMsg("Using your current location as the start."); },
      () => setGeoMsg("Could not get your location."));
  };

  const submit = (e) => {
    e.preventDefault();
    setLoading(true); setError(""); setPlan(null);
    const body = { city, ...f };
    if (start) { body.start_latitude = start.lat; body.start_longitude = start.lng; }
    api.planTrip(body).then(setPlan).catch((e) => setError(e.message)).finally(() => setLoading(false));
  };

  return (
    <>
      <h1>Trip Planner – {city}</h1>
      <form className="panel" onSubmit={submit}>
        <div className="form-grid">
          <label>Budget<input type="number" min="1" value={f.budget} onChange={set("budget")} required /></label>
          <label>Currency<input maxLength="3" value={f.currency} onChange={set("currency")} /></label>
          <label>Days<input type="number" min="1" max="14" value={f.days} onChange={set("days")} /></label>
          <label>Max places<input type="number" min="1" max="30" value={f.max_places} onChange={set("max_places")} /></label>
        </div>
        <label>Interests (optional)</label>
        <InterestPicker options={categories} value={f.interests} onChange={(v) => setF({ ...f, interests: v })} />
        <div>
          <button type="button" className="btn ghost small" onClick={useLocation}>Use my location as start</button>
          {geoMsg && <small className="hint"> {geoMsg}</small>}
        </div>
        <button className="btn">Generate trip plan</button>
      </form>
      <Status loading={loading} error={error} />
      {plan && (
        <>
          <p className="hint">{plan.cost_note}</p>
          <p className="notice">{plan.budget_status}</p>
          <div className="split">
            <div className="list">
              {plan.itinerary.map((p, i) => (
                <div className="card" key={p.OSM_ID || i}>
                  <h3>{p.Visit_Order ?? i + 1}. {p.Place_Name}</h3>
                  <span className="tag">{nice(p.Category)}</span>
                  <span className="tag alt">
                    {p.Entry_Fee != null ? `Entry: ${p.Entry_Fee_Currency || ""} ${p.Entry_Fee}` : "Entry fee not verified"}
                  </span>
                  {p.Distance_From_Current_KM != null && <p className="hint">{Number(p.Distance_From_Current_KM).toFixed(1)} km from the previous point</p>}
                </div>
              ))}
            </div>
            <MapView line markers={plan.itinerary.map((p, i) => ({ lat: p.Latitude, lng: p.Longitude, title: `${p.Visit_Order ?? i + 1}. ${p.Place_Name}`, subtitle: nice(p.Category) }))} />
          </div>
        </>
      )}
    </>
  );
}
