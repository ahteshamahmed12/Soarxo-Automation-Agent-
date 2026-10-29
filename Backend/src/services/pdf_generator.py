from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..models.approval import ApprovalRequest
from ..models.invoice import InvoiceDraft
from ..core.config import settings
from ..core.logging import log


class PDFGenerator:
    """Generates PDF invoices using WeasyPrint + Jinja2 templates."""

    def __init__(self) -> None:
        template_dir = Path(__file__).parent.parent / "templates"
        self._env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html"]),
        )

    def generate_invoice_pdf(self, invoice: InvoiceDraft) -> str:
        """Generate an invoice PDF and return the output file path."""
        template = self._env.get_template("invoice_template.html")
        html_content = template.render(
            invoice=invoice,
            logo_url="",  # Could be a URL or base64
        )

        output_dir = Path(settings.PROJECT_ROOT) / "generated_pdfs" / "invoices"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"invoice_{invoice.id}.pdf"

        from weasyprint import HTML

        HTML(string=html_content, base_url=str(template_dir)).write_pdf(
            target=str(output_path)
        )

        log.info(
            "Invoice PDF generated",
            extra={
                "action": "pdf_generate",
                "actor": "agent",
                "invoice_id": invoice.id,
                "output_path": str(output_path),
            },
        )
        return str(output_path)