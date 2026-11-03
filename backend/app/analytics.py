import json
from collections import defaultdict
from datetime import datetime
from statistics import mean
from sklearn.linear_model import LinearRegression
from sqlalchemy.orm import Session
from .models import AcademicRecord, Attendance, DigitalTwinSnapshot, Student


def calculate_twin(student: Student, db: Session, persist: bool = True) -> dict:
    subject_scores = defaultdict(list)
    for record in student.records:
        subject_scores[record.subject.name].append((record.score / record.max_score) * 100)
    subject_attendance = defaultdict(lambda: [0, 0])
    for row in student.attendance:
        subject_attendance[row.subject.name][0] += row.attended
        subject_attendance[row.subject.name][1] += row.total
    scores = [value for values in subject_scores.values() for value in values]
    attendance_total = sum(row.total for row in student.attendance)
    attendance_attended = sum(row.attended for row in student.attendance)
    study_hours = [item.hours for item in student.study_activities]
    average_score = round(mean(scores), 1) if scores else None
    attendance_rate = round(attendance_attended / attendance_total * 100, 1) if attendance_total else None
    average_daily_study = round(mean(study_hours), 1) if study_hours else 0
    subject_summary = []
    for subject in student.subjects:
        subject_values = subject_scores.get(subject.name, [])
        att = subject_attendance[subject.name]
        score = round(mean(subject_values), 1) if subject_values else None
        rate = round(att[0] / att[1] * 100, 1) if att[1] else None
        subject_summary.append({"subject": subject.name, "score": score, "attendance": rate,
                                "status": "strong" if score is not None and score >= 75 else "needs_attention" if score is not None else "no_data"})
    risks = []
    if average_score is not None and average_score < 50:
        risks.append({"level": "high", "title": "Low academic performance", "detail": "Your current average is below 50%."})
    elif average_score is not None and average_score < 65:
        risks.append({"level": "medium", "title": "Performance needs attention", "detail": "Use targeted revision for lower-scoring subjects."})
    if attendance_rate is not None and attendance_rate < 75:
        risks.append({"level": "high", "title": "Attendance risk", "detail": "Attendance is below the recommended 75%."})
    if study_hours and mean(study_hours) < 1:
        risks.append({"level": "medium", "title": "Inconsistent study routine", "detail": "Build a daily study block of at least one hour."})
    prediction = None
    if len(scores) >= 3:
        model = LinearRegression().fit([[index] for index in range(len(scores))], scores)
        projected = float(model.predict([[len(scores)]])[0])
        prediction = {"value": round(min(100, max(0, projected)), 1),
                      "method": "linear regression", "confidence": "limited",
                      "explanation": "This estimate uses assessment sequence only; it is not a substitute for a validated cohort model and improves with longitudinal data."}
    recommendations = []
    for row in subject_summary:
        if row["status"] == "needs_attention":
            recommendations.append({"title": f"Prioritise {row['subject']}", "detail": "Schedule two focused practice sessions and review mistakes."})
    if attendance_rate is not None and attendance_rate < 85:
        recommendations.append({"title": "Protect attendance", "detail": "Attend upcoming classes and review missed material within 24 hours."})
    if not recommendations:
        recommendations.append({"title": "Maintain momentum", "detail": "Keep logging study activity and review progress weekly."})
    state = {"average_score": average_score, "attendance_rate": attendance_rate, "average_daily_study": average_daily_study,
             "subject_summary": subject_summary, "risks": risks, "prediction": prediction,
             "recommendations": recommendations, "updated_at": datetime.utcnow().isoformat()}
    if persist:
        snapshot = DigitalTwinSnapshot(student_id=student.id, state_json=json.dumps(state))
        db.add(snapshot)
        db.commit()
    return state
