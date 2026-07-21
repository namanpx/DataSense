"use client";

const TABS = ["TERMINAL", "ARCHIVE", "SOURCES", "SYSTEM"] as const;
type Tab = (typeof TABS)[number];

export default function Header({
  activeTab,
  onTabChange,
}: {
  activeTab: Tab;
  onTabChange: (tab: Tab) => void;
}) {
  return (
    <header className="glass-panel mb-4 flex items-center justify-between px-5 py-3">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-cyan/10 text-cyan">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path
              d="M4 18L9 11L13 15L20 6"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <circle cx="20" cy="6" r="2" fill="currentColor" />
          </svg>
        </div>
        <span className="font-sans text-lg font-bold text-on-surface">
          DataSense v1.0
        </span>
      </div>

      <nav className="hidden gap-6 md:flex">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => onTabChange(tab)}
            className={`font-mono text-label-caps uppercase transition-colors ${
              tab === activeTab
                ? "text-cyan"
                : "text-outline hover:text-on-surface-variant"
            }`}
          >
            {tab}
          </button>
        ))}
      </nav>

      <div className="flex items-center gap-2">
        <span className="font-mono text-label-caps uppercase text-outline">
          operator
        </span>
        <span className="inline-block h-2 w-2 rounded-full status-dot-active animate-pulse-cyan" />
      </div>
    </header>
  );
}

export { TABS };
export type { Tab };
