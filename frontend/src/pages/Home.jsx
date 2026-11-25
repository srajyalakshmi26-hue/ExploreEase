import { useNavigate } from "react-router-dom";
import { useApp } from "../context.jsx";

export default function Home() {
  const { cities, city, setCity } = useApp();
  const nav = useNavigate();
  return (
    <>
      <section className="hero">
        <h1>Explore More, Travel Smarter</h1>
        <p>Discover tourist places and restaurants, get recommendations and plan your trip on an interactive map.</p>
      </section>
      <h2>Choose a city</h2>
      <div className="grid">
        {cities.map((c) => (
          <button key={c} className={`card city ${c === city ? "active" : ""}`} onClick={() => { setCity(c); nav("/places"); }}>
            <h3>{c}</h3>
            <span>Explore places →</span>
          </button>
        ))}
        {cities.length === 0 && <p className="state">No cities loaded. Check that the backend is running.</p>}
      </div>
      <h2>What you can do</h2>
      <div className="grid">
        {[["/places", "Tourist Places", "Search and filter places with map markers."],
          ["/restaurants", "Restaurants", "Find restaurants and cuisines."],
          ["/food", "Local Food", "Famous local dishes of the city."],
          ["/recommendations", "Recommendations", "Places ranked for your interests."],
          ["/trip-planner", "Trip Planner", "Generate an itinerary route."],
          ["/reviews", "Review Analyzer", "Check the sentiment of reviews."]].map(([to, t, d]) => (
          <button key={to} className="card" onClick={() => nav(to)}><h3>{t}</h3><span>{d}</span></button>
        ))}
      </div>
    </>
  );
}
