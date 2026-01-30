"""CV processing and analysis service.

This service handles CV analysis using Gemini API, extracting structured data
from CV texts and files.
"""

import json
import logging
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types


class CVProcessingError(Exception):
    """Custom exception for CV processing errors."""

    pass


class CVService:
    """Service for CV analysis and processing."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """Initialize CVService with Gemini API configuration.

        Args:
            api_key: Gemini API key
            model_name: Name of the Gemini model to use (default: gemini-2.5-flash)
        """
        self.api_key = api_key
        self.model_name = model_name
        self.client = None

        # Configure Gemini API
        try:
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            logging.error(f"Failed to initialize Gemini client: {e}")
            raise CVProcessingError(f"Failed to initialize Gemini client: {e}")

    def analyze_cv_text(self, cv_text: str) -> dict[str, Any]:
        """Analyze CV text using Gemini API and extract structured data.

        Args:
            cv_text: Text content of the CV

        Returns:
            Dictionary containing extracted data (skills, experiences, education)

        Raises:
            ValueError: If cv_text is empty
            CVProcessingError: If analysis fails
        """
        if not cv_text or not cv_text.strip():
            raise ValueError("CV text cannot be empty")

        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(cv_text)

            # Call Gemini API with structured JSON output
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=self._get_cv_analysis_schema(),
                ),
            )

            # Parse response
            result = self._parse_analysis_response(response.text)

            # Validate result structure
            if not self.validate_analysis_result(result):
                raise CVProcessingError("Invalid analysis result structure")

            return result

        except Exception as e:
            logging.error(f"Failed to analyze CV: {e}")
            raise CVProcessingError(f"Failed to analyze CV: {e}")

    def _create_analysis_prompt(self, cv_text: str) -> str:
        """Create prompt for CV analysis."""
        return f"""Analyze this CV and extract structured information.

        CV Content:
        {cv_text}

        Extract the following information:
        1. Skills with name, level (beginner/intermediate/advanced), and years of experience
        2. Work experiences with title, company, duration, and description
        3. Education with degree, school, and year

        Return the result as structured JSON."""

    def _get_cv_analysis_schema(self) -> dict[str, Any]:
        """Get JSON schema for CV analysis response."""
        return {
            "type": "object",
            "properties": {
                "extracted_data": {
                    "type": "object",
                    "properties": {
                        "skills": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "level": {
                                        "type": "string",
                                        "enum": [
                                            "beginner",
                                            "intermediate",
                                            "advanced",
                                        ],
                                    },
                                    "years": {"type": "number", "minimum": 0},
                                },
                                "required": ["name", "level", "years"],
                            },
                        },
                        "experiences": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "company": {"type": "string"},
                                    "duration": {"type": "string"},
                                    "description": {"type": "string"},
                                },
                                "required": [
                                    "title",
                                    "company",
                                    "duration",
                                    "description",
                                ],
                            },
                        },
                        "education": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "degree": {"type": "string"},
                                    "school": {"type": "string"},
                                    "year": {
                                        "type": "number",
                                        "minimum": 1900,
                                        "maximum": 2100,
                                    },
                                },
                                "required": ["degree", "school", "year"],
                            },
                        },
                    },
                    "required": ["skills", "experiences", "education"],
                }
            },
            "required": ["extracted_data"],
        }

    def _parse_analysis_response(self, response_text: str) -> dict[str, Any]:
        """Parse Gemini response text into structured data.

        Args:
            response_text: Raw text response from Gemini

        Returns:
            Parsed JSON data

        Raises:
            CVProcessingError: If parsing fails
        """
        try:
            # Clean response text - remove markdown code blocks if present
            text = response_text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]

            # Parse JSON
            return json.loads(text)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse Gemini response: {e}")
            # Try to extract JSON from malformed response
            try:
                # Look for JSON-like structure
                start_idx = text.find("{")
                end_idx = text.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = text[start_idx:end_idx]
                    return json.loads(json_str)
            except:
                pass

            raise CVProcessingError(f"Failed to parse analysis response: {e}")

    def validate_analysis_result(self, result: dict[str, Any]) -> bool:
        """Validate the structure of CV analysis result.

        Args:
            result: Analysis result to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(result, dict):
            return False

        if "extracted_data" not in result:
            return False

        extracted = result["extracted_data"]
        if not isinstance(extracted, dict):
            return False

        # Check for required fields (can be empty lists)
        required_fields = {"skills", "experiences", "education"}
        for field in required_fields:
            if field not in extracted:
                return False
            if not isinstance(extracted[field], list):
                return False

        return True

    def extract_skills(self, analysis_result: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract skills from analysis result.

        Args:
            analysis_result: Result from analyze_cv_text

        Returns:
            List of skills
        """
        if not self.validate_analysis_result(analysis_result):
            return []

        return analysis_result["extracted_data"].get("skills", [])

    def extract_experiences(
        self, analysis_result: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Extract work experiences from analysis result.

        Args:
            analysis_result: Result from analyze_cv_text

        Returns:
            List of work experiences
        """
        if not self.validate_analysis_result(analysis_result):
            return []

        return analysis_result["extracted_data"].get("experiences", [])

    def extract_education(
        self, analysis_result: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Extract education from analysis result.

        Args:
            analysis_result: Result from analyze_cv_text

        Returns:
            List of education entries
        """
        if not self.validate_analysis_result(analysis_result):
            return []

        return analysis_result["extracted_data"].get("education", [])

    async def process_cv_file_async(self, file_path: Path) -> dict[str, Any]:
        """Asynchronously process a CV file.

        Args:
            file_path: Path to CV file

        Returns:
            Analysis result

        Raises:
            CVProcessingError: If file processing fails
        """
        try:
            # Read file content (simplified - in production would handle PDF/DOCX)
            text = file_path.read_text(encoding="utf-8", errors="ignore")

            # Analyze text
            return self.analyze_cv_text(text)

        except Exception as e:
            logging.error(f"Failed to process CV file {file_path}: {e}")
            raise CVProcessingError(f"Failed to process CV file: {e}")

    def calculate_total_experience_years(self, analysis_result: dict[str, Any]) -> int:
        """Calculate total years of experience from analysis result.

        Args:
            analysis_result: Result from analyze_cv_text

        Returns:
            Total years of experience (estimated)
        """
        if not self.validate_analysis_result(analysis_result):
            return 0

        extracted = analysis_result["extracted_data"]

        # Method 1: Sum years from skills
        skill_years = 0
        for skill in extracted.get("skills", []):
            if "years" in skill:
                try:
                    skill_years = max(skill_years, int(skill["years"]))
                except (ValueError, TypeError):
                    pass

        # Method 2: Parse duration from experiences
        experience_years = 0
        for exp in extracted.get("experiences", []):
            if "duration" in exp:
                duration = exp["duration"].lower()
                # Simple parsing (e.g., "2 years", "3.5 years")
                for word in duration.split():
                    try:
                        years = float(word)
                        experience_years += years
                        break
                    except ValueError:
                        pass

        # Return the maximum of both methods
        return int(max(skill_years, experience_years))

    def get_cv_summary(self, analysis_result: dict[str, Any]) -> dict[str, Any]:
        """Create a summary of CV analysis.

        Args:
            analysis_result: Result from analyze_cv_text

        Returns:
            Summary dictionary
        """
        if not self.validate_analysis_result(analysis_result):
            return {"error": "Invalid analysis result"}

        extracted = analysis_result["extracted_data"]

        return {
            "total_skills": len(extracted.get("skills", [])),
            "total_experiences": len(extracted.get("experiences", [])),
            "total_education": len(extracted.get("education", [])),
            "estimated_experience_years": self.calculate_total_experience_years(
                analysis_result
            ),
            "primary_skills": [
                skill["name"]
                for skill in extracted.get("skills", [])[:5]
                if "name" in skill
            ],
        }
