from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.schemas.content import ResumeContent
from app.schemas.pdf_template import FidelityScoreBreakdown


class WriterStrategy(ABC):
    """Common abstraction for document writers: DOCX, PDF In-Place, and PDF Rebuild."""

    @abstractmethod
    def plan(self, content: ResumeContent, template_data: Any) -> Dict[str, Any]:
        """Calculates character/line budgets, formatting constraints, and planned reflow deltas."""
        pass

    @abstractmethod
    def write(self, content: ResumeContent, template_path: str, output_path: str, **kwargs) -> str:
        """Renders/writes tailored content to the output file path. Returns output path."""
        pass

    @abstractmethod
    def measure(self, original_path: str, generated_path: str, **kwargs) -> FidelityScoreBreakdown:
        """Measures fidelity between original and generated document (page count, position delta, SSIM)."""
        pass
