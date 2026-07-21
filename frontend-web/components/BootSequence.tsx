"use client";

import { useEffect, useState } from "react";

const BOOT_LINES = [
  "INITIALIZING AGENT...",
  "LOADING SCHEMA [v4.2]...",
  "ALLOCATING VECTOR HEAP...",
  "DECRYPTING CORE ASSETS...",
  "CONNECTING TO DATA SOURCE [DUCKDB]...",
  "SYNCHRONIZING SECURE TUNNEL...",
  "OPTIMIZING INFERENCE ENGINE...",
  "SYSTEM READY",
];

export default function BootSequence({ onDone }: { onDone: () => void }) {
  const [visibleLines, setVisibleLines] = useState<number>(0);

  useEffect(() => {
    if (visibleLines >= BOOT_LINES.length) {
      const t = setTimeout(onDone, 350);
      return () => clearTimeout(t);
    }
    const t = setTimeout(() => setVisibleLines((n) => n + 1), 140);
    return () => clearTimeout(t);
  }, [visibleLines, onDone]);

  return (
    <div className="flex h-screen w-full items-center justify-center bg-void">
      <div className="w-full max-w-md px-6 font-mono text-terminal-log text-primary">
        {BOOT_LINES.slice(0, visibleLines).map((line, i) => (
          <div key={i} className="mb-1 opacity-80">
            <span className="text-outline">[{String(i).padStart(2, "0")}]</span>{" "}
            {line}
          </div>
        ))}
        {visibleLines < BOOT_LINES.length && (
          <span className="inline-block h-3 w-2 animate-blink bg-cyan align-middle" />
        )}
      </div>
    </div>
  );
}
