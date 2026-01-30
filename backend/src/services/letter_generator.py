import logging
import os
import re
import uuid
from datetime import datetime
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

try:
    from weasyprint import CSS, HTML

    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

# Configuration du logging
logger = logging.getLogger(__name__)


class LetterGenerationError(Exception):
    """Exception levée en cas d'erreur de génération de lettre."""

    pass


class LetterGeneratorService:
    """Service de génération de lettres de motivation PDF/HTML."""

    def __init__(self, templates_dir: str | None = None):
        """Initialise le service avec le dossier des templates."""
        if templates_dir is None:
            # Par défaut : backend/src/templates
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            templates_dir = os.path.join(base_dir, "templates")

        self.templates_dir = templates_dir
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )
        self.base_url = f"file://{self.templates_dir}/"  # Pour les assets locaux

    def generate_letter(
        self,
        data: dict[str, Any],
        output_dir: str,
        template_name: str = "base_letter.html",
    ) -> dict[str, Any]:
        """
        Génère une lettre de motivation complète (HTML + PDF).

        Args:
            data: Dictionnaire contenant les données pour le template
            output_dir: Dossier de sortie pour les fichiers
            template_name: Nom du fichier template à utiliser

        Returns:
            Dict contenant les chemins des fichiers et métadonnées
        """
        try:
            # 1. Validation
            content = data.get("content", "")
            self.validate_length(content)

            # Enrichissement des données si manquant
            if "date" not in data:
                data["date"] = datetime.now().strftime("%d/%m/%Y")

            # 2. Génération HTML
            html_content = self.render_html(data, template_name)

            # 3. Préparation noms de fichiers
            offer_title = self._sanitize_filename(data.get("job_title", "offre"))
            candidate = self._sanitize_filename(data.get("candidate_name", "candidat"))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_base = f"Lettre_{candidate}_{offer_title}_{timestamp}"

            # Création dossier si nécessaire
            os.makedirs(output_dir, exist_ok=True)

            html_path = os.path.join(output_dir, f"{file_base}.html")
            pdf_path = os.path.join(output_dir, f"{file_base}.pdf")

            # 4. Sauvegarde HTML
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            # 5. Génération PDF
            final_pdf_path = self.generate_pdf(html_content, pdf_path)

            return {
                "id": str(uuid.uuid4()),
                "html_path": html_path,
                "pdf_path": final_pdf_path,
                "html_content": html_content,
                "metadata": {
                    "word_count": len(content.split()),
                    "generated_at": datetime.now().isoformat(),
                    "template_used": template_name,
                },
            }

        except Exception as e:
            logger.error(f"Erreur lors de la génération de la lettre : {str(e)}")
            raise LetterGenerationError(f"Échec de la génération : {str(e)}")

    def render_html(self, data: dict[str, Any], template_name: str) -> str:
        """Rend le contenu HTML à partir du template Jinja2."""
        try:
            template = self.jinja_env.get_template(template_name)
            # Conversion des sauts de ligne en <br> pour le HTML si le contenu est plain text
            if (
                "content" in data
                and "\n" in data["content"]
                and "<p>" not in data["content"]
            ):
                data["content"] = data["content"].replace("\n", "<br>")

            return template.render(**data)
        except Exception as e:
            raise LetterGenerationError(f"Erreur de templating : {str(e)}")

    def generate_pdf(self, html_content: str, output_path: str) -> str:
        """Génère le fichier PDF via WeasyPrint."""
        if not WEASYPRINT_AVAILABLE:
            logger.warning("WeasyPrint non disponible. Génération PDF simulée.")
            # Fallback : on crée un fichier vide ou texte pour dire "PDF non dispo"
            with open(output_path, "w") as f:
                f.write("PDF Generation not available (WeasyPrint missing)")
            return output_path

        try:
            HTML(string=html_content, base_url=self.base_url).write_pdf(output_path)
            return output_path
        except Exception as e:
            raise LetterGenerationError(f"Erreur WeasyPrint : {str(e)}")

    def validate_length(
        self, text: str, min_words: int = 50, max_words: int = 1000
    ) -> bool:
        """Valide la longueur du texte."""
        word_count = len(text.split())
        if word_count < min_words:
            raise LetterGenerationError(
                f"Lettre trop courte ({word_count} mots). Minimum : {min_words}"
            )
        if word_count > max_words:
            raise LetterGenerationError(
                f"Lettre trop longue ({word_count} mots). Maximum : {max_words}"
            )
        return True

    def _sanitize_filename(self, filename: str) -> str:
        """Nettoie un nom de fichier pour éviter les caractères dangereux."""
        # Garde seulement alphanumérique, tirets, underscores, espaces et points
        s = re.sub(r"[^\w\s\.-]", "", filename)
        # Remplace espaces par underscores
        s = re.sub(r"\s+", "_", s)
        # Empêche les path traversal en retirant les ..
        s = s.replace("..", "")
        return s.strip()
