/**
 * EventPanel — collapsible sidebar showing GPS/EW-related news events.
 *
 * Fetches events from the backend on mount, displays them as a
 * scrollable list with timestamp, source, headline, and matched keywords.
 * Clicking a headline opens the source article in a new tab.
 */

import { useEffect, useState } from "react";
import { fetchEvents, type EventData } from "../api/client";

export default function EventPanel() {
  const [events, setEvents] = useState<EventData[]>([]);
  const [collapsed, setCollapsed] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch events on mount, then refresh every 5 minutes
    loadEvents();
    const interval = setInterval(loadEvents, 300000);
    return () => clearInterval(interval);
  }, []);

  const loadEvents = async () => {
    try {
      const data = await fetchEvents(30);
      setEvents(data);
    } catch (err) {
      console.error("Failed to fetch events:", err);
    } finally {
      setLoading(false);
    }
  };

  // Format timestamp to a short readable string
  const formatTime = (ts: string) => {
    const d = new Date(ts);
    return d.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div style={panelStyle}>
      {/* Header with collapse toggle */}
      <div
        onClick={() => setCollapsed(!collapsed)}
        style={headerStyle}
      >
        <span>Events {events.length > 0 && `(${events.length})`}</span>
        <span>{collapsed ? "◀" : "▶"}</span>
      </div>

      {/* Event list — only shown when not collapsed */}
      {!collapsed && (
        <div style={listStyle}>
          {loading && (
            <div style={{ color: "#666", padding: 12, fontSize: 12 }}>
              Loading events...
            </div>
          )}

          {!loading && events.length === 0 && (
            <div style={{ color: "#666", padding: 12, fontSize: 12 }}>
              No GPS/EW events found yet. The collector polls RSS feeds
              every 30 minutes.
            </div>
          )}

          {events.map((event) => (
            <div key={event.id} style={eventCardStyle}>
              {/* Source badge and timestamp */}
              <div style={metaRowStyle}>
                <span style={sourceBadgeStyle}>{event.source}</span>
                <span style={timeStyle}>{formatTime(event.timestamp)}</span>
              </div>

              {/* Headline — links to source article */}
             <a 
                href={event.url || "#"}
                target="_blank"
                rel="noopener noreferrer"
                style={headlineStyle}
              >
                {event.headline}
              </a>

              {/* Matched keywords and region tag */}
              <div style={tagRowStyle}>
                {event.keywords_matched && (
                  <span style={keywordStyle}>{event.keywords_matched}</span>
                )}
                {event.region_name && (
                  <span style={regionStyle}>{event.region_name}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* --- Styles --- */

const panelStyle: React.CSSProperties = {
  position: "absolute",
  top: 16,
  right: 16,
  width: 320,
  maxHeight: "70vh",
  background: "rgba(10, 10, 10, 0.92)",
  border: "1px solid #333",
  borderRadius: 8,
  zIndex: 1000,
  display: "flex",
  flexDirection: "column",
  overflow: "hidden",
};

const headerStyle: React.CSSProperties = {
  padding: "10px 14px",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  cursor: "pointer",
  color: "#ccc",
  fontSize: 14,
  fontWeight: 600,
  borderBottom: "1px solid #333",
  userSelect: "none",
};

const listStyle: React.CSSProperties = {
  overflowY: "auto",
  flex: 1,
};

const eventCardStyle: React.CSSProperties = {
  padding: "10px 14px",
  borderBottom: "1px solid #222",
};

const metaRowStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: 4,
};

const sourceBadgeStyle: React.CSSProperties = {
  fontSize: 10,
  fontWeight: 600,
  color: "#999",
  textTransform: "uppercase",
  letterSpacing: "0.5px",
};

const timeStyle: React.CSSProperties = {
  fontSize: 10,
  color: "#666",
};

const headlineStyle: React.CSSProperties = {
  fontSize: 12,
  lineHeight: "1.4",
  color: "#ddd",
  textDecoration: "none",
  display: "block",
  marginBottom: 4,
};

const tagRowStyle: React.CSSProperties = {
  display: "flex",
  gap: 6,
  flexWrap: "wrap",
};

const keywordStyle: React.CSSProperties = {
  fontSize: 10,
  color: "#f46d43",
  background: "rgba(244, 109, 67, 0.15)",
  padding: "1px 6px",
  borderRadius: 3,
};

const regionStyle: React.CSSProperties = {
  fontSize: 10,
  color: "#66bd63",
  background: "rgba(102, 189, 99, 0.15)",
  padding: "1px 6px",
  borderRadius: 3,
};
