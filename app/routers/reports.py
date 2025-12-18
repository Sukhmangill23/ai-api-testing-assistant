from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/analysis/{execution_id}")
def get_ai_analysis(execution_id: int, db: Session = Depends(get_db)):
    """Get AI-powered analysis of test execution"""

    execution = db.query(models.TestExecution).filter(
        models.TestExecution.id == execution_id
    ).first()

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    if execution.status != "completed":
        raise HTTPException(status_code=400,
                            detail="Execution not yet completed")

    # Get AI analysis
    ai_service = AIService()
    analysis = ai_service.analyze_test_results(execution.results)

    return {
        "execution_id": execution_id,
        "analysis": analysis,
        "execution_summary": {
            "total_tests": execution.total_tests,
            "passed_tests": execution.passed_tests,
            "failed_tests": execution.failed_tests,
            "coverage_percentage": execution.coverage_percentage,
            "execution_time": execution.execution_time
        }
    }


@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""

    total_specs = db.query(models.APISpec).count()
    total_suites = db.query(models.TestSuite).count()
    total_executions = db.query(models.TestExecution).count()

    recent_executions = db.query(models.TestExecution).order_by(
        models.TestExecution.started_at.desc()
    ).limit(10).all()

    avg_coverage = db.query(models.TestExecution).filter(
        models.TestExecution.status == "completed"
    ).with_entities(
        models.TestExecution.coverage_percentage
    ).all()

    avg_coverage_val = sum([c[0] for c in avg_coverage]) / len(
        avg_coverage) if avg_coverage else 0

    return {
        "total_api_specs": total_specs,
        "total_test_suites": total_suites,
        "total_executions": total_executions,
        "average_coverage": round(avg_coverage_val, 2),
        "recent_executions": [
            {
                "id": e.id,
                "test_suite_id": e.test_suite_id,
                "status": e.status,
                "passed_tests": e.passed_tests,
                "failed_tests": e.failed_tests,
                "coverage": e.coverage_percentage,
                "started_at": e.started_at
            }
            for e in recent_executions
        ]
    }
