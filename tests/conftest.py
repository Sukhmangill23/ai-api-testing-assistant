import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app import models


@pytest.fixture(scope="function")
def test_db():
    """Create a test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False,
                                    bind=engine)
    db = TestSessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_api_spec(test_db):
    """Create a sample API spec in database"""
    spec = models.APISpec(
        name="Test API",
        spec_content='{"openapi": "3.0.0", "paths": {}}'
    )
    test_db.add(spec)
    test_db.commit()
    test_db.refresh(spec)
    return spec


@pytest.fixture
def sample_test_suite(test_db, sample_api_spec):
    """Create a sample test suite"""
    suite = models.TestSuite(
        api_spec_id=sample_api_spec.id,
        name="Test Suite",
        description="Sample test suite",
        generated_tests=[
            {
                "name": "Test 1",
                "method": "GET",
                "endpoint": "/test",
                "expected_status": 200
            }
        ]
    )
    test_db.add(suite)
    test_db.commit()
    test_db.refresh(suite)
    return suite
