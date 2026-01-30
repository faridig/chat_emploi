"""Unit tests for SQLAlchemy models."""

import pytest
import sqlalchemy.exc
from database.models import (
    AnonymizedProfile,
    Application,
    AuditLog,
    Base,
    ConversationHistory,
    Feedback,
    JobOffer,
    User,
)
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session


@pytest.fixture
def engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    return engine


@pytest.fixture
def session(engine):
    """Create a fresh database session for each test."""
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)


class TestUserModel:
    """Test suite for User model."""

    def test_create_user(self, session):
        """Test creating a basic user."""
        user = User(
            id="user_123",
            settings={"theme": "light"},
            metadata={"os": "linux", "version": "1.0"},
        )
        session.add(user)
        session.commit()

        # Retrieve user
        retrieved = session.get(User, "user_123")
        assert retrieved is not None
        assert retrieved.id == "user_123"
        assert retrieved.settings == {"theme": "light"}
        assert retrieved.metadata["os"] == "linux"
        assert retrieved.created_at is not None
        assert retrieved.last_active is None

    def test_user_relationships(self, session):
        """Test user relationships with other models."""
        user = User(id="user_1")

        # Create related records
        profile = AnonymizedProfile(
            id="profile_1",
            user_id="user_1",
            original_hash="abc123",
            anonymized_path="/path/to/cv.pdf",
            analysis_json={"skills": ["Python"]},
            extracted_data={"skills": []},
        )

        application = Application(id="app_1", user_id="user_1", status="draft")

        conversation = ConversationHistory(
            id="conv_1",
            user_id="user_1",
            session_id="sess_1",
            agent_type="coach",
            message_type="user",
            content="Hello",
            metadata={"tokens": 10},
        )

        feedback = Feedback(
            id="fb_1",
            user_id="user_1",
            item_type="offer",
            item_id="offer_1",
            rating=5,
            comment="Great!",
        )

        session.add_all([user, profile, application, conversation, feedback])
        session.commit()

        # Verify relationships (if we define them as relationships)
        # For now, just verify foreign key constraints work
        retrieved_user = session.get(User, "user_1")
        assert retrieved_user is not None


class TestAnonymizedProfileModel:
    """Test suite for AnonymizedProfile model."""

    def test_create_profile(self, session):
        """Test creating an anonymized profile."""
        profile = AnonymizedProfile(
            id="profile_123",
            user_id="user_123",
            original_hash="sha256:abc123",
            anonymized_path="/data/profiles/profile_123.pdf",
            analysis_json={"skills": ["Python", "React"], "experience_years": 5},
            extracted_data={
                "skills": [{"name": "Python", "level": "advanced", "years": 5}],
                "experiences": [],
                "education": [],
            },
            embedding_vector=b"fake_embedding",
        )
        session.add(profile)
        session.commit()

        retrieved = session.get(AnonymizedProfile, "profile_123")
        assert retrieved is not None
        assert retrieved.user_id == "user_123"
        assert "Python" in retrieved.analysis_json["skills"]
        assert retrieved.embedding_vector == b"fake_embedding"
        assert retrieved.created_at is not None
        assert retrieved.updated_at is None  # not set on creation

    def test_profile_user_relationship(self, session):
        """Test profile belongs to user."""
        user = User(id="user_1")
        profile = AnonymizedProfile(
            id="profile_1",
            user_id="user_1",
            original_hash="hash",
            anonymized_path="/path",
            analysis_json={},
            extracted_data={},
        )
        session.add_all([user, profile])
        session.commit()

        # Test we can query profile via user_id
        stmt = select(AnonymizedProfile).where(AnonymizedProfile.user_id == "user_1")
        result = session.execute(stmt).scalar_one()
        assert result.id == "profile_1"


class TestJobOfferModel:
    """Test suite for JobOffer model."""

    def test_create_job_offer(self, session):
        """Test creating a job offer."""
        import datetime

        offer = JobOffer(
            id="offer_ft_12345",
            source="france_travail",
            raw_data={"title": "Developer", "company": "Tech Corp"},
            title="Développeur Python Senior",
            company="DataTech SA",
            location="Paris (75)",
            contract_type="CDI",
            publication_date=datetime.date(2026, 1, 25),
            description="We need a Python developer...",
            requirements="5+ years Python, React experience",
            embedding_vector=b"fake_embedding",
            expires_at=datetime.datetime(2026, 2, 25),
        )
        session.add(offer)
        session.commit()

        retrieved = session.get(JobOffer, "offer_ft_12345")
        assert retrieved is not None
        assert retrieved.title == "Développeur Python Senior"
        assert retrieved.company == "DataTech SA"
        assert retrieved.source == "france_travail"
        assert retrieved.publication_date.year == 2026
        assert retrieved.fetched_at is not None
        assert retrieved.expires_at is not None


class TestApplicationModel:
    """Test suite for Application model."""

    def test_create_application(self, session):
        """Test creating a job application."""
        import datetime

        # Need user and profile and offer first
        user = User(id="user_1")
        profile = AnonymizedProfile(
            id="profile_1",
            user_id="user_1",
            original_hash="hash",
            anonymized_path="/path",
            analysis_json={},
            extracted_data={},
        )
        offer = JobOffer(
            id="offer_1",
            source="test",
            raw_data={},
            title="Test",
            company="Test",
            location="Paris",
            contract_type="CDI",
            publication_date=datetime.date.today(),
            description="",
            requirements="",
            expires_at=datetime.datetime.now() + datetime.timedelta(days=30),
        )

        application = Application(
            id="app_123",
            user_id="user_1",
            profile_id="profile_1",
            offer_id="offer_1",
            status="applied",
            applied_date=datetime.date.today(),
            cover_letter_path="/letters/letter.pdf",
            notes="Follow up next week",
            interview_date=datetime.datetime(2026, 2, 10, 14, 30),
            reminders={"reminder1": "2026-02-05T10:00:00"},
            metrics={"match_score": 0.85, "letter_quality": 0.92},
        )

        session.add_all([user, profile, offer, application])
        session.commit()

        retrieved = session.get(Application, "app_123")
        assert retrieved is not None
        assert retrieved.status == "applied"
        assert retrieved.applied_date == datetime.date.today()
        assert retrieved.metrics["match_score"] == 0.85
        assert retrieved.interview_date.year == 2026

    def test_application_status_constraint(self, session):
        """Test that status must be one of allowed values."""
        # Create a user first (required foreign key)
        user = User(id="user_1")
        session.add(user)
        session.commit()

        # This should raise an IntegrityError due to CHECK constraint
        application = Application(
            id="app_1",
            user_id="user_1",
            status="invalid_status",  # Invalid status
        )
        session.add(application)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()


class TestConversationHistoryModel:
    """Test suite for ConversationHistory model."""

    def test_create_conversation(self, session):
        """Test creating a conversation entry."""

        conversation = ConversationHistory(
            id="conv_123",
            user_id="user_1",
            session_id="sess_456",
            agent_type="coach",
            message_type="user",
            content="Hello, I need help finding a job",
            metadata={"tokens": 15, "latency": 1.2, "model": "gemini-pro"},
        )
        session.add(conversation)
        session.commit()

        retrieved = session.get(ConversationHistory, "conv_123")
        assert retrieved is not None
        assert retrieved.agent_type == "coach"
        assert retrieved.message_type == "user"
        assert "help" in retrieved.content
        assert retrieved.metadata["tokens"] == 15
        assert retrieved.created_at is not None


class TestFeedbackModel:
    """Test suite for Feedback model."""

    def test_create_feedback(self, session):
        """Test creating feedback."""
        feedback = Feedback(
            id="fb_123",
            user_id="user_1",
            item_type="letter",
            item_id="letter_456",
            rating=4,
            comment="The letter was good but could be more personalized",
            metadata={"context": "generation", "step": "letter_review"},
        )
        session.add(feedback)
        session.commit()

        retrieved = session.get(Feedback, "fb_123")
        assert retrieved is not None
        assert retrieved.rating == 4
        assert retrieved.rating >= 1 and retrieved.rating <= 5
        assert "personalized" in retrieved.comment


class TestAuditLogModel:
    """Test suite for AuditLog model."""

    def test_create_audit_log(self, session):
        """Test creating an audit log entry."""

        log = AuditLog(
            id="audit_123",
            user_id="user_1",
            event_type="cv_upload",
            event_data={"filename": "cv.pdf", "size": 1024},
            ip_address="localhost",
            user_agent="Mozilla/5.0",
        )
        session.add(log)
        session.commit()

        retrieved = session.get(AuditLog, "audit_123")
        assert retrieved is not None
        assert retrieved.event_type == "cv_upload"
        assert retrieved.event_data["filename"] == "cv.pdf"
        assert retrieved.ip_address == "localhost"
        assert retrieved.created_at is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
