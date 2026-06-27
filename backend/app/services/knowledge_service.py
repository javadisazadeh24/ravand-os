from pathlib import Path
from typing import Dict


class KnowledgeService:
    """
    Reads markdown knowledge files from the project knowledge directory.
    """

    def __init__(self):
        # Project root:
        # backend/app/services -> backend -> project root
        self.project_root = Path(__file__).resolve().parents[3]

        self.knowledge_dir = self.project_root / "knowledge"

    def read(self, filename: str) -> str:
        file_path = self.knowledge_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(f"{filename} not found")

        return file_path.read_text(encoding="utf-8")

    def company(self) -> str:
        return self.read("company.md")

    def products(self) -> str:
        return self.read("products.md")

    def services(self) -> str:
        return self.read("services.md")

    def pricing(self) -> str:
        return self.read("pricing.md")

    def all(self) -> Dict[str, str]:
        return {
            "company": self.company(),
            "products": self.products(),
            "services": self.services(),
            "pricing": self.pricing(),
        }


knowledge = KnowledgeService()