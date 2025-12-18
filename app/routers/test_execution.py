from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.test_executor import TestExecutor
from datetime import datetime

router = APIRouter(prefix="/api/execution", tags=["Test Execution"])


def run_tests_background(execution_id: int, test_cases: list, base_url: str,
                         db: Session):
    """Background task to run tests"""
    executor = TestExecutor(base_url)
    results = executor.execute_test_suite(test_cases)

    # Update execution record
    execution = db.query(models.TestExecution).filter(
        models.TestExecution.id == execution_id
    ).first()

    if execution:
        execution.status = "completed"
        execution.total_tests = results["total_tests"]
        execution.passed_tests = results["passed_tests"]
        execution.failed_tests = results["failed_tests"]
        execution.coverage_percentage = results["coverage_percentage"]
        execution.execution_time = results["execution_time"]
        execution.results = results["results"]
        execution.completed_at = datetime.utcnow()
        db.commit()


@router.post("/execute", response_model=schemas.TestExecutionResponse)
def execute_tests(
        request: schemas.ExecuteTestsRequest,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    """Execute a test suite"""

    # Get test suite
    test_suite = db.query(models.TestSuite).filter(
        models.TestSuite.id == request.test_suite_id
    ).first()

    if not test_suite:
        raise HTTPException(status_code=404, detail="Test suite not found")

    # Create execution record
    execution = models.TestExecution(
        test_suite_id=test_suite.id,
        status="running",
        total_tests=len(test_suite.generated_tests),
        passed_tests=0,
        failed_tests=0,
        coverage_percentage=0.0,
        execution_time=0.0,
        results=[]
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)

    # Run tests in background
    background_tasks.add_task(
        run_tests_background,
        execution.id,
        test_suite.generated_tests,
        request.base_url,
        db
    )

    return execution


@router.get("/executions/{execution_id}",
            response_model=schemas.TestExecutionResponse)
def get_execution(execution_id: int, db: Session = Depends(get_db)):
    """Get execution results"""
    execution = db.query(models.TestExecution).filter(
        models.TestExecution.id == execution_id
    ).first()

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    return execution


@router.get("/executions", response_model=list[schemas.TestExecutionResponse])
def list_executions(db: Session = Depends(get_db)):
    """List all test executions"""
    return db.query(models.TestExecution).order_by(
        models.TestExecution.started_at.desc()
    ).limit(50).all()
