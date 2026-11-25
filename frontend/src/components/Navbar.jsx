import { NavLink, Link, useNavigate } from "react-router-dom";
import { useApp } from "../context.jsx";

export default function Navbar() {
  const { user, logout, city, setCity, cities } = useApp();
  const nav = useNavigate();
  return (
    <header className="navbar">
      <Link to="/" className="brand">Explore<span>Ease</span></Link>
      <nav className="links">
        <NavLink to="/places">Places</NavLink>
        <NavLink to="/restaurants">Restaurants</NavLink>
        <NavLink to="/food">Food</NavLink>
        <NavLink to="/recommendations">Recommend</NavLink>
        <NavLink to="/trip-planner">Trip Planner</NavLink>
        <NavLink to="/reviews">Reviews</NavLink>
        {user && <NavLink to="/saved">Saved</NavLink>}
      </nav>
      <div className="nav-right">
        <select value={city} onChange={(e) => setCity(e.target.value)} aria-label="City">
          {cities.length === 0 && <option value="">City</option>}
          {cities.map((c) => <option key={c}>{c}</option>)}
        </select>
        {user ? (
          <>
            <span className="user">Hi, {user.full_name.split(" ")[0]}</span>
            <button className="btn small ghost" onClick={() => { logout(); nav("/"); }}>Logout</button>
          </>
        ) : (
          <Link className="btn small" to="/login">Login</Link>
        )}
      </div>
    </header>
  );
}
