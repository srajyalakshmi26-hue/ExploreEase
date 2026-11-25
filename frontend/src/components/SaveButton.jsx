import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { useApp } from "../context.jsx";

export function useSavePlace() {
  const { user } = useApp();
  const nav = useNavigate();
  return async (p) => {
    if (!user) { nav("/login"); return "login"; }
    try {
      await api.savePlace({
        place_name: p.Place_Name, city: p.City, category: p.Category || null,
        latitude: Number.isFinite(Number(p.Latitude)) ? Number(p.Latitude) : null,
        longitude: Number.isFinite(Number(p.Longitude)) ? Number(p.Longitude) : null,
        osm_id: p.OSM_ID || null,
      });
      return "saved";
    } catch (e) { return e.message; }
  };
}

export default function SaveButton({ place }) {
  const save = useSavePlace();
  const [msg, setMsg] = useState("");
  return (
    <span>
      <button className="btn small ghost" onClick={async () => setMsg(await save(place))}>Save</button>
      {msg && <small className="hint"> {msg === "saved" ? "Saved!" : msg}</small>}
    </span>
  );
}
