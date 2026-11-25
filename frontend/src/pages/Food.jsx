import { useEffect, useState } from "react";
import { api } from "../api";
import { useApp } from "../context.jsx";
import { Status } from "../components/Common.jsx";

export default function Food() {
  const { city } = useApp();
  const [data, setData] = useState({ items: [], note: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!city) return;
    setLoading(true); setError("");
    api.food(city).then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [city]);

  return (
    <>
      <h1>Local Food in {city}</h1>
      {data.note && <p className="hint">{data.note}</p>}
      <Status loading={loading} error={error} empty={!loading && !error && data.items.length === 0} />
      <div className="grid">
        {data.items.map((f, i) => {
          const hasPrice = f.Approx_Price !== null && f.Approx_Price !== undefined && f.Approx_Price !== "";
          return (
            <div className="card" key={i}>
              <h3>{f.Food_Name}</h3>
              <p>{f.Description}</p>
              <span className="tag alt">{hasPrice ? `${f.Currency || ""} ${f.Approx_Price}` : "Price not verified"}</span>
              {f.Restaurant_Name && <p className="hint">Available at: {f.Restaurant_Name}</p>}
            </div>
          );
        })}
      </div>
    </>
  );
}
