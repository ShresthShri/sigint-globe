export interface InterferenceCell {
  h3_index: string;
  lat: number;
  lon: number;
  severity: number;
  aircraft_count: number;
  low_nac_count: number;
  interference_ratio: number;
  avg_nac_p: number;
  timestamp: string;
  snapshot_id: number;
}

export interface SnapshotSummary {
  id: number;
  timestamp: string;
  region_name: string;
  aircraft_total: number;
  aircraft_with_nacp: number;
  aircraft_low_nacp: number;
  duration_ms: number;
}
