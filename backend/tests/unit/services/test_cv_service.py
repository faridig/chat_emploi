"""Test suite for CV processing service.

Tests the CVService for analyzing and anonymizing CVs with mock Gemini API.
Following TDD approach - tests should fail initially.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from services.cv.cv_service import CVProcessingError, CVService


class TestCVService:
    """Test suite for CVService."""

    @pytest.fixture
    def mock_gemini_client(self):
        """Mock Gemini API client."""
        with patch("services.cv.cv_service.genai") as mock_genai:
            # Mock client
            mock_client = Mock()
            mock_models = Mock()

            # Setup mocks
            mock_client.models = mock_models
            mock_genai.Client.return_value = mock_client

            yield mock_genai, mock_client, mock_models

    @pytest.fixture
    def sample_cv_text(self):
        """Sample CV text for testing."""
        return """John Doe
Software Engineer
Skills: Python, React, AWS
Experience: 5 years at Tech Corp
Education: Master in Computer Science"""

    @pytest.fixture
    def sample_analysis_result(self):
        """Mock Gemini analysis result."""
        return {
            "extracted_data": {
                "skills": [
                    {"name": "Python", "level": "advanced", "years": 5},
                    {"name": "React", "level": "intermediate", "years": 3},
                    {"name": "AWS", "level": "intermediate", "years": 2},
                ],
                "experiences": [
                    {
                        "title": "Software Engineer",
                        "company": "Tech Corp",
                        "duration": "5 years",
                        "description": "Developed web applications",
                    }
                ],
                "education": [
                    {
                        "degree": "Master in Computer Science",
                        "school": "University",
                        "year": 2020,
                    }
                ],
            }
        }

    @pytest.fixture
    def cv_service(self, mock_gemini_client):
        """Create CVService instance with mocked dependencies."""
        gemini_mock, _, _ = mock_gemini_client
        return CVService(api_key="test_key")

    def test_init_with_api_key(self, mock_gemini_client):
        """Test CVService initialization with API key."""
        # Arrange
        gemini_mock, _, _ = mock_gemini_client

        # Act
        service = CVService(api_key="test_key")

        # Assert
        assert service.api_key == "test_key"
        assert service.client is not None
        # Verify Client was called with API key
        gemini_mock.Client.assert_called_once_with(api_key="test_key")

    def test_analyze_cv_text_success(
        self, cv_service, mock_gemini_client, sample_cv_text, sample_analysis_result
    ):
        """Test successful CV text analysis."""
        # Arrange
        _, mock_client, mock_models = mock_gemini_client

        # Mock the response from Gemini
        mock_response = Mock()
        mock_response.text = json.dumps(sample_analysis_result)
        mock_models.generate_content.return_value = mock_response

        # Act
        result = cv_service.analyze_cv_text(sample_cv_text)

        # Assert
        assert result is not None
        assert "extracted_data" in result
        assert "skills" in result["extracted_data"]
        assert len(result["extracted_data"]["skills"]) == 3
        assert result["extracted_data"]["skills"][0]["name"] == "Python"

        # Verify Gemini was called with correct parameters
        mock_models.generate_content.assert_called_once()
        call_args = mock_models.generate_content.call_args
        assert call_args[1]["model"] == "gemini-2.5-flash"
        assert "Analyze this CV" in call_args[1]["contents"]
        assert sample_cv_text in call_args[1]["contents"]
        # Check config has response_mime_type
        config = call_args[1]["config"]
        assert (
            hasattr(config, "response_mime_type")
            or "response_mime_type" in config.__dict__
        )
        # The actual check depends on how the mock is configured

    def test_analyze_cv_text_empty_input(self, cv_service):
        """Test CV analysis with empty input."""
        # Act & Assert
        with pytest.raises(ValueError, match="CV text cannot be empty"):
            cv_service.analyze_cv_text("")

    def test_analyze_cv_text_api_error(self, cv_service, mock_gemini_client):
        """Test CV analysis when Gemini API fails."""
        # Arrange
        _, mock_client, mock_models = mock_gemini_client
        mock_models.generate_content.side_effect = Exception("API error")

        # Act & Assert
        with pytest.raises(CVProcessingError, match="Failed to analyze CV"):
            cv_service.analyze_cv_text("Sample CV text")

    def test_extract_skills_from_analysis(self, cv_service, sample_analysis_result):
        """Test skill extraction from analysis result."""
        # Act
        skills = cv_service.extract_skills(sample_analysis_result)

        # Assert
        assert len(skills) == 3
        assert skills[0]["name"] == "Python"
        assert skills[0]["level"] == "advanced"
        assert skills[0]["years"] == 5

    def test_extract_experiences_from_analysis(
        self, cv_service, sample_analysis_result
    ):
        """Test experience extraction from analysis result."""
        # Act
        experiences = cv_service.extract_experiences(sample_analysis_result)

        # Assert
        assert len(experiences) == 1
        assert experiences[0]["title"] == "Software Engineer"
        assert experiences[0]["company"] == "Tech Corp"

    def test_validate_cv_analysis_result(self, cv_service):
        """Test validation of CV analysis result structure."""
        # Valid result
        valid_result = {
            "extracted_data": {"skills": [], "experiences": [], "education": []}
        }
        assert cv_service.validate_analysis_result(valid_result) is True

        # Invalid result - missing extracted_data
        invalid_result = {"skills": []}
        assert cv_service.validate_analysis_result(invalid_result) is False

        # Invalid result - extracted_data not a dict
        invalid_result2 = {"extracted_data": "not a dict"}
        assert cv_service.validate_analysis_result(invalid_result2) is False

    @pytest.mark.asyncio
    async def test_process_cv_file_async(
        self, cv_service, mock_gemini_client, sample_cv_text, sample_analysis_result
    ):
        """Test async processing of CV file."""
        # Arrange
        _, mock_client, mock_models = mock_gemini_client
        mock_response = Mock()
        mock_response.text = json.dumps(sample_analysis_result)
        mock_models.generate_content.return_value = mock_response

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(sample_cv_text)
            temp_path = f.name

        try:
            # Act
            result = await cv_service.process_cv_file_async(Path(temp_path))

            # Assert
            assert result is not None
            assert "extracted_data" in result
            mock_models.generate_content.assert_called_once()
        finally:
            # Cleanup
            Path(temp_path).unlink(missing_ok=True)

    def test_calculate_experience_years(self, cv_service):
        """Test calculation of total experience years from analysis."""
        analysis_result = {
            "extracted_data": {
                "skills": [
                    {"name": "Python", "years": 5},
                    {"name": "React", "years": 3},
                ],
                "experiences": [{"duration": "2 years"}, {"duration": "3 years"}],
                "education": [],  # Required field for validation
            }
        }

        # Act
        total_years = cv_service.calculate_total_experience_years(analysis_result)

        # Assert
        assert total_years == 5  # Max of skill years or sum of experience years

    def test_parse_analysis_response_invalid_json(self, cv_service):
        """Test parsing Gemini response with invalid JSON (should try to extract JSON)."""
        # Arrange
        invalid_json_response = 'Some text before {"key": "value"} some text after'

        # Act
        result = cv_service._parse_analysis_response(invalid_json_response)

        # Assert
        assert result == {"key": "value"}

    def test_parse_analysis_response_malformed_json(self, cv_service):
        """Test parsing Gemini response with malformed JSON (should raise error)."""
        # Arrange
        malformed_response = "Not a JSON at all"

        # Act & Assert
        with pytest.raises(
            CVProcessingError, match="Failed to parse analysis response"
        ):
            cv_service._parse_analysis_response(malformed_response)

    def test_parse_analysis_response_with_code_blocks(self, cv_service):
        """Test parsing Gemini response with markdown code blocks."""
        # Arrange
        response_with_blocks = '```json\n{"test": "data"}\n```'

        # Act
        result = cv_service._parse_analysis_response(response_with_blocks)

        # Assert
        assert result == {"test": "data"}

    def test_validate_analysis_result_invalid(self, cv_service):
        """Test validation of invalid analysis result."""
        # Arrange
        invalid_result = {"missing_extracted_data": True}

        # Act
        result = cv_service.validate_analysis_result(invalid_result)

        # Assert
        assert result is False

    def test_extract_skills_empty_analysis(self, cv_service):
        """Test extracting skills from empty analysis."""
        # Arrange
        empty_analysis = {
            "extracted_data": {"skills": [], "experiences": [], "education": []}
        }

        # Act
        skills = cv_service.extract_skills(empty_analysis)

        # Assert
        assert skills == []

    def test_extract_experiences_empty_analysis(self, cv_service):
        """Test extracting experiences from empty analysis."""
        # Arrange
        empty_analysis = {
            "extracted_data": {"skills": [], "experiences": [], "education": []}
        }

        # Act
        experiences = cv_service.extract_experiences(empty_analysis)

        # Assert
        assert experiences == []
