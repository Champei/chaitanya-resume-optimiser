from pathlib import Path
from document_loader import DocumentLoader
from ats_engine import ATSSystem


def main():
    BASE_DIR = Path(__file__).parent

    resume_path = BASE_DIR / "resume.txt"
    jd_path = BASE_DIR / "jd.txt"

    # Load resume
    loader = DocumentLoader()
    resume_text = loader.load(str(resume_path))

    # Load job description (optional)
    if jd_path.exists():
        job_description = jd_path.read_text(encoding="utf-8", errors="ignore")
    else:
        job_description = (
            "Generic software engineering role requiring strong programming, "
            "problem-solving, data structures, and system design skills."
        )

    ats = ATSSystem()
    result = ats.analyze(resume_text, job_description)

    print(result)


if __name__ == "__main__":
    main()
