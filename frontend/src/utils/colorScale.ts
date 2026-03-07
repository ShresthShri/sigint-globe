export function severityToColor(severity: number): string {
  if (severity === 0) return "#1a9850";
  if (severity < 2) return "#66bd63";
  if (severity < 4) return "#fee08b";
  if (severity < 6) return "#fdae61";
  if (severity < 8) return "#f46d43";
  return "#d73027";
}

export function severityToOpacity(severity: number): number {
  if (severity === 0) return 0.15;
  return 0.3 + severity * 0.07;
}
