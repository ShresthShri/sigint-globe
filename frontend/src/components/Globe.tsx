import { Ion, Color, Cartesian3 } from "cesium";
import { Viewer, Entity, PolygonGraphics } from "resium";
import { cellToBoundary } from "h3-js";
import type { InterferenceCell } from "../types";
import { severityToColor, severityToOpacity } from "../utils/colorScale";

Ion.defaultAccessToken = import.meta.env.VITE_CESIUM_TOKEN;

function hexToRgb(hex: string): [number, number, number] {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return [r, g, b];
}

function cellToCartesian(h3Index: string): Cartesian3[] {
  const boundary = cellToBoundary(h3Index);
  return boundary.map(([lat, lng]) =>
    Cartesian3.fromDegrees(lng, lat)
  );
}

interface GlobeProps {
  cells: InterferenceCell[];
}

export default function Globe({ cells }: GlobeProps) {
  return (
    <Viewer
      full
      timeline={false}
      animation={false}
      homeButton={false}
      sceneModePicker={false}
      baseLayerPicker={false}
      navigationHelpButton={false}
      geocoder={false}
      fullscreenButton={false}
      selectionIndicator
      infoBox
    >
      {cells.map((cell) => {
        const positions = cellToCartesian(cell.h3_index);
        const [r, g, b] = hexToRgb(severityToColor(cell.severity));
        const opacity = severityToOpacity(cell.severity);

        return (
          <Entity
            key={cell.h3_index}
            name={`Severity: ${cell.severity.toFixed(1)}`}
            description={`
              Aircraft: ${cell.aircraft_count}<br/>
              Low NACp: ${cell.low_nac_count}<br/>
              Avg NACp: ${cell.avg_nac_p.toFixed(1)}<br/>
              Ratio: ${(cell.interference_ratio * 100).toFixed(0)}%
            `}
          >
            <PolygonGraphics
              hierarchy={positions}
              material={Color.fromBytes(r, g, b, Math.floor(opacity * 255))}
              outline
              outlineColor={Color.fromBytes(r, g, b, 200)}
              outlineWidth={1}
            />
          </Entity>
        );
      })}
    </Viewer>
  );
}
