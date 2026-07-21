"use client";

import dynamic from "next/dynamic";
import type { PlotlyChartData } from "@/lib/api";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

function highlightPeakBar(chart: PlotlyChartData): PlotlyChartData {
  const data = chart.data.map((trace: Record<string, unknown>) => {
    if (trace.type !== "bar" || !Array.isArray(trace.y)) return trace;
    const yValues = trace.y as number[];
    const maxIdx = yValues.indexOf(Math.max(...yValues));
    const baseColors = Array.isArray(
      (trace.marker as Record<string, unknown> | undefined)?.color
    )
      ? ((trace.marker as Record<string, unknown>).color as string[])
      : yValues.map(() => "#2a2a2a");
    const colors = baseColors.map((c: string, i: number) =>
      i === maxIdx ? "#00F5FF" : "#3a3939"
    );
    return {
      ...trace,
      marker: { ...(trace.marker as Record<string, unknown>), color: colors },
    };
  });
  return { ...chart, data };
}

export default function ChartPanel({
  chart,
  caption,
}: {
  chart: PlotlyChartData;
  caption?: string;
}) {
  const styledChart = highlightPeakBar(chart);

  return (
    <div className="glass-panel-active mt-3 overflow-hidden">
      <div className="flex items-center justify-end gap-2 border-b border-white/5 px-3 py-2">
        <button
          type="button"
          aria-label="Expand chart"
          className="text-outline transition hover:text-cyan"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path
              d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
        <button
          type="button"
          aria-label="Download chart"
          className="text-outline transition hover:text-cyan"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 4v12m0 0l-4-4m4 4l4-4M4 20h16"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>

      <div className="p-3">
        <Plot
          data={styledChart.data as Record<string, unknown>[]}
          layout={{
            ...(styledChart.layout as Record<string, unknown>),
            autosize: true,
            font: { family: "Geist, sans-serif", color: "#e5e2e1", size: 12 },
            plot_bgcolor: "rgba(0,0,0,0)",
            paper_bgcolor: "rgba(0,0,0,0)",
            margin: { l: 40, r: 20, t: 30, b: 40 },
          }}
          config={{ displayModeBar: false, responsive: true }}
          style={{ width: "100%", height: "300px" }}
          useResizeHandler
        />
      </div>

      {caption && (
        <div className="border-t border-white/5 px-3 py-2 font-mono text-terminal-log uppercase tracking-wide text-outline">
          {caption}
        </div>
      )}
    </div>
  );
}
