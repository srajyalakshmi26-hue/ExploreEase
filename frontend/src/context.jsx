import { createContext, useContext, useEffect, useState } from "react";
import { api, getToken, setToken } from "./api";

const Ctx = createContext(null);
export const useApp = () => useContext(Ctx);

export function AppProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);
  const [city, setCityState] = useState(localStorage.getItem("ee_city") || "");
  const [cities, setCities] = useState([]);

  const setCity = (c) => {
    setCityState(c);
    localStorage.setItem("ee_city", c);
  };

  useEffect(() => {
    api.cities().then((d) => {
      setCities(d.cities || []);
      if (!localStorage.getItem("ee_city") && d.cities?.length) setCity(d.cities[0]);
    }).catch(() => {});
    if (getToken()) {
      api.me().then(setUser).catch(() => setToken(null)).finally(() => setReady(true));
    } else setReady(true);
  }, []);

  const authenticate = async (fn, body) => {
    const res = await fn(body);
    setToken(res.access_token);
    setUser(res.user);
  };
  const login = (b) => authenticate(api.login, b);
  const register = (b) => authenticate(api.register, b);
  const logout = () => { setToken(null); setUser(null); };

  return <Ctx.Provider value={{ user, ready, city, setCity, cities, login, register, logout }}>{children}</Ctx.Provider>;
}
