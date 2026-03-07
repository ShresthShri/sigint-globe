import { Polygon, Tooltip } from "react-leaflet";
import { cellToBoundary } from "h3-js";
import type { InterferenceCell } from "../types";
import { severityToColor, severityToOpacity } from "../utils/colorScale";

interface HexLayerProps {
  cells: InterferenceCell[];
}

export default function HexLayer({ cells }: HexLayerProps) {
  return (
    <>
      {cells.map((cell) => {
        const boundary = cellToBoundary(cell.h3_index);
        const positions = boundary.map(([lat, lng]) => [lat, lng] as [number, number]);

        return (
          <Polygon
            key={cell.h3_index}
            positions={positions}
            pathOptions={{
              color: severityToColor(cell.severity),
              fillColor: severityToColor(cell.severity),
              fillOpacity: severityToOpacity(cell.severity),
              weight: 1,
            }}
          >
            <Tooltip>
              <div>
                <strong>Severity: {cell.severity.toFixed(1)}</strong>
                <br />
                Aircraft: {cell.aircraft_count}
                <br />
                Low NACp: {cell.low_nac_count}
                <br />
                Avg NACp: {cell.avg_nac_p.toFixed(1)}
                <br />
                Ratio: {(cell.interference_ratio * 100).toFixed(0)}%
              </div>
            </Tooltip>
          </Polygon>
        );
      })}
    </>
  );
}
