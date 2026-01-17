import requests
from typing import List

GITHUB_REPOS = [
    "https://raw.githubusercontent.com/jwasham/coding-interview-university/main/README.md",
    "https://raw.githubusercontent.com/ossu/computer-science/master/README.md",
    "https://raw.githubusercontent.com/donnemartin/system-design-primer/master/README.md"
]

def load_github_corpus_text() -> str:
    texts: List[str] = []

    for url in GITHUB_REPOS:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                texts.append(response.text)
        except Exception:
            continue

    return "\n".join(texts)
