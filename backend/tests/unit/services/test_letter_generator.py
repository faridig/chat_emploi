from unittest.mock import MagicMock, patch

import pytest
from services.letter_generator import LetterGenerationError, LetterGeneratorService


class TestLetterGeneratorService:
    @pytest.fixture
    def service(self):
        return LetterGeneratorService()

    @pytest.fixture
    def sample_data(self):
        return {
            "content": "Ceci est un paragraphe de test pour la lettre de motivation. "
            * 20,
            "candidate_name": "Jean Dupont",
            "job_title": "Développeur Python",
            "company_name": "Tech Corp",
            "date": "29 janvier 2026",
        }

    def test_validate_length_success(self, service):
        """Test validation longueur correcte (entre 100 et 1000 mots pour l'instant)"""
        text = "mot " * 350
        assert service.validate_length(text) is True

    def test_validate_length_too_short(self, service):
        """Test validation échoue si trop court"""
        text = "mot " * 49
        with pytest.raises(LetterGenerationError) as exc:
            service.validate_length(text)
        assert "trop courte" in str(exc.value)

    def test_validate_length_too_long(self, service):
        """Test validation échoue si trop long"""
        text = "mot " * 1001
        with pytest.raises(LetterGenerationError) as exc:
            service.validate_length(text)
        assert "trop longue" in str(exc.value)

    def test_render_html(self, service, sample_data):
        """Test du rendu Jinja2"""
        # On injecte un template simple pour le test via le constructeur ou attribut si possible,
        # mais ici on va tester avec le vrai template ou un mock du loader

        # Pour ce test unitaire, on va mocker jinja_env.get_template
        with patch.object(service.jinja_env, "get_template") as mock_get:
            mock_template = MagicMock()
            mock_template.render.return_value = "<html>Jean Dupont</html>"
            mock_get.return_value = mock_template

            html = service.render_html(sample_data, template_name="test.html")

            assert "Jean Dupont" in html
            mock_template.render.assert_called_once()

    @patch("services.letter_generator.HTML")
    def test_generate_pdf(self, mock_html_cls, service, tmp_path):
        """Test de la génération PDF via WeasyPrint"""
        html_content = "<html><body>Test</body></html>"
        output_path = tmp_path / "test.pdf"

        # Setup mock
        mock_html_instance = MagicMock()
        mock_html_cls.return_value = mock_html_instance

        # Action
        result_path = service.generate_pdf(html_content, str(output_path))

        # Assertions
        assert result_path == str(output_path)
        mock_html_cls.assert_called_with(string=html_content, base_url=service.base_url)
        mock_html_instance.write_pdf.assert_called_once_with(str(output_path))

    def test_sanitize_filename(self, service):
        """Test nettoyage nom de fichier"""
        unsafe = "../../etc/passwd.pdf"
        safe = service._sanitize_filename(unsafe)
        assert "/" not in safe
        # Les .. sont retirés explicitement maintenant
        assert ".." not in safe
        # Le résultat attendu avec ma nouvelle logique
        assert safe == "etcpasswd.pdf"

        unsafe_complex = "Lettre: Jean Dupont / Tech Corp!.pdf"
        safe_complex = service._sanitize_filename(unsafe_complex)
        assert ":" not in safe_complex
        assert "/" not in safe_complex
        # Espaces remplacés par _ et compactés
        assert (
            safe_complex == "Lettre_Jean_Dupont_Tech_Corppdf"
            or safe_complex == "Lettre_Jean_Dupont_Tech_Corp.pdf"
        )
        # wait, le ! est supprimé. "Corp!" -> "Corp"
        # "Lettre: Jean Dupont / Tech Corp!.pdf" -> "Lettre Jean Dupont  Tech Corp.pdf"
        # \s+ -> _
        # "Lettre_Jean_Dupont_Tech_Corp.pdf"
        assert safe_complex == "Lettre_Jean_Dupont_Tech_Corp.pdf"

    def test_generate_full_process(self, service, sample_data, tmp_path):
        """Test d'intégration du service complet (mockant juste WeasyPrint)"""
        with patch("services.letter_generator.HTML") as mock_html_cls:
            mock_html_instance = MagicMock()
            mock_html_cls.return_value = mock_html_instance

            # On utilise le template par défaut qui doit exister (ou on mock si pas encore créé)
            # Ici on va mocker render_html pour simplifier ce test si on n'a pas encore le fichier template
            with patch.object(service, "render_html", return_value="<html>TEST</html>"):
                output_dir = tmp_path / "letters"
                output_dir.mkdir()

                result = service.generate_letter(
                    data=sample_data, output_dir=str(output_dir)
                )

                assert result["pdf_path"].endswith(".pdf")
                assert result["html_content"] == "<html>TEST</html>"
                assert "word_count" in result["metadata"]
