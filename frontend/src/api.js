const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";
export const getToken = () => localStorage.getItem("ee_token");
export const setToken = (t) => (t ? localStorage.setItem("ee_token", t) : localStorage.removeItem("ee_token"));

function qs(params = {}) {
  const sp = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v === undefined || v === null || v === "") return;
    if (Array.isArray(v)) v.forEach((x) => sp.append(k, x));
    else sp.append(k, v);
  });
  const s = sp.toString();
  return s ? `?${s}` : "";
}

async function request(path, { method = "GET", body, params } = {}) {
  const headers = {};
  if (body) headers["Content-Type"] = "application/json";
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  let res;
  try {
    res = await fetch(`${BASE}${path}${qs(params)}`, { method, headers, body: body ? JSON.stringify(body) : undefined });
  } catch {
    throw new Error("Cannot reach the server. Make sure the backend is running.");
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const d = data.detail;
    const msg = Array.isArray(d) ? d.map((e) => e.msg).join(", ") : d || `Request failed (${res.status})`;
    throw new Error(msg);
  }
  return data;
}

export const api = {
  register: (b) => request("/auth/register", { method: "POST", body: b }),
  login: (b) => request("/auth/login", { method: "POST", body: b }),
  me: () => request("/auth/me"),
  cities: () => request("/meta/cities"),
  places: (p) => request("/places", { params: p }),
  categories: (city) => request("/places/categories", { params: { city } }),
  restaurants: (p) => request("/restaurants", { params: p }),
  recommend: (p) => request("/recommendations/places", { params: p }),
  food: (city) => request("/food", { params: { city } }),
  analyzeReviews: (reviews) => request("/reviews/analyze", { method: "POST", body: { reviews } }),
  planTrip: (b) => request("/trips/plan", { method: "POST", body: b }),
  savePlace: (b) => request("/saved-places", { method: "POST", body: b }),
  savedPlaces: () => request("/saved-places"),
  deleteSaved: (id) => request(`/saved-places/${id}`, { method: "DELETE" }),
};
