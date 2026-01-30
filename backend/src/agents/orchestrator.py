"""
Système d'orchestration d'agents LangGraph pour Chat Emploi.

Ce module implémente un workflow multi-agents avec LangGraph pour orchestrer
les agents spécialisés (coach, researcher, writer, interviewer) selon
les spécifications TECH_SPECS.md.
"""

import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Literal, TypedDict

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph

from src.rag.core import RAGSystem
from src.services.cache.cache_service import CacheService

# Configuration du logging
logger = logging.getLogger(__name__)


# ============================================================================
# Définition des États & Types
# ============================================================================


class UserSessionState(TypedDict):
    """État de session utilisateur pour le workflow LangGraph.

    Conforme aux spécifications TECH_SPECS.md section 2.3.2.
    """

    user_id: str
    current_step: Literal[
        "profile", "search", "selection", "letter", "interview", "tracking"
    ]
    profile_data: dict[str, Any]
    selected_offers: list[dict[str, Any]]
    generated_documents: list[dict[str, Any]]
    conversation_history: list[dict[str, str]]
    session_metrics: dict[str, float]
    # Champs temporaires pour la communication
    user_message: str | None
    error: str | None
    last_agent: str | None


# ============================================================================
# Exceptions Personnalisées
# ============================================================================


class AgentError(Exception):
    """Exception de base pour les erreurs d'agents."""

    def __init__(self, agent_type: str, message: str, details: dict | None = None):
        self.agent_type = agent_type
        self.message = message
        self.details = details or {}
        super().__init__(f"{agent_type} error: {message}")


class SessionNotFoundError(Exception):
    """Exception levée quand une session n'est pas trouvée."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(f"Session not found: {session_id}")


class AgentTimeoutError(Exception):
    """Exception levée quand un agent dépasse le timeout."""

    def __init__(self, agent_type: str, timeout_seconds: int):
        self.agent_type = agent_type
        self.timeout_seconds = timeout_seconds
        super().__init__(f"{agent_type} timeout after {timeout_seconds} seconds")


# ============================================================================
# Agents Spécialisés
# ============================================================================


class BaseAgent:
    """Classe de base pour tous les agents."""

    def __init__(self, llm: ChatGoogleGenerativeAI, agent_type: str):
        self.llm = llm
        self.agent_type = agent_type
        self.logger = logging.getLogger(f"{__name__}.{agent_type}")

    def _log_agent_call(self, state: UserSessionState):
        """Log l'appel à l'agent."""
        self.logger.info(
            f"Agent {self.agent_type} called for user {state.get('user_id', 'unknown')} "
            f"at step {state.get('current_step', 'unknown')}"
        )

    def _handle_error(
        self, error: Exception, state: UserSessionState
    ) -> dict[str, Any]:
        """Gère les erreurs d'agent de manière standardisée."""
        self.logger.error(f"Agent {self.agent_type} error: {error}", exc_info=True)

        return {
            "error": str(error),
            "last_agent": self.agent_type,
            "conversation_history": state.get("conversation_history", [])
            + [
                {
                    "role": "system",
                    "content": f"Désolé, une erreur technique est survenue avec l'agent {self.agent_type}. "
                    f"Veuillez réessayer ou contacter le support.",
                }
            ],
        }


class CoachAgent(BaseAgent):
    """Agent Coach - Analyse de profil et guidance empathique.

    Conforme aux spécifications PRD.md section 5.2.
    """

    def __init__(self, llm: ChatGoogleGenerativeAI):
        super().__init__(llm, "coach")
        self.role = "Career Coach & Profile Analyst"
        self.goal = "Comprendre la situation de l'utilisateur et fournir un accompagnement empathique"
        self.backstory = (
            "Coach de carrière expérimenté avec une formation en psychologie. "
            "Spécialiste de la reconversion professionnelle et de la valorisation des compétences. "
            "Toujours encourageant et réaliste."
        )

        # Prompt pour l'analyse de profil
        self.profile_analysis_prompt = PromptTemplate.from_template(
            """
        Vous êtes un coach de carrière empathique. Analysez la conversation suivante
        pour extraire les informations clés du profil professionnel de l'utilisateur.

        Conversation récente:
        {conversation}

        Message actuel de l'utilisateur:
        {user_message}

        Extrayez les informations suivantes au format JSON:
        1. Compétences techniques mentionnées
        2. Années d'expérience (si mentionnées)
        3. Secteur d'activité
        4. Objectifs professionnels
        5. Points forts identifiés
        6. Domaines d'amélioration potentiels

        Répondez UNIQUEMENT avec un objet JSON valide, sans texte supplémentaire.
        """
        )

        # Prompt pour la réponse empathique
        self.response_prompt = PromptTemplate.from_template(
            """
        Vous êtes {role}. Votre objectif: {goal}

        Votre backstory: {backstory}

        Contexte de l'utilisateur:
        - Profil extrait: {profile_summary}
        - Historique conversation: {conversation_history}

        Message de l'utilisateur: {user_message}

        Répondez de manière:
        1. EMPATHIQUE: Montrez que vous comprenez leur situation
        2. ENCOURAGEANT: Soulignez leurs points forts
        3. PRATIQUE: Proposez des prochaines étapes concrètes
        4. PROFESSIONNEL: Restez dans le cadre du coaching emploi

        Limitez votre réponse à 3-4 phrases maximum.
        """
        )

        self.json_parser = JsonOutputParser()

    def process(self, state: UserSessionState) -> dict[str, Any]:
        """Traite un message utilisateur et met à jour l'état."""
        self._log_agent_call(state)

        try:
            user_message = state.get("user_message") or ""
            conversation_history = state.get("conversation_history", [])

            # 1. Extraire les informations de profil
            profile_info = self._extract_profile_info(
                conversation_history, user_message
            )

            # 2. Générer une réponse empathique
            coach_response = self._generate_response(
                profile_info, conversation_history, user_message
            )

            # 3. Mettre à jour l'état
            updated_state = {
                "profile_data": {**state.get("profile_data", {}), **profile_info},
                "conversation_history": conversation_history
                + [
                    {"role": "user", "content": user_message},
                    {"role": "coach", "content": coach_response},
                ],
                "last_agent": self.agent_type,
                "session_metrics": {
                    **state.get("session_metrics", {}),
                    "coach_interactions": state.get("session_metrics", {}).get(
                        "coach_interactions", 0
                    )
                    + 1,
                },
            }

            # 4. Déterminer la prochaine étape
            if (
                profile_info.get("skills")
                and profile_info.get("experience_years") is not None
            ):
                # Profil suffisamment complet pour passer à la recherche
                updated_state["current_step"] = "search"
                updated_state["conversation_history"].append(
                    {
                        "role": "coach",
                        "content": "Votre profil est maintenant assez complet ! Je vais vous passer à mon collègue spécialiste de la recherche d'offres.",
                    }
                )

            return updated_state

        except Exception as e:
            return self._handle_error(e, state)

    def _extract_profile_info(
        self, conversation: list[dict], user_message: str | None
    ) -> dict[str, Any]:
        """Extrait les informations de profil de la conversation."""
        conversation_text = "\n".join(
            [
                f"{msg['role']}: {msg['content']}"
                for msg in conversation[-5:]  # Derniers 5 messages
            ]
        )

        prompt = self.profile_analysis_prompt.format(
            conversation=conversation_text, user_message=user_message
        )

        response = self.llm.invoke(prompt)
        profile_data = self.json_parser.parse(response.content)

        # Normalisation des données
        normalized = {
            "skills": profile_data.get("compétences techniques mentionnées", []) or [],
            "experience_years": self._parse_experience(
                profile_data.get("années d'expérience", "")
            ),
            "industry": profile_data.get("secteur d'activité", ""),
            "goals": profile_data.get("objectifs professionnels", ""),
            "strengths": profile_data.get("points forts identifiés", []),
            "improvement_areas": profile_data.get(
                "domaines d'amélioration potentiels", []
            ),
        }

        return normalized

    def _parse_experience(self, experience_text: str) -> int | None:
        """Parse le texte d'expérience en nombre d'années."""
        if not experience_text:
            return None

        # Extraction simple des nombres
        import re

        numbers = re.findall(r"\d+", experience_text)
        if numbers:
            return int(numbers[0])
        return None

    def _generate_response(
        self,
        profile_info: dict,
        conversation_history: list[dict],
        user_message: str | None,
    ) -> str:
        """Génère une réponse empathique du coach."""
        profile_summary = self._create_profile_summary(profile_info)

        prompt = self.response_prompt.format(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            profile_summary=profile_summary,
            conversation_history="\n".join(
                [
                    f"{msg['role']}: {msg['content']}"
                    for msg in conversation_history[-3:]
                ]
            ),
            user_message=user_message,
        )

        response = self.llm.invoke(prompt)
        return response.content.strip()

    def _create_profile_summary(self, profile_info: dict) -> str:
        """Crée un résumé lisible du profil."""
        summary_parts = []

        if profile_info.get("skills"):
            summary_parts.append(f"Compétences: {', '.join(profile_info['skills'])}")

        if profile_info.get("experience_years"):
            summary_parts.append(f"Expérience: {profile_info['experience_years']} ans")

        if profile_info.get("industry"):
            summary_parts.append(f"Secteur: {profile_info['industry']}")

        if profile_info.get("goals"):
            summary_parts.append(f"Objectifs: {profile_info['goals']}")

        return (
            "\n".join(summary_parts)
            if summary_parts
            else "Profil en cours de construction"
        )


class ResearcherAgent(BaseAgent):
    """Agent Researcher - Recherche d'offres d'emploi.

    Conforme aux spécifications PRD.md section 5.3.
    """

    def __init__(
        self, llm: ChatGoogleGenerativeAI, rag_system: RAGSystem | None = None
    ):
        super().__init__(llm, "researcher")
        self.role = "Job Market Research Specialist"
        self.goal = "Trouver des opportunités d'emploi pertinentes basées sur le profil"
        self.backstory = (
            "Chercheur data-driven avec une connaissance approfondie du marché du travail. "
            "Spécialiste des tendances d'emploi et des algorithmes de matching. "
            "Toujours à la recherche des meilleures opportunités."
        )

        self.rag_system = rag_system
        self.cache_service = CacheService()
        self.json_parser = JsonOutputParser()

        # Prompt pour l'analyse des résultats
        self.analysis_prompt = PromptTemplate.from_template(
            """
        Vous êtes un spécialiste de la recherche d'emploi. Analysez les offres matching
        et expliquez pourquoi elles correspondent au profil.

        Profil utilisateur:
        {profile_summary}

        Offres trouvées (score de matching):
        {offers_summary}

        Pour chaque offre, fournissez:
        1. Une explication concise du matching (max 2 phrases)
        2. Les points forts de la correspondance
        3. Les éventuelles lacunes à combler

        Répondez au format JSON avec une liste d'explications.
        """
        )

    def process(self, state: UserSessionState) -> dict[str, Any]:
        """Recherche des offres d'emploi pertinentes."""
        self._log_agent_call(state)

        try:
            profile_data = state.get("profile_data", {})

            # 1. Vérifier le cache
            cache_key = f"offers:{self._create_profile_hash(profile_data)}"
            cached_offers = self.cache_service.get(cache_key)

            if cached_offers:
                self.logger.info("Using cached offers")
                offers = cached_offers
            else:
                # 2. Rechercher avec le système RAG
                offers = self._search_offers(profile_data)

                # 3. Mettre en cache pour 24h
                self.cache_service.set(cache_key, offers, ttl_seconds=86400)

            # 4. Analyser et expliquer les résultats
            analyzed_offers = self._analyze_offers(offers, profile_data)

            # 5. Mettre à jour l'état
            updated_state = {
                "selected_offers": analyzed_offers,
                "current_step": "selection",
                "last_agent": self.agent_type,
                "session_metrics": {
                    **state.get("session_metrics", {}),
                    "offers_found": len(analyzed_offers),
                    "avg_match_score": sum(
                        o.get("match_score", 0) for o in analyzed_offers
                    )
                    / max(len(analyzed_offers), 1),
                },
                "conversation_history": state.get("conversation_history", [])
                + [
                    {
                        "role": "researcher",
                        "content": f"J'ai trouvé {len(analyzed_offers)} offres qui pourraient vous correspondre ! "
                        f"La meilleure correspondance est à {analyzed_offers[0].get('match_score', 0)*100:.0f}%.",
                    }
                ],
            }

            return updated_state

        except Exception as e:
            return self._handle_error(e, state)

    def _create_profile_hash(self, profile_data: dict) -> str:
        """Crée un hash pour le cache basé sur le profil."""
        import hashlib

        profile_str = json.dumps(profile_data, sort_keys=True)
        return hashlib.md5(profile_str.encode()).hexdigest()

    def _search_offers(self, profile_data: dict) -> list[dict[str, Any]]:
        """Recherche des offres avec le système RAG."""
        if not self.rag_system:
            self.logger.warning("RAG system not initialized, returning mock data")
            return self._get_mock_offers(profile_data)

        # Créer un profil CV pour le matching
        # Créer un ID unique pour le profil
        import hashlib

        from src.rag.core import CVProfile

        profile_hash = hashlib.md5(
            json.dumps(profile_data, sort_keys=True).encode()
        ).hexdigest()

        cv_profile = CVProfile(
            id=f"profile_{profile_hash}",
            skills=profile_data.get("skills", []),
            experiences=[],  # À compléter avec les données réelles
            education=[],  # À compléter avec les données réelles
            summary=f"Profil avec {len(profile_data.get('skills', []))} compétences",
        )

        # Rechercher les offres matching
        matches = self.rag_system.match_cv_with_jobs(cv_profile, max_results=10)

        # Convertir en format standard
        offers = []
        for match in matches:
            job_offer = match.job_offer
            offers.append(
                {
                    "offer_id": job_offer.id,
                    "match_score": match.similarity_score,
                    "explanation": match.explanation
                    or f"Matching basé sur {len(match.matching_skills)} compétences communes",
                    "offer_details": {
                        "title": job_offer.title,
                        "company": job_offer.company,
                        "location": job_offer.location,
                        "contract": job_offer.experience_level,  # Utiliser experience_level comme proxy pour contract
                        "description": (
                            job_offer.description[:200] + "..."
                            if job_offer.description
                            else ""
                        ),
                    },
                }
            )

        return offers

    def _analyze_offers(self, offers: list[dict], profile_data: dict) -> list[dict]:
        """Analyse et enrichit les offres avec des explications."""
        if not offers:
            return []

        # Trier par score de matching
        sorted_offers = sorted(
            offers, key=lambda x: x.get("match_score", 0), reverse=True
        )

        # Prendre les 5 meilleures
        top_offers = sorted_offers[:5]

        # Générer des explications détaillées
        profile_summary = self._create_profile_summary(profile_data)
        offers_summary = "\n".join(
            [
                f"- {o['offer_details']['title']} chez {o['offer_details']['company']} ({o['match_score']*100:.0f}%)"
                for o in top_offers
            ]
        )

        prompt = self.analysis_prompt.format(
            profile_summary=profile_summary, offers_summary=offers_summary
        )

        response = self.llm.invoke(prompt)

        try:
            explanations = self.json_parser.parse(response.content)

            # Fusionner les explications avec les offres
            for i, offer in enumerate(top_offers):
                if i < len(explanations):
                    offer["detailed_explanation"] = explanations[i]

        except Exception as e:
            self.logger.warning(f"Failed to parse explanations: {e}")
            for offer in top_offers:
                offer["detailed_explanation"] = {
                    "explanation": offer.get(
                        "explanation", "Correspondance basée sur le profil"
                    ),
                    "strengths": ["Matching algorithmique"],
                    "gaps": [],
                }

        return top_offers

    def _get_mock_offers(self, profile_data: dict) -> list[dict[str, Any]]:
        """Retourne des offres mock pour le développement."""
        skills = profile_data.get("skills", [])
        mock_offers = []

        for i in range(5):
            skill = skills[i % len(skills)] if skills else "Python"
            mock_offers.append(
                {
                    "offer_id": f"mock_offer_{i}",
                    "match_score": 0.7 + (i * 0.05),
                    "explanation": f"Correspondance basée sur vos compétences en {skill}",
                    "offer_details": {
                        "title": f"Développeur {skill}",
                        "company": f"Entreprise Tech {i+1}",
                        "location": "Paris",
                        "contract": "CDI",
                        "description": f"Poste de développeur {skill} avec opportunités d'évolution.",
                    },
                }
            )

        return mock_offers

    def _create_profile_summary(self, profile_data: dict) -> str:
        """Crée un résumé du profil pour l'analyse."""
        parts = []

        if skills := profile_data.get("skills"):
            parts.append(f"Compétences: {', '.join(skills[:5])}")

        if exp := profile_data.get("experience_years"):
            parts.append(f"Expérience: {exp} ans")

        if industry := profile_data.get("industry"):
            parts.append(f"Secteur: {industry}")

        return "\n".join(parts)


class WriterAgent(BaseAgent):
    """Agent Writer - Génération de lettres de motivation.

    Conforme aux spécifications PRD.md section 5.4.
    """

    def __init__(self, llm: ChatGoogleGenerativeAI):
        super().__init__(llm, "writer")
        self.role = "Motivation Letter Specialist"
        self.goal = "Créer des lettres de motivation personnalisées et persuasives"
        self.backstory = (
            "Écrivain professionnel avec expérience en RH et recrutement. "
            "Spécialiste de la valorisation des compétences et de l'adaptation aux offres. "
            "Maîtrise parfaite des codes professionnels français."
        )

        # Template de lettre de motivation
        self.letter_template = PromptTemplate.from_template(
            """
        Vous êtes {role}. Votre objectif: {goal}

        Votre backstory: {backstory}

        CONTEXTE:
        - Profil candidat: {profile_summary}
        - Offre d'emploi: {offer_details}
        - Ton souhaité: {tone} (1=formel, 5=enthousiaste)

        GÉNÉREZ une lettre de motivation professionnelle en français avec:
        1. Objet: Poste de {job_title} - {candidate_name}
        2. Formule d'appel: Madame, Monsieur,
        3. Introduction: Présentation brève + motivation pour le poste
        4. Paragraphe 1: Adéquation compétences/exigences
        5. Paragraphe 2: Expérience pertinente + réalisations
        6. Paragraphe 3: Motivation pour l'entreprise
        7. Conclusion: Disponibilité + formule de politesse
        8. Signature: {candidate_name}

        IMPORTANT:
        - Longueur: 300-400 mots
        - Ton: {tone_description}
        - Inclure des éléments spécifiques du profil: {profile_highlights}
        - Personnaliser pour l'entreprise: {company_specifics}

        Répondez UNIQUEMENT avec le texte de la lettre, sans commentaires.
        """
        )

    def process(self, state: UserSessionState) -> dict[str, Any]:
        """Génère une lettre de motivation pour l'offre sélectionnée."""
        self._log_agent_call(state)

        try:
            profile_data = state.get("profile_data", {})
            selected_offers = state.get("selected_offers", [])

            if not selected_offers:
                raise AgentError(
                    self.agent_type, "Aucune offre sélectionnée pour générer une lettre"
                )

            # Prendre la première offre (la mieux matching)
            target_offer = selected_offers[0]

            # Générer la lettre
            letter_content = self._generate_letter(profile_data, target_offer)

            # Créer le document
            document = {
                "document_id": str(uuid.uuid4()),
                "type": "cover_letter",
                "offer_id": target_offer.get("offer_id"),
                "content": letter_content,
                "metadata": {
                    "word_count": len(letter_content.split()),
                    "generated_at": datetime.now().isoformat(),
                    "offer_title": target_offer.get("offer_details", {}).get("title"),
                    "company": target_offer.get("offer_details", {}).get("company"),
                    "match_score": target_offer.get("match_score", 0),
                },
            }

            # Mettre à jour l'état
            updated_state = {
                "generated_documents": state.get("generated_documents", [])
                + [document],
                "current_step": "interview",
                "last_agent": self.agent_type,
                "session_metrics": {
                    **state.get("session_metrics", {}),
                    "letters_generated": state.get("session_metrics", {}).get(
                        "letters_generated", 0
                    )
                    + 1,
                },
                "conversation_history": state.get("conversation_history", [])
                + [
                    {
                        "role": "writer",
                        "content": f"Lettre de motivation générée pour le poste de "
                        f"{target_offer.get('offer_details', {}).get('title')} ! "
                        f"Elle met en valeur vos {len(profile_data.get('skills', []))} compétences clés.",
                    }
                ],
            }

            return updated_state

        except Exception as e:
            return self._handle_error(e, state)

    def _generate_letter(self, profile_data: dict, offer: dict) -> str:
        """Génère le contenu de la lettre de motivation."""
        # Préparer les données pour le template
        profile_summary = self._create_profile_summary(profile_data)
        offer_details = self._create_offer_summary(offer)

        # Déterminer le ton (basé sur le type d'entreprise)
        tone, tone_description = self._determine_tone(offer)

        # Points forts à mettre en avant
        profile_highlights = self._extract_highlights(profile_data, offer)

        # Éléments spécifiques à l'entreprise
        company_specifics = self._extract_company_specifics(offer)

        prompt = self.letter_template.format(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            profile_summary=profile_summary,
            offer_details=offer_details,
            job_title=offer.get("offer_details", {}).get("title", "le poste"),
            candidate_name="[Nom du candidat]",  # À remplacer par l'utilisateur
            tone=tone,
            tone_description=tone_description,
            profile_highlights=profile_highlights,
            company_specifics=company_specifics,
        )

        response = self.llm.invoke(prompt)
        return response.content.strip()

    def _create_profile_summary(self, profile_data: dict) -> str:
        """Crée un résumé du profil pour la lettre."""
        parts = []

        if skills := profile_data.get("skills"):
            parts.append(f"Compétences principales: {', '.join(skills[:3])}")

        if exp := profile_data.get("experience_years"):
            parts.append(f"Expérience: {exp} ans dans le secteur")

        if strengths := profile_data.get("strengths"):
            parts.append(f"Points forts: {', '.join(strengths[:2])}")

        return "\n".join(parts)

    def _create_offer_summary(self, offer: dict) -> str:
        """Crée un résumé de l'offre."""
        details = offer.get("offer_details", {})

        summary = f"Poste: {details.get('title', 'Non spécifié')}\n"
        summary += f"Entreprise: {details.get('company', 'Non spécifiée')}\n"
        summary += f"Localisation: {details.get('location', 'Non spécifiée')}\n"
        summary += f"Type de contrat: {details.get('contract', 'Non spécifié')}\n"

        if description := details.get("description"):
            summary += f"Description: {description[:150]}..."

        return summary

    def _determine_tone(self, offer: dict) -> tuple[int, str]:
        """Détermine le ton approprié pour la lettre."""
        company = offer.get("offer_details", {}).get("company", "").lower()

        # Startup vs Grand groupe vs Institution
        if any(word in company for word in ["startup", "scaleup", "tech", "innov"]):
            return 4, "enthousiaste et dynamique"
        elif any(word in company for word in ["société", "groupe", "corp", "sa"]):
            return 3, "professionnel et engagé"
        elif any(
            word in company
            for word in ["administration", "public", "état", "ministère"]
        ):
            return 2, "formel et respectueux"
        else:
            return 3, "professionnel et motivé"

    def _extract_highlights(self, profile_data: dict, offer: dict) -> str:
        """Extrait les points forts à mettre en avant."""
        offer_title = offer.get("offer_details", {}).get("title", "").lower()
        profile_skills = profile_data.get("skills", [])

        # Trouver les compétences correspondantes
        matching_skills = []
        for skill in profile_skills:
            if any(keyword in offer_title for keyword in skill.lower().split()):
                matching_skills.append(skill)

        if matching_skills:
            return (
                f"Compétences directement pertinentes: {', '.join(matching_skills[:3])}"
            )
        elif profile_skills:
            return f"Compétences transférables: {', '.join(profile_skills[:3])}"
        else:
            return "Expérience et motivation"

    def _extract_company_specifics(self, offer: dict) -> str:
        """Extrait des éléments spécifiques à l'entreprise."""
        company = offer.get("offer_details", {}).get("company", "")

        if not company:
            return "votre entreprise"

        # Phrases génériques adaptables
        specifics = [
            f"les valeurs et la culture de {company}",
            f"les projets innovants de {company}",
            f"la réputation d'excellence de {company}",
            f"le secteur d'activité de {company}",
            f"la vision stratégique de {company}",
        ]

        return specifics[hash(company) % len(specifics)]


class InterviewCoachAgent(BaseAgent):
    """Agent Interview Coach - Préparation aux entretiens.

    Conforme aux spécifications PRD.md section 4.2 (Should Have).
    """

    def __init__(self, llm: ChatGoogleGenerativeAI):
        super().__init__(llm, "interview_coach")
        self.role = "Interview Preparation Expert"
        self.goal = (
            "Préparer l'utilisateur aux entretiens avec des simulations personnalisées"
        )
        self.backstory = (
            "Ancien responsable RH avec plus de 1000 entretiens conduits. "
            "Spécialiste de la préparation aux entretiens techniques et comportementaux. "
            "Expert en détection du stress et en techniques de communication."
        )

        # Prompt pour les questions d'entretien
        self.questions_prompt = PromptTemplate.from_template(
            """
        Vous êtes un coach d'entretien expert. Générez des questions d'entretien
        personnalisées basées sur le profil et l'offre.

        Profil candidat:
        {profile_summary}

        Offre d'emploi:
        {offer_summary}

        Générez 5 questions d'entretien:
        1. Une question technique spécifique au poste
        2. Une question comportementale sur l'expérience
        3. Une question sur la motivation pour l'entreprise
        4. Une question sur les défis/échecs
        5. Une question sur les objectifs de carrière

        Pour chaque question, incluez:
        - La question
        - Ce que le recruteur cherche à évaluer
        - Des éléments de réponse suggérés

        Répondez au format JSON.
        """
        )

        # Prompt pour le feedback
        self.feedback_prompt = PromptTemplate.from_template(
            """
        Analysez cette réponse à une question d'entretien:

        Question: {question}
        Réponse de l'utilisateur: {user_response}

        Fournissez un feedback constructif:
        1. Points forts de la réponse
        2. Points à améliorer
        3. Suggestions concrètes
        4. Score sur 10

        Répondez au format JSON.
        """
        )

        self.json_parser = JsonOutputParser()

    def process(self, state: UserSessionState) -> dict[str, Any]:
        """Prépare l'utilisateur pour un entretien."""
        self._log_agent_call(state)

        try:
            profile_data = state.get("profile_data", {})
            selected_offers = state.get("selected_offers", [])

            if not selected_offers:
                raise AgentError(
                    self.agent_type,
                    "Aucune offre sélectionnée pour la préparation d'entretien",
                )

            target_offer = selected_offers[0]

            # Générer les questions d'entretien
            interview_questions = self._generate_questions(profile_data, target_offer)

            # Créer le document de préparation
            preparation_doc = {
                "document_id": str(uuid.uuid4()),
                "type": "interview_preparation",
                "offer_id": target_offer.get("offer_id"),
                "content": interview_questions,
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "offer_title": target_offer.get("offer_details", {}).get("title"),
                    "company": target_offer.get("offer_details", {}).get("company"),
                    "question_count": len(interview_questions.get("questions", [])),
                },
            }

            # Mettre à jour l'état
            updated_state = {
                "generated_documents": state.get("generated_documents", [])
                + [preparation_doc],
                "current_step": "tracking",
                "last_agent": self.agent_type,
                "session_metrics": {
                    **state.get("session_metrics", {}),
                    "interview_preparations": state.get("session_metrics", {}).get(
                        "interview_preparations", 0
                    )
                    + 1,
                },
                "conversation_history": state.get("conversation_history", [])
                + [
                    {
                        "role": "interview_coach",
                        "content": f"Préparation d'entretien générée avec {len(interview_questions.get('questions', []))} questions ! "
                        f"Vous êtes prêt pour l'entretien chez {target_offer.get('offer_details', {}).get('company')}.",
                    }
                ],
            }

            return updated_state

        except Exception as e:
            return self._handle_error(e, state)

    def _generate_questions(self, profile_data: dict, offer: dict) -> dict[str, Any]:
        """Génère des questions d'entretien personnalisées."""
        profile_summary = self._create_profile_summary(profile_data)
        offer_summary = self._create_offer_summary(offer)

        prompt = self.questions_prompt.format(
            profile_summary=profile_summary, offer_summary=offer_summary
        )

        response = self.llm.invoke(prompt)

        try:
            questions_data = self.json_parser.parse(response.content)

            # Ajouter des conseils généraux
            preparation_guide = {
                "questions": questions_data,
                "general_advice": [
                    "Arrivez 10 minutes en avance",
                    "Préparez 2-3 questions à poser au recruteur",
                    "Habillez-vous professionnellement",
                    "Maintenez un contact visuel",
                    "Soyez concis dans vos réponses (1-2 minutes max)",
                ],
                "company_research_tips": [
                    f"Visitez le site web de {offer.get('offer_details', {}).get('company')}",
                    "Recherchez les actualités récentes de l'entreprise",
                    "Consultez les avis sur Glassdoor ou LinkedIn",
                    "Identifiez les valeurs et la culture d'entreprise",
                ],
            }

            return preparation_guide

        except Exception as e:
            self.logger.warning(f"Failed to parse interview questions: {e}")

            # Questions par défaut
            return {
                "questions": [
                    {
                        "question": "Parlez-moi de votre expérience professionnelle",
                        "what_to_assess": "Clarté, pertinence, capacité de synthèse",
                        "suggested_elements": "Focus sur les expériences liées au poste",
                    }
                ],
                "general_advice": ["Soyez vous-même et préparez-vous bien"],
                "company_research_tips": ["Renseignez-vous sur l'entreprise"],
            }

    def _create_profile_summary(self, profile_data: dict) -> str:
        """Crée un résumé pour les questions d'entretien."""
        parts = []

        if skills := profile_data.get("skills"):
            parts.append(f"Compétences: {', '.join(skills)}")

        if exp := profile_data.get("experience_years"):
            parts.append(f"Expérience: {exp} ans")

        if industry := profile_data.get("industry"):
            parts.append(f"Secteur: {industry}")

        if goals := profile_data.get("goals"):
            parts.append(f"Objectifs: {goals}")

        return "\n".join(parts)

    def _create_offer_summary(self, offer: dict) -> str:
        """Crée un résumé de l'offre pour les questions d'entretien."""
        details = offer.get("offer_details", {})

        summary = f"Poste: {details.get('title', 'Non spécifié')}\n"
        summary += f"Entreprise: {details.get('company', 'Non spécifiée')}\n"
        summary += f"Secteur: {details.get('industry', 'Non spécifié')}\n"

        if description := details.get("description"):
            summary += f"Description: {description[:100]}..."

        return summary


class AgentOrchestrator:
    """Orchestrateur principal pour gérer les sessions et exécuter le workflow.

    Conforme aux spécifications TECH_SPECS.md section 2.3.
    """

    def __init__(
        self, gemini_api_key: str, session_persistence_path: str | None = None
    ):
        self.gemini_api_key = gemini_api_key
        self.session_persistence_path = session_persistence_path or os.path.join(
            os.path.expanduser("~"), ".chat_emploi", "sessions"
        )

        # Initialiser le LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=gemini_api_key,
            temperature=0.7,
            max_output_tokens=2048,
        )

        # Initialiser les agents
        self.coach_agent = CoachAgent(self.llm)
        self.researcher_agent = ResearcherAgent(
            self.llm, rag_system=None
        )  # RAG system sera injecté
        self.writer_agent = WriterAgent(self.llm)
        self.interview_coach_agent = InterviewCoachAgent(self.llm)

        # Sessions en mémoire
        self.sessions: dict[str, dict] = {}

        # Construire le graphe de workflow
        self.workflow_graph = self._build_workflow_graph()

    def _build_workflow_graph(self):
        """Construit le graphe de workflow LangGraph."""
        builder = StateGraph(UserSessionState)

        # Ajouter les nodes (agents)
        builder.add_node("coach", self.coach_agent.process)
        builder.add_node("researcher", self.researcher_agent.process)
        builder.add_node("writer", self.writer_agent.process)
        builder.add_node("interview_coach", self.interview_coach_agent.process)

        # Définir la logique de routing conditionnel
        def route_based_on_step(state: UserSessionState) -> str:
            """Route vers le bon agent basé sur l'étape actuelle."""
            current_step = state.get("current_step", "profile")

            routing_map = {
                "profile": "coach",
                "search": "researcher",
                "selection": "researcher",  # Même agent pour search et selection
                "letter": "writer",
                "interview": "interview_coach",
                "tracking": END,
            }

            return routing_map.get(current_step, "coach")

        # Ajouter les edges conditionnels
        builder.add_conditional_edges(
            START,
            route_based_on_step,
            {
                "coach": "coach",
                "researcher": "researcher",
                "writer": "writer",
                "interview_coach": "interview_coach",
                END: END,
            },
        )

        # Ajouter les edges entre agents
        builder.add_edge("coach", "researcher")
        builder.add_edge("researcher", "writer")
        builder.add_edge("writer", "interview_coach")
        builder.add_edge("interview_coach", END)

        # Compiler le graphe
        return builder.compile()

    def create_session(self, user_id: str) -> str:
        """Crée une nouvelle session utilisateur."""
        session_id = str(uuid.uuid4())

        self.sessions[session_id] = {
            "user_id": user_id,
            "current_step": "profile",
            "profile_data": {},
            "selected_offers": [],
            "generated_documents": [],
            "conversation_history": [],
            "session_metrics": {
                "created_at": datetime.now().isoformat(),
                "coach_interactions": 0,
                "offers_found": 0,
                "letters_generated": 0,
                "interview_preparations": 0,
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        logger.info(f"Created new session {session_id} for user {user_id}")
        return session_id

    def get_session(self, session_id: str) -> dict:
        """Récupère une session par son ID."""
        if session_id not in self.sessions:
            raise SessionNotFoundError(session_id)

        return self.sessions[session_id]

    def update_session_step(self, session_id: str, step: str):
        """Met à jour l'étape de progression d'une session."""
        session = self.get_session(session_id)
        session["current_step"] = step
        session["updated_at"] = datetime.now().isoformat()

    def execute_workflow(self, session_id: str, user_message: str) -> dict[str, Any]:
        """Exécute le workflow pour une session avec un message utilisateur."""
        session = self.get_session(session_id)

        # Préparer l'état initial
        initial_state = {
            "user_id": session["user_id"],
            "current_step": session["current_step"],
            "profile_data": session["profile_data"],
            "selected_offers": session["selected_offers"],
            "generated_documents": session["generated_documents"],
            "conversation_history": session["conversation_history"],
            "session_metrics": session["session_metrics"],
            "user_message": user_message,
            "error": None,
            "last_agent": None,
        }

        try:
            # Exécuter le workflow
            result = self.workflow_graph.invoke(initial_state)  # type: ignore

            # Mettre à jour la session
            session.update(
                {
                    "current_step": result.get("current_step", session["current_step"]),
                    "profile_data": result.get("profile_data", session["profile_data"]),
                    "selected_offers": result.get(
                        "selected_offers", session["selected_offers"]
                    ),
                    "generated_documents": result.get(
                        "generated_documents", session["generated_documents"]
                    ),
                    "conversation_history": result.get(
                        "conversation_history", session["conversation_history"]
                    ),
                    "session_metrics": result.get(
                        "session_metrics", session["session_metrics"]
                    ),
                    "updated_at": datetime.now().isoformat(),
                }
            )

            return result

        except Exception as e:
            logger.error(f"Workflow execution failed for session {session_id}: {e}")

            # Enregistrer l'erreur dans la session
            session["error"] = str(e)
            session["updated_at"] = datetime.now().isoformat()

            raise AgentError("orchestrator", f"Workflow execution failed: {e}") from e

    def save_session(self, session_id: str):
        """Sauvegarde une session sur le disque."""
        session = self.get_session(session_id)

        # Créer le dossier de sauvegarde si nécessaire
        os.makedirs(self.session_persistence_path, exist_ok=True)

        # Sauvegarder la session
        session_file = os.path.join(self.session_persistence_path, f"{session_id}.json")
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved session {session_id} to {session_file}")

    def load_session(self, session_id: str):
        """Charge une session depuis le disque."""
        session_file = os.path.join(self.session_persistence_path, f"{session_id}.json")

        if not os.path.exists(session_file):
            raise SessionNotFoundError(session_id)

        with open(session_file, encoding="utf-8") as f:
            session = json.load(f)

        self.sessions[session_id] = session
        logger.info(f"Loaded session {session_id} from {session_file}")

    def set_rag_system(self, rag_system: RAGSystem):
        """Injecte le système RAG dans l'agent researcher."""
        self.researcher_agent.rag_system = rag_system
