"use client";

const SUGGESTIONS = [
  { label: "--visualize-trends", fill: "Show me the sales trend over time" },
  { label: "--audit-anomalies", fill: "Are there any anomalies in the sales data?" },
  { label: "--export-csv", fill: "Export the current results as CSV" },
  { label: "--switch-mode sql", fill: "" },
];

export default function CommandChips({
  onSelect,
}: {
  onSelect: (fillText: string) => void;
}) {
  return (
    <div className="mt-3 flex flex-wrap gap-2">
      {SUGGESTIONS.map((s) => (
        <button
          key={s.label}
          type="button"
          onClick={() => onSelect(s.fill)}
          className="rounded-full border border-white/10 bg-surface-container px-3 py-1 font-mono text-label-caps text-outline transition hover:border-cyan/40 hover:text-cyan"
        >
          {s.label}
        </button>
      ))}
    </div>
  );
}
