import { nice } from "./Common.jsx";

export default function InterestPicker({ options, value, onChange }) {
  const toggle = (c) => onChange(value.includes(c) ? value.filter((x) => x !== c) : [...value, c]);
  return (
    <div className="chips">
      {options.map((c) => (
        <button type="button" key={c} className={`chip ${value.includes(c) ? "on" : ""}`} onClick={() => toggle(c)}>{nice(c)}</button>
      ))}
    </div>
  );
}
