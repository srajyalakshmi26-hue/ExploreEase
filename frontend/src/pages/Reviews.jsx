import { useState } from "react";
import { api } from "../api";
import { Status } from "../components/Common.jsx";

export default function Reviews() {
  const [text, setText] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = (e) => {
    e.preventDefault();
    const reviews = text.split("\n").map((s) => s.trim()).filter(Boolean);
    if (!reviews.length) return setError("Enter at least one review.");
    setLoading(true); setError(""); setData(null);
    api.analyzeReviews(reviews).then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  };

  return (
    <>
      <h1>Review Sentiment Analyzer</h1>
      <form className="panel" onSubmit={submit}>
        <label>Enter one review per line
          <textarea rows="6" value={text} onChange={(e) => setText(e.target.value)} placeholder={"Beautiful place, very clean.\nToo crowded and poorly maintained."} />
        </label>
        <button className="btn">Analyze</button>
      </form>
      <Status loading={loading} error={error} />
      {data && (
        <>
          <p className="hint">{data.notice}</p>
          <div className="list">
            {data.results.map((r, i) => (
              <div className="card row" key={i}>
                <p>{r.review}</p>
                <span className={`tag sent-${r.sentiment}`}>{r.sentiment} ({r.scores.compound.toFixed(2)})</span>
              </div>
            ))}
          </div>
        </>
      )}
    </>
  );
}
