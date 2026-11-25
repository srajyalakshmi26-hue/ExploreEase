import { Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import { useApp } from "./context.jsx";
import Home from "./pages/Home.jsx";
import Places from "./pages/Places.jsx";
import Restaurants from "./pages/Restaurants.jsx";
import Food from "./pages/Food.jsx";
import Recommendations from "./pages/Recommendations.jsx";
import TripPlanner from "./pages/TripPlanner.jsx";
import Reviews from "./pages/Reviews.jsx";
import Saved from "./pages/Saved.jsx";
import { Login, Register } from "./pages/Auth.jsx";

function Protected({ children }) {
  const { user, ready } = useApp();
  if (!ready) return <p className="state">Loading...</p>;
  return user ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <>
      <Navbar />
      <main className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/places" element={<Places />} />
          <Route path="/restaurants" element={<Restaurants />} />
          <Route path="/food" element={<Food />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/trip-planner" element={<TripPlanner />} />
          <Route path="/reviews" element={<Reviews />} />
          <Route path="/saved" element={<Protected><Saved /></Protected>} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <footer className="footer">Map data © OpenStreetMap contributors (ODbL). ExploreEase – Explore More, Travel Smarter.</footer>
    </>
  );
}
