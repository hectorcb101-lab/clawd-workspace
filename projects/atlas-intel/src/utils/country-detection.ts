// ============================================================================
// Atlas Intel — Local GeoJSON Point-in-Polygon Country Detection
// ============================================================================
//
// Uses ray-casting against a countries GeoJSON file to resolve lat/lng → ISO
// country code or country name without any external geocoding service.
//
// NOTE: Standard GeoJSON coordinates are [longitude, latitude].
// The point-in-polygon algorithm treats index 0 as x (longitude) and
// index 1 as y (latitude).
// ============================================================================

interface GeoFeature {
  type: string;
  properties: { ISO_A2?: string; ADMIN?: string; [key: string]: unknown };
  geometry: {
    type: 'Polygon' | 'MultiPolygon';
    coordinates: number[][][] | number[][][][];
  };
}

let countriesGeoJSON: GeoFeature[] | null = null;

// ---------------------------------------------------------------------------
// Loader
// ---------------------------------------------------------------------------

/** Load countries GeoJSON (lazy, cached) */
export async function loadCountriesGeoJSON(): Promise<void> {
  if (countriesGeoJSON) return;
  const resp = await fetch('/countries.geojson');
  const data = await resp.json();
  countriesGeoJSON = data.features;
}

// ---------------------------------------------------------------------------
// Ray-casting algorithm
// ---------------------------------------------------------------------------

/**
 * Determine whether a point (lng, lat) lies inside a polygon ring.
 *
 * GeoJSON rings are arrays of [lng, lat] pairs, so:
 *   polygon[i][0] → longitude (x)
 *   polygon[i][1] → latitude  (y)
 *
 * The function accepts (lat, lng) as separate args to match the rest of
 * the codebase's Coordinates convention, but internally maps them to the
 * correct axes for the GeoJSON coordinate order.
 */
function pointInPolygon(lat: number, lng: number, polygon: number[][]): boolean {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i][0]; // longitude (x)
    const yi = polygon[i][1]; // latitude  (y)
    const xj = polygon[j][0]; // longitude (x)
    const yj = polygon[j][1]; // latitude  (y)

    const intersect =
      ((yi > lat) !== (yj > lat)) &&
      (lng < ((xj - xi) * (lat - yi)) / (yj - yi) + xi);

    if (intersect) inside = !inside;
  }
  return inside;
}

// ---------------------------------------------------------------------------
// Helpers — iterate geometry rings
// ---------------------------------------------------------------------------

function matchFeature(
  feature: GeoFeature,
  lat: number,
  lng: number,
): boolean {
  const geo = feature.geometry;

  if (geo.type === 'Polygon') {
    for (const ring of geo.coordinates as number[][][]) {
      if (pointInPolygon(lat, lng, ring)) return true;
    }
  } else if (geo.type === 'MultiPolygon') {
    for (const polygon of geo.coordinates as number[][][][]) {
      for (const ring of polygon) {
        if (pointInPolygon(lat, lng, ring)) return true;
      }
    }
  }

  return false;
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/** Detect country ISO-A2 code from lat/lng */
export function detectCountry(lat: number, lng: number): string | null {
  if (!countriesGeoJSON) return null;

  for (const feature of countriesGeoJSON) {
    if (matchFeature(feature, lat, lng)) {
      return feature.properties.ISO_A2 || null;
    }
  }

  return null;
}

/** Detect country name (ADMIN field) from lat/lng */
export function detectCountryName(lat: number, lng: number): string | null {
  if (!countriesGeoJSON) return null;

  for (const feature of countriesGeoJSON) {
    if (matchFeature(feature, lat, lng)) {
      return feature.properties.ADMIN || null;
    }
  }

  return null;
}
