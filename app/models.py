from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, \
    ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class APISpec(Base):
    __tablename__ = "api_specs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    spec_content = Column(Text)  # OpenAPI/Swagger JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    test_suites = relationship("TestSuite", back_populates="api_spec")


class TestSuite(Base):
    __tablename__ = "test_suites"

    id = Column(Integer, primary_key=True, index=True)
    api_spec_id = Column(Integer, ForeignKey("api_specs.id"))
    name = Column(String)
    description = Column(Text)
    generated_tests = Column(JSON)  # List of test cases
    created_at = Column(DateTime, default=datetime.utcnow)

    api_spec = relationship("APISpec", back_populates="test_suites")
    executions = relationship("TestExecution", back_populates="test_suite")


class TestExecution(Base):
    __tablename__ = "test_executions"

    id = Column(Integer, primary_key=True, index=True)
    test_suite_id = Column(Integer, ForeignKey("test_suites.id"))
    status = Column(String)  # running, completed, failed
    total_tests = Column(Integer)
    passed_tests = Column(Integer)
    failed_tests = Column(Integer)
    coverage_percentage = Column(Float)
    execution_time = Column(Float)  # seconds
    results = Column(JSON)  # Detailed results
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    test_suite = relationship("TestSuite", back_populates="executions")
