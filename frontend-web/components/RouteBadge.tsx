import type { Route } from "@/lib/api";

export default function RouteBadge({
  route,
  extra,
}: {
  route: Route;
  extra?: string;
}) {
  return (
    <div className="flex flex-wrap items-center gap-2 font-mono text-label-caps uppercase text-outline">
      <span className="rounded bg-surface-container-high px-2 py-1 text-primary">
        [route: {route}]
      </span>
      {extra && (
        <span className="rounded bg-surface-container-high px-2 py-1">
          {extra}
        </span>
      )}
    </div>
  );
}
