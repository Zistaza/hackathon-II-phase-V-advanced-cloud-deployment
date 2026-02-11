import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..main import app
from ..database import Base
from ..models.container_images import ContainerImage
from ..services.security_scanner import SecurityScanner
import docker
import json

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_security.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test client
client = TestClient(app)

# Security scanner instance
security_scanner = SecurityScanner()

docker_client = docker.from_env()

# Test data
TEST_IMAGE_NAME = "python:3.11-slim"
TEST_DOCKERFILE_CONTENT = """
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
USER nonroot
CMD ['python', 'app.py']
"""

# Test setup and teardown
@pytest.fixture(scope="module")
def test_image():
    """Create a test container image"""
    try:
        # Pull test image if not exists
        try:
            docker_client.images.get(TEST_IMAGE_NAME)
        except docker.errors.ImageNotFound:
            docker_client.images.pull(TEST_IMAGE_NAME)

        yield TEST_IMAGE_NAME
    finally:
        pass  # Cleanup if needed

@pytest.fixture(scope="module")
def test_container_image(test_image, db):
    """Create a test ContainerImage database record"""
    db_image = ContainerImage(
        name=test_image,
        path="/test/path",
        base_image="python:3.11-slim",
        optimization_level="security-first",
        dockerfile_content=TEST_DOCKERFILE_CONTENT,
        image_size=150.0,  # 150MB
        security_score=85.0,
        built_status="success",
        user_id=1
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    yield db_image
    db.delete(db_image)
    db.commit()

# Test Docker security analysis
class TestDockerSecurityAnalysis:
    def test_analyze_dockerfile_security(self, test_container_image):
        """Test Dockerfile security analysis"""
        result = security_scanner.analyze_dockerfile(test_container_image.dockerfile_content)
        assert "analysis completed" in result.lower()
        assert "nonroot" in result.lower()  # Should detect non-root user

    def test_check_security_compliance(self, test_container_image):
        """Test Dockerfile compliance check"""
        result = security_scanner.check_security_compliance(test_container_image.dockerfile_content)
        assert "compliance check completed" in result.lower()
        assert "nonroot" in result.lower()  # Should detect non-root user compliance

    def test_check_for_secrets(self, test_container_image):
        """Test secret detection"""
        image_metadata = docker_client.api.inspect_image(test_container_image.name)
        result = security_scanner.check_for_secrets(image_metadata)
        assert result == False  # Test image shouldn't contain secrets

    def test_analyze_image_layers(self, test_container_image):
        """Test image layer analysis"""
        image_metadata = docker_client.api.inspect_image(test_container_image.name)
        result = security_scanner.analyze_image_layers(image_metadata)
        assert result["total_layers"] > 0
        assert "issues" in result

# Test vulnerability scanning
class TestVulnerabilityScanning:
    def test_scan_vulnerabilities(self, test_container_image):
        """Test vulnerability scanning"""
        vulnerabilities = security_scanner.scan_vulnerabilities(test_container_image.name)
        assert isinstance(vulnerabilities, list)
        for vuln in vulnerabilities:
            assert "vulnerability_id" in vuln
            assert "severity" in vuln
            assert "package_name" in vuln

    def test_generate_vulnerability_report(self, test_container_image):
        """Test vulnerability report generation"""
        report = security_scanner.generate_vulnerability_report(test_container_image.name)
        assert "image_name" in report
        assert "total_vulnerabilities" in report
        assert "risk_score" in report
        assert "vulnerability_details" in report

    def test_calculate_risk_score(self, test_container_image):
        """Test risk score calculation"""
        vulnerabilities = security_scanner.scan_vulnerabilities(test_container_image.name)
        risk_score = security_scanner.calculate_risk_score(vulnerabilities)
        assert 0 <= risk_score <= 100

# Test compliance checking
class TestComplianceChecking:
    def test_check_cis_docker_benchmark(self, test_container_image):
        """Test CIS Docker Benchmark compliance"""
        result = security_scanner.check_cis_docker_benchmark(test_container_image.name)
        assert "standard" in result
        assert "status" in result
        assert "details" in result

    def test_check_nist_800_53(self, test_container_image):
        """Test NIST 800-53 compliance"""
        result = security_scanner.check_nist_800_53(test_container_image.name)
        assert "standard" in result
        assert "status" in result
        assert "details" in result

    def test_check_compliance_multiple_standards(self, test_container_image):
        """Test compliance checking with multiple standards"""
        standards = ["cis-docker-benchmark", "nist-800-53"]
        result = security_scanner.check_compliance(test_container_image.name, standards)
        assert "image_name" in result
        assert "compliance_results" in result
        assert "overall_compliance" in result
        assert len(result["compliance_results"]) == 2

# Test security score calculation
class TestSecurityScoreCalculation:
    def test_calculate_security_score(self, test_container_image):
        """Test security score calculation"""
        scan_results = {
            "vulnerabilities": security_scanner.scan_vulnerabilities(test_container_image.name),
            "secrets_found": False,
            "layer_analysis": security_scanner.analyze_image_layers(
                docker_client.api.inspect_image(test_container_image.name)
            )
        }
        score = security_scanner.calculate_security_score(scan_results)
        assert 0 <= score <= 100

    def test_security_score_with_vulnerabilities(self, test_container_image):
        """Test security score calculation with vulnerabilities"""
        vulnerabilities = security_scanner.scan_vulnerabilities(test_container_image.name)
        # Add some critical vulnerabilities for testing
        critical_vuln = {
            "vulnerability_id": "TEST-001",
            "package_name": "test-package",
            "package_version": "1.0.0",
            "severity": "CRITICAL",
            "description": "Test vulnerability"
        }
        vulnerabilities.append(critical_vuln)

        scan_results = {
            "vulnerabilities": vulnerabilities,
            "secrets_found": False,
            "layer_analysis": security_scanner.analyze_image_layers(
                docker_client.api.inspect_image(test_container_image.name)
            )
        }
        score = security_scanner.calculate_security_score(scan_results)
        assert score < 100  # Should be reduced due to critical vulnerability

# Test helper methods
class TestHelperMethods:
    def test_get_image_metadata(self, test_container_image):
        """Test getting image metadata"""
        metadata = security_scanner.get_image_metadata(test_container_image.name)
        assert "Id" in metadata
        assert "RepoTags" in metadata
        assert "Size" in metadata
        assert "Created" in metadata

    def test_generate_recommendations(self, test_container_image):
        """Test recommendation generation"""
        vulnerabilities = security_scanner.scan_vulnerabilities(test_container_image.name)
        recommendations = security_scanner.generate_recommendations(
            test_container_image.optimization_level,
            vulnerabilities
        )
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        for rec in recommendations:
            assert isinstance(rec, str)

# Integration tests
class TestSecurityScannerIntegration:
    def test_comprehensive_scan(self, test_container_image):
        """Test comprehensive security scan"""
        result = security_scanner.comprehensive_scan(test_container_image.name)
        assert "image_name" in result
        assert "security_score" in result
        assert "vulnerabilities" in result
        assert "secrets_found" in result
        assert "layer_analysis" in result
        assert "scan_type" in result
        assert result["scan_type"] == "comprehensive"

    def test_comprehensive_scan_with_errors(self, test_container_image):
        """Test comprehensive scan with simulated errors"""
        # Simulate error by using invalid image name
        invalid_image_name = "invalid-image-name:123"
        result = security_scanner.comprehensive_scan(invalid_image_name)
        assert "image_name" in result
        assert "error" in result
        assert "scan_type" in result
        assert result["scan_type"] == "comprehensive"

# Performance tests
class TestPerformance:
    def test_scan_performance(self, test_container_image):
        """Test performance of vulnerability scanning"""
        import time
        start_time = time.time()
        vulnerabilities = security_scanner.scan_vulnerabilities(test_container_image.name)
        end_time = time.time()
        duration = end_time - start_time
        assert len(vulnerabilities) >= 0  # Can be 0 if no vulnerabilities
        assert duration < 60  # Should complete within 60 seconds

    def test_comprehensive_scan_performance(self, test_container_image):
        """Test performance of comprehensive scan"""
        import time
        start_time = time.time()
        result = security_scanner.comprehensive_scan(test_container_image.name)
        end_time = time.time()
        duration = end_time - start_time
        assert duration < 120  # Should complete within 120 seconds

# Edge case tests
class TestEdgeCases:
    def test_empty_dockerfile(self):
        """Test analysis with empty Dockerfile"""
        result = security_scanner.analyze_dockerfile("")
        assert "analysis completed" in result.lower()
        assert "issues" in result.lower()

    def test_invalid_image_name(self):
        """Test with invalid image name"""
        result = security_scanner.comprehensive_scan("invalid-image-name")
        assert "error" in result

    def test_no_vulnerabilities(self):
        """Test with image that has no vulnerabilities"""
        # This test may need adjustment based on actual image vulnerabilities
        vulnerabilities = security_scanner.scan_vulnerabilities("alpine:latest")
        assert isinstance(vulnerabilities, list)

# Test setup and teardown functions
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Setup test database"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup after tests
    Base.metadata.drop_all(bind=engine)

def pytest_configure(config):
    """Configure pytest"""
    # Add any global configuration here
    pass

def pytest_unconfigure(config):
    """Unconfigure pytest"""
    # Add any global cleanup here
    pass