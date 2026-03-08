import type { InterferenceCell, SnapshotSummary } from "../types";

const BASE_URL = "http://localhost:8000";

export async function fetchInterference(
  snapshotId?: number
): Promise<InterferenceCell[]> {
  const url = new URL(`${BASE_URL}/interference`);
  if (snapshotId) {
    url.searchParams.set("snapshot_id", String(snapshotId));
  }
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Failed to fetch interference: ${res.status}`);
  return res.json();
}

export async function fetchSnapshots(
  limit: number = 20
): Promise<SnapshotSummary[]> {
  const res = await fetch(`${BASE_URL}/snapshots?limit=${limit}`);
  if (!res.ok) throw new Error(`Failed to fetch snapshots: ${res.status}`);
  return res.json();
}

export async function fetchTimeline(): Promise<{
  snapshot_ids: number[];
  timestamps: string[];
}> {
  const res = await fetch(`${BASE_URL}/interference/timeline`);
  if (!res.ok) throw new Error(`Failed to fetch timeline: ${res.status}`);
  return res.json();
}
