import { useEffect, useState } from "react";
import { MapContainer, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import HexLayer from "./components/HexLayer";
import { fetchInterference } from "./api/client";
import type { InterferenceCell } from "./types";

export default function App() {
  const [cells, setCells] = useState<InterferenceCell[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchInterference()
      .then((data) => {
        setCells(data);
        setError(null);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

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
    </div>
  );
}
