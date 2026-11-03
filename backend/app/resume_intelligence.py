import re
from collections import Counter

KNOWN_SKILLS = [
    "python", "java", "javascript", "typescript", "react", "fastapi", "sql", "postgresql",
    "mongodb", "docker", "kubernetes", "aws", "azure", "git", "machine learning", "data science",
    "statistics", "communication", "problem solving", "figma", "excel", "pandas", "numpy",
]


def extract_resume(text: str) -> dict:
    lowered = text.lower()
    skills = [skill.title() for skill in KNOWN_SKILLS if skill in lowered]
    sections = {}
    for heading in ("education", "skills", "projects", "experience", "internships", "certifications", "achievements"):
        match = re.search(rf"\b{heading}\b\s*:?\s*(.*?)(?=\n\s*[A-Z][A-Za-z ]{{2,30}}\s*:?\s*\n|\Z)", text, re.I | re.S)
        sections[heading] = match.group(1).strip()[:3000] if match else ""
    return {"skills": skills, "sections": sections, "limitations": "Deterministic text extraction requires user confirmation; names and claims are not verified."}


def extract_job(text: str) -> dict:
    lowered = text.lower()
    found = [skill.title() for skill in KNOWN_SKILLS if skill in lowered]
    preferred_words = ("preferred", "nice to have", "bonus", "plus")
    preferred = [skill for skill in found if any(word in lowered[max(0, lowered.find(skill.lower())-100):lowered.find(skill.lower())+100] for word in preferred_words)]
    required = [skill for skill in found if skill not in preferred]
    responsibilities = [line.strip("- •") for line in text.splitlines() if re.search(r"\b(build|develop|design|manage|analyse|analyze|lead|maintain|deliver)\b", line, re.I)][:10]
    education = [line.strip() for line in text.splitlines() if re.search(r"\b(bachelor|master|degree|diploma|phd)\b", line, re.I)][:5]
    return {"required_skills": required, "preferred_skills": preferred, "responsibilities": responsibilities, "education": education,
            "keywords": sorted(set(found)), "experience_requirements": [line.strip() for line in text.splitlines() if re.search(r"\b\d+\+?\s*(years?|months?)\b", line, re.I)][:5],
            "limitations": "Keyword extraction is deterministic and should be reviewed against the original job description."}


def match_job(job: dict, skills, projects, experiences, certifications, profile) -> dict:
    claimed = {skill.name.lower(): skill for skill in skills}
    project_text = " ".join((project.technologies or "") + " " + (project.skills_demonstrated or "") for project in projects).lower()
    rows = []
    for required in job.get("required_skills", []) + job.get("preferred_skills", []):
        key = required.lower()
        skill = claimed.get(key)
        if skill and (skill.verified or skill.evidence):
            status = "Matched"
            reason = "Career Twin skill with supporting evidence."
        elif skill:
            status = "Needs verification"
            reason = "Skill is self-assessed without linked evidence."
        elif key in project_text:
            status = "Partially matched"
            reason = "Skill appears in a recorded project, but no Career Twin skill claim exists."
        else:
            status = "Missing"
            reason = "No matching skill or project evidence was found."
        rows.append({"requirement": required, "status": status, "reason": reason})
    weights = {"Matched": 1, "Partially matched": .6, "Needs verification": .35, "Missing": 0}
    score = round(sum(weights[row["status"]] for row in rows) / len(rows) * 100, 1) if rows else None
    relevant_projects = [{"name": project.name, "reason": "Contains job keywords in recorded technologies or demonstrated skills."}
                         for project in projects
                         if any(word.lower() in ((project.technologies or "") + " " + (project.skills_demonstrated or "")).lower()
                                for word in job.get("required_skills", []))]
    gaps = [row["requirement"] for row in rows if row["status"] in ("Missing", "Needs verification")]
    suggestions = [f"Add evidence for {gap} before presenting it as demonstrated." if any(row["requirement"] == gap and row["status"] == "Needs verification" for row in rows) else f"Build or practise {gap}." for gap in gaps]
    return {"score": score, "criteria": "Matched=100%, partially matched=60%, needs verification=35%, missing=0%; score measures profile alignment, not hiring probability.",
            "requirements": rows, "gaps": gaps, "relevant_projects": relevant_projects, "resume_suggestions": suggestions}
