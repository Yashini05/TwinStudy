export type SimulationValues = {
  study_hours_delta: number;
  attendance_delta: number;
  score_delta: number;
};

export function projectScore(base: number, values: SimulationValues) {
  const projected = Math.min(
    100,
    Math.max(0, base + values.score_delta + values.study_hours_delta * 2 + values.attendance_delta * 0.15),
  );
  return Math.round(projected * 10) / 10;
}
