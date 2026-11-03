import { describe, expect, it } from "vitest";
import { projectScore } from "./simulation";

describe("what-if projection", () => {
  it("applies changes and caps the score at 100", () => {
    expect(projectScore(80, { study_hours_delta: 10, attendance_delta: 10, score_delta: 5 })).toBe(100);
  });

  it("never returns a negative score", () => {
    expect(projectScore(10, { study_hours_delta: -24, attendance_delta: -100, score_delta: -100 })).toBe(0);
  });
});
