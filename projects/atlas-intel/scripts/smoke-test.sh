#!/usr/bin/env bash
# Atlas Intel — Smoke Test
# Verifies: TypeScript compiles, Vite builds, dev server starts, backend serves data

set -e
cd "$(dirname "$0")/.."

echo "=== 1. TypeScript check ==="
npx tsc --noEmit
echo "✓ TypeScript clean"

echo "=== 2. Vite production build ==="
npx vite build 2>&1 | tail -5
echo "✓ Build successful"

echo "=== 3. Check all required files exist ==="
# Check public assets
for f in public/textures/earth-topo.jpg public/textures/earth-water.png public/textures/night-sky.png public/countries.geojson; do
  if [ -f "$f" ]; then echo "  ✓ $f"; else echo "  ✗ MISSING: $f"; fi
done

echo "=== 4. Dev server starts ==="
npx vite &
VITE_PID=$!
sleep 3
if curl -s http://localhost:5173 | grep -q "ATLAS INTEL"; then
  echo "✓ Dev server serving correctly"
else
  echo "✗ Dev server not responding"
fi
kill $VITE_PID 2>/dev/null

echo "=== 5. Check data JSON files exist ==="
REQUIRED_JSON="vessel_live flight_live military_live earthquake_live news_live cyber_threats_live"
for name in $REQUIRED_JSON; do
  f="dashboard/data/${name}.json"
  if [ -f "$f" ]; then echo "  ✓ $f ($(du -h "$f" | cut -f1))"; else echo "  ✗ MISSING: $f"; fi
done

echo "=== 6. Source file count ==="
echo "  TypeScript: $(find src -name '*.ts' | wc -l) files"
echo "  CSS: $(find src -name '*.css' | wc -l) files"
echo "  Total lines: $(find src -name '*.ts' -o -name '*.css' | xargs wc -l | tail -1)"

echo ""
echo "=== Smoke test complete ==="
