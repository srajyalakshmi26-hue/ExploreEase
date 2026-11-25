export const Status = ({ loading, error, empty }) => {
  if (loading) return <p className="state">Loading...</p>;
  if (error) return <p className="state error">{error}</p>;
  if (empty) return <p className="state">Nothing found.</p>;
  return null;
};

export const Pager = ({ total, offset, limit, onChange }) => {
  if (!total || total <= limit) return null;
  return (
    <div className="pager">
      <button className="btn small ghost" disabled={offset === 0} onClick={() => onChange(Math.max(0, offset - limit))}>Previous</button>
      <span>{offset + 1}–{Math.min(offset + limit, total)} of {total}</span>
      <button className="btn small ghost" disabled={offset + limit >= total} onClick={() => onChange(offset + limit)}>Next</button>
    </div>
  );
};

export const nice = (s) => (s ? String(s).replace(/_/g, " ") : "");
