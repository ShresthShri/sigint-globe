import { useEffect, useRef, useState } from "react";

interface TimeScrubberProps {
  timestamps: string[];
  snapshotIds: number[];
  currentIndex: number;
  onIndexChange: (index: number) => void;
}

export default function TimeScrubber({
  timestamps,
  snapshotIds,
  currentIndex,
  onIndexChange,
}: TimeScrubberProps) {
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (playing) {
      intervalRef.current = setInterval(() => {
        onIndexChange(-1);
      }, 1000 / speed);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [playing, speed]);

  if (snapshotIds.length === 0) {
    return (
      <div style={containerStyle}>
        <span style={{ color: "#888" }}>No snapshots yet — waiting for data...</span>
      </div>
    );
  }

  const currentTime = timestamps[currentIndex]
    ? new Date(timestamps[currentIndex]).toLocaleTimeString()
    : "--:--:--";

  const currentDate = timestamps[currentIndex]
    ? new Date(timestamps[currentIndex]).toLocaleDateString()
    : "";

  return (
    <div style={containerStyle}>
      <button
        onClick={() => setPlaying(!playing)}
        style={buttonStyle}
      >
        {playing ? "⏸" : "▶"}
      </button>

      <button
        onClick={() => setSpeed(speed === 1 ? 2 : speed === 2 ? 5 : 1)}
        style={buttonStyle}
      >
        {speed}x
      </button>

      <input
        type="range"
        min={0}
        max={snapshotIds.length - 1}
        value={currentIndex}
        onChange={(e) => {
          setPlaying(false);
          onIndexChange(Number(e.target.value));
        }}
        style={{ flex: 1, cursor: "pointer" }}
      />

      <span style={{ color: "#ccc", fontSize: 13, minWidth: 160, textAlign: "right" }}>
        {currentDate} {currentTime}
      </span>

      <span style={{ color: "#666", fontSize: 12, minWidth: 80, textAlign: "right" }}>
        {currentIndex + 1} / {snapshotIds.length}
      </span>
    </div>
  );
}

const containerStyle: React.CSSProperties = {
  position: "absolute",
  bottom: 24,
  left: "50%",
  transform: "translateX(-50%)",
  width: "80%",
  maxWidth: 700,
  background: "rgba(10, 10, 10, 0.9)",
  border: "1px solid #333",
  borderRadius: 8,
  padding: "10px 16px",
  display: "flex",
  alignItems: "center",
  gap: 12,
  zIndex: 1000,
};

const buttonStyle: React.CSSProperties = {
  background: "#222",
  border: "1px solid #444",
  borderRadius: 4,
  color: "#ccc",
  padding: "4px 10px",
  cursor: "pointer",
  fontSize: 14,
};
