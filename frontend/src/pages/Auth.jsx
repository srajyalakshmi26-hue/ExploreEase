import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useApp } from "../context.jsx";

function AuthForm({ mode }) {
  const { login, register } = useApp();
  const nav = useNavigate();
  const [f, setF] = useState({ full_name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const isReg = mode === "register";
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError(""); setBusy(true);
    try {
      if (isReg) await register(f);
      else await login({ email: f.email, password: f.password });
      nav("/places");
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  };

  return (
    <form className="panel auth" onSubmit={submit}>
      <h1>{isReg ? "Create account" : "Login"}</h1>
      {isReg && <label>Full name<input value={f.full_name} onChange={set("full_name")} minLength="2" required /></label>}
      <label>Email<input type="email" value={f.email} onChange={set("email")} required /></label>
      <label>Password<input type="password" value={f.password} onChange={set("password")} minLength={isReg ? 8 : 1} required /></label>
      {isReg && <small className="hint">Password must be at least 8 characters.</small>}
      {error && <p className="state error">{error}</p>}
      <button className="btn" disabled={busy}>{busy ? "Please wait..." : isReg ? "Register" : "Login"}</button>
      <p className="hint">{isReg ? <>Already have an account? <Link to="/login">Login</Link></> : <>New here? <Link to="/register">Create an account</Link></>}</p>
    </form>
  );
}

export const Login = () => <AuthForm mode="login" />;
export const Register = () => <AuthForm mode="register" />;
