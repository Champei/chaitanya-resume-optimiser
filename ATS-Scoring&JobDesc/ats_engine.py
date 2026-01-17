import re
import numpy as np
import spacy
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Any
from github_ground import load_github_corpus_text

nlp = spacy.load("en_core_web_lg")
embedder = SentenceTransformer("all-MiniLM-L6-v2")


class ATSEngine:
    def __init__(self):
        self.github_text = load_github_corpus_text()

    def extract_skills(self, text: str) -> Dict[str, Any]:
        doc = nlp(text)
        skills = set()

        for chunk in doc.noun_chunks:
            token_text = chunk.text.lower()
            if 2 <= len(token_text.split()) <= 4:
                skills.add(token_text)

        return {
            "detected": sorted(skills),
            "confidence": round(min(len(skills) / 20, 1.0), 2)
        }

    def extract_projects(self, text: str) -> List[str]:
        patterns = [
            r"project[:\-]\s*(.+)",
            r"built\s+(.*)",
            r"developed\s+(.*)"
        ]

        projects = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            projects.extend(matches)

        return list(set(p.strip() for p in projects))

    def extract_experience(self, text: str) -> Dict[str, Any]:
        year_matches = re.findall(r"(20\d{2}|19\d{2})", text)

        if not year_matches:
            return {
                "estimated_years": 0,
                "confidence": "low",
                "reason": "No year patterns found"
            }

        years = sorted(map(int, year_matches))
        experience = max(years) - min(years)

        return {
            "estimated_years": max(experience, 0),
            "confidence": "high"
        }
    # Semantic similarity


    def semantic_similarity(self, a: str, b: str) -> float:
        if not a.strip() or not b.strip():
            return 0.0

        a_vec = embedder.encode(a)
        b_vec = embedder.encode(b)

        return float(
            np.dot(a_vec, b_vec)
            / (np.linalg.norm(a_vec) * np.linalg.norm(b_vec))
        )

    def compute_ats_score(self, signals: List[float]) -> Dict[str, Any]:
        valid = [s for s in signals if s > 0]

        if not valid:
            return {
                "value": 0.0,
                "confidence": "low",
                "reason": "Insufficient data"
            }

        score = round(sum(valid) / len(valid) * 100, 2)

        return {
            "value": score,
            "confidence": "high" if score > 70 else "medium"
        }

    def analyze(
        self,
        resume_text: str,
        job_description: str
    ) -> Dict[str, Any]:

        skills = self.extract_skills(resume_text)
        projects = self.extract_projects(resume_text)
        experience = self.extract_experience(resume_text)

        sem_resume_jd = self.semantic_similarity(resume_text, job_description)
        sem_resume_git = self.semantic_similarity(resume_text, self.github_text)

        ats = self.compute_ats_score([
            sem_resume_jd,
            sem_resume_git,
            skills["confidence"]
        ])

        return {
            "resume_extracted": {
                "skills": skills,
                "projects": projects if projects else ["Not explicitly found"],
                "experience": experience
            },
            "job_description": job_description[:500],
            "semantic_similarity": {
                "resume_job": round(sem_resume_jd, 3),
                "resume_github": round(sem_resume_git, 3)
            },
            "ats_score": ats
        }
