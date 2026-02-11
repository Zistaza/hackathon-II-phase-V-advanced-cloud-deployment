from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
import docker
from docker.types import Mount
from pydantic import BaseModel

from ..database import get_db
from ..models.container_images import ContainerImage, ContainerImageCreate, ContainerImageUpdate
from ..services.auth_service import get_current_user
from ..services.docker_ai_service import DockerAIService
from ..services.security_scanner import SecurityScanner

router = APIRouter(prefix="/api/container-images", tags=["container-images"])
security = HTTPBearer()

class ValidationResult(BaseModel):
    dockerfile_analysis: str
    security_best_practices: str
    vulnerability_scan: str
    optimization_score: str
    recommendations: List[str] = []

class HealthCheckResult(BaseModel):
    image_exists: bool
    size: Optional[float]
    last_built: Optional[datetime]
    status: str
    security_compliance: str
    vulnerabilities: Optional[int]
    registry_status: Optional[str]

@router.post("/{image_id}:validate", response_model=ValidationResult)
def validate_container_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Validate container image security and configuration
    """
    image = db.query(ContainerImage).filter(
        ContainerImage.id == image_id,
        ContainerImage.user_id == current_user["user_id"]
    ).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container image not found"
        )

    try:
        # Perform security validation using SecurityScanner
        scanner = SecurityScanner()

        # Analyze Dockerfile content
        dockerfile_analysis = scanner.analyze_dockerfile(image.dockerfile_content)

        # Check security best practices
        security_compliance = scanner.check_security_compliance(image.dockerfile_content)

        # Scan for vulnerabilities
        vulnerabilities = scanner.scan_vulnerabilities(image.base_image)

        # Generate recommendations
        recommendations = scanner.generate_recommendations(
            image.optimization_level,
            vulnerabilities
        )

        # Calculate security score
        security_score = 85  # Placeholder - would be calculated based on scan results
        image.security_score = security_score
        db.commit()

        validation_result = {
            "dockerfile_analysis": dockerfile_analysis,
            "security_best_practices": security_compliance,
            "vulnerability_scan": "none_detected" if len(vulnerabilities) == 0 else "vulnerabilities_found",
            "optimization_score": image.optimization_level,
            "recommendations": recommendations
        }

        return validation_result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate container image: {str(e)}"
        )

@router.post("/{image_id}:health-check", response_model=HealthCheckResult)
def health_check_container_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Perform health check on container image
    """
    image = db.query(ContainerImage).filter(
        ContainerImage.id == image_id,
        ContainerImage.user_id == current_user["user_id"]
    ).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container image not found"
        )

    try:
        # Check if image exists in Docker registry
        client = docker.from_env()
        try:
            client.images.get(image.name)
            image_exists = True
        except docker.errors.ImageNotFound:
            image_exists = False

        # Check for vulnerabilities if image exists
        vulnerabilities = 0
        if image_exists:
            scanner = SecurityScanner()
            vulnerabilities = len(scanner.scan_vulnerabilities(image.name))

        health_status = {
            "image_exists": image_exists,
            "size": image.image_size,
            "last_built": image.built_at,
            "status": "healthy" if image_exists else "missing",
            "security_compliance": "compliant" if image.security_score >= 80 else "non_compliant",
            "vulnerabilities": vulnerabilities,
            "registry_status": "available" if image_exists else "not_found"
        }

        return health_status

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform health check: {str(e)}"
        )

@router.post("/{image_id}:security-scan", response_model=Dict[str, Any])
def security_scan_container_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Perform comprehensive security scan on container image
    """
    image = db.query(ContainerImage).filter(
        ContainerImage.id == image_id,
        ContainerImage.user_id == current_user["user_id"]
    ).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container image not found"
        )

    try:
        scanner = SecurityScanner()

        # Perform comprehensive scan
        scan_results = scanner.comprehensive_scan(image.name)

        # Update security score based on scan results
        security_score = scanner.calculate_security_score(scan_results)
        image.security_score = security_score
        db.commit()

        return scan_results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform security scan: {str(e)}"
        )

@router.post("/{image_id}:compliance-check", response_model=Dict[str, Any])
def compliance_check_container_image(
    image_id: int,
    compliance_standards: List[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Check container image compliance with security standards
    """
    image = db.query(ContainerImage).filter(
        ContainerImage.id == image_id,
        ContainerImage.user_id == current_user["user_id"]
    ).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container image not found"
        )

    try:
        scanner = SecurityScanner()

        # Check compliance with specified standards
        compliance_standards = compliance_standards or ["cis-docker-benchmark", "nist-800-53"]
        compliance_results = scanner.check_compliance(
            image.name,
            compliance_standards
        )

        return compliance_results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check compliance: {str(e)}"
        )

@router.post("/{image_id}:vulnerability-report", response_model=Dict[str, Any])
def vulnerability_report_container_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate detailed vulnerability report for container image
    """
    image = db.query(ContainerImage).filter(
        ContainerImage.id == image_id,
        ContainerImage.user_id == current_user["user_id"]
    ).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container image not found"
        )

    try:
        scanner = SecurityScanner()

        # Generate vulnerability report
        vulnerability_report = scanner.generate_vulnerability_report(image.name)

        # Calculate risk score
        risk_score = scanner.calculate_risk_score(vulnerability_report)

        return {
            "vulnerability_report": vulnerability_report,
            "risk_score": risk_score,
            "remediation_suggestions": scanner.generate_remediation_suggestions(vulnerability_report),
            "overall_security_status": "secure" if risk_score < 50 else "moderate" if risk_score < 80 else "high"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate vulnerability report: {str(e)}"
        )