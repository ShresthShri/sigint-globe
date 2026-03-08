import { useCallback, useEffect, useRef, useState } from "react";
import { MapContainer, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import HexLayer from "./components/HexLayer";
import TimeScrubber from "./components/TimeScrubber";
import { fetchInterference, fetchTimeline } from "./api/client";
import type { InterferenceCell } from "./types";

export default function App() {
  const [cells, setCells] = useState<InterferenceCell[]>([]);
  const [snapshotIds, setSnapshotIds] = useState<number[]>([]);
  const [timestamps, setTimestamps] = useState<string[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const indexRef = useRef(currentIndex);
  indexRef.current = currentIndex;

  const loadTimeline = useCallback(async () => {
    try {
      const tl = await fetchTimeline();
      setSnapshotIds(tl.snapshot_ids);
      setTimestamps(tl.timestamps);
      if (tl.snapshot_ids.length > 0) {
        const lastIndex = tl.snapshot_ids.length - 1;
        setCurrentIndex(lastIndex);
        await loadCells(tl.snapshot_ids[lastIndex]);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadCells = async (snapshotId: number) => {
    try {
      const data = await fetchInterference(snapshotId);
      setCells(data);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    }
  };

  useEffect(() => {
    loadTimeline();
    const refreshInterval = setInterval(loadTimeline, 60000);
    return () => clearInterval(refreshInterval);
  }, []);

  const handleIndexChange = useCallback(
    (index: number) => {
      if (index === -1) {
        const next = indexRef.current + 1;
        if (next >= snapshotIds.length) {
          setCurrentIndex(0);
          if (snapshotIds[0]) loadCells(snapshotIds[0]);
        } else {
          setCurrentIndex(next);
          loadCells(snapshotIds[next]);
        }
      } else {
        setCurrentIndex(index);
        loadCells(snapshotIds[index]);
      }
    },
    [snapshotIds]
  );

  return (
    <div style={{ width: "100vw", height: "100vh", background: "#0a0a0a" }}>
      {error && (
        <div style={{
          position: "absolute",
          top: 16,
          left: "50%",
          transform: "translateX(-50%)",
          background: "#d73027",
          color: "white",
          padding: "8px 16px",
          borderRadius: 4,
          zIndex: 1000,
          fontSize: 13,
        }}>
          {error}
        </div>
      )}
      {loading && (
        <div style={{
          position: "absolute",
          top: 16,
          right: 16,
          color: "#aaa",
          zIndex: 1000,
        }}>
          Loading...
        </div>
      )}
      <MapContainer
        center={[34.7, 33.5]}
        zoom={6}
        style={{ width: "100%", height: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        <HexLayer cells={cells} />
      </MapContainer>
      <TimeScrubber
        timestamps={timestamps}
        snapshotIds={snapshotIds}
        currentIndex={currentIndex}
        onIndexChange={handleIndexChange}
      />
    </div>
  );
}
