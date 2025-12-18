from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.test_generator import TestGenerator
import json

router = APIRouter(prefix="/api/generation", tags=["Test Generation"])


@router.post("/specs", response_model=schemas.APISpecResponse)
def create_api_spec(spec: schemas.APISpecCreate, db: Session = Depends(get_db)):
    """Upload an OpenAPI specification"""
    try:
        # Validate it's valid JSON
        json.loads(spec.spec_content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400,
                            detail="Invalid JSON in spec_content")

    db_spec = models.APISpec(
        name=spec.name,
        spec_content=spec.spec_content
    )
    db.add(db_spec)
    db.commit()
    db.refresh(db_spec)
    return db_spec


@router.get("/specs", response_model=list[schemas.APISpecResponse])
def list_api_specs(db: Session = Depends(get_db)):
    """List all uploaded API specifications"""
    return db.query(models.APISpec).all()


@router.post("/generate", response_model=schemas.TestSuiteResponse)
def generate_tests(request: schemas.GenerateTestsRequest,
                   db: Session = Depends(get_db)):
    """Generate test cases for an API specification"""

    # Get the API spec
    api_spec = db.query(models.APISpec).filter(
        models.APISpec.id == request.api_spec_id
    ).first()

    if not api_spec:
        raise HTTPException(status_code=404,
                            detail="API specification not found")

    # Generate tests
    generator = TestGenerator()
    test_cases = generator.generate_tests_for_spec(
        api_spec.spec_content,
        request.include_edge_cases
    )

    if not test_cases:
        raise HTTPException(status_code=500,
                            detail="Failed to generate test cases")

    # Save test suite
    test_suite = models.TestSuite(
        api_spec_id=api_spec.id,
        name=f"Generated Tests for {api_spec.name}",
        description=f"Auto-generated test suite with {len(test_cases)} test cases",
        generated_tests=test_cases
    )
    db.add(test_suite)
    db.commit()
    db.refresh(test_suite)

    return test_suite


@router.get("/suites", response_model=list[schemas.TestSuiteResponse])
def list_test_suites(db: Session = Depends(get_db)):
    """List all test suites"""
    return db.query(models.TestSuite).all()


@router.get("/suites/{suite_id}", response_model=schemas.TestSuiteResponse)
def get_test_suite(suite_id: int, db: Session = Depends(get_db)):
    """Get a specific test suite"""
    suite = db.query(models.TestSuite).filter(
        models.TestSuite.id == suite_id).first()
    if not suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    return suite
