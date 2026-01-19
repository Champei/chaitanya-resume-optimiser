from pathlib import Path
import pdfplumber
import docx


class DocumentLoader:
    def load(self, file_path: str) -> str:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = path.suffix.lower()

        if suffix == ".pdf":
            return self._load_pdf(path)
        elif suffix == ".docx":
            return self._load_docx(path)
        elif suffix == ".txt":
            return self._load_txt(path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

    def _load_pdf(self, path: Path) -> str:
        text = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return "\n".join(text)

    def _load_docx(self, path: Path) -> str:
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    def _load_txt(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="ignore")
