# Wiring these into your real `frontend-web`

1. Copy these files into your existing `frontend-web/` (created by
   `create-next-app`), overwriting `tailwind.config.ts` and `app/globals.css`,
   adding `app/page.tsx`, and creating the `components/` and `lib/` folders.

2. Install the one new dependency this needs:
   ```bash
   npm install react-plotly.js plotly.js
   npm install -D @types/react-plotly.js
   ```

3. Confirm `tsconfig.json` has the `@/*` path alias (create-next-app sets
   this up by default):
   ```json
   "paths": { "@/*": ["./*"] }
   ```

4. Set your backend URL:
   ```bash
   echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > .env.local
   ```

5. Make sure the backend's CORS allows `http://localhost:3000` (it currently
   allows `*`, so this already works locally — just don't forget to restrict
   it to your real Vercel URL before final deploy).

6. Run it:
   ```bash
   npm run dev
   ```
   You should see the boot sequence, then the terminal chat UI. Ask a
   question — it calls your real `/ask` endpoint.

## What's implemented vs. still open
- Boot sequence, terminal chat, route badges, SQL query display, Plotly
  chart rendering, error states, loading state — all wired to the real
  backend contract you already confirmed works.
- NOT yet included: the atmospheric shader/particle background (Level 0
  in DESIGN.md), the upload dropzones (structured/document), and the
  settings panel for backend URL. `lib/api.ts` already has
  `uploadStructured`/`uploadDocument` typed and ready — those endpoints
  need to exist on the backend first (per the earlier upload task brief)
  before a dropzone component is worth building.
- Mobile layout: current version is responsive via Tailwind's default
  flow but hasn't been visually tuned against DESIGN.md's "bottom-anchored
  command bar" spec for small screens — worth a pass once desktop is
  confirmed good.
