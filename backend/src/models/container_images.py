from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class ContainerImage(Base):
    """
    ContainerImage model for storing container image information
    """
    __tablename__ = "container_images"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    path = Column(String(500), nullable=False)
    base_image = Column(String(255), nullable=False)
    optimization_level = Column(String(50), nullable=False)
    dockerfile_content = Column(Text, nullable=False)
    image_size = Column(Float, nullable=True)  # Size in bytes
    security_score = Column(Float, nullable=True)  # Score from 0-100
    built_status = Column(String(20), nullable=True)  # success, failed, pending
    built_error = Column(Text, nullable=True)
    built_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="container_images")

    # Indexes for performance
    __table_args__ = (
        {
            "indexes": [
                {"columns": [user_id, name], "unique": True},
                {"columns": [user_id, created_at]},
                {"columns": [user_id, built_status]},
            ]
        },
    )

class ContainerImageCreate:
    """
    Pydantic model for creating container images
    """
    def __init__(
        self,
        name: str,
        path: str,
        base_image: str,
        optimization_level: str
    ):
        self.name = name
        self.path = path
        self.base_image = base_image
        self.optimization_level = optimization_level

class ContainerImageUpdate:
    """
    Pydantic model for updating container images
    """
    def __init__(
        self,
        name: Optional[str] = None,
        optimization_level: Optional[str] = None
    ):
        self.name = name
        self.optimization_level = optimization_level

class ContainerImageResponse:
    """
    Pydantic model for container image response
    """
    def __init__(
        self,
        id: int,
        name: str,
        path: str,
        base_image: str,
        optimization_level: str,
        dockerfile_content: str,
        image_size: Optional[float],
        security_score: Optional[float],
        built_status: Optional[str],
        built_error: Optional[str],
        built_at: Optional[datetime],
        created_at: datetime,
        updated_at: datetime
    ):
        self.id = id
        self.name = name
        self.path = path
        self.base_image = base_image
        self.optimization_level = optimization_level
        self.dockerfile_content = dockerfile_content
        self.image_size = image_size
        self.security_score = security_score
        self.built_status = built_status
        self.built_error = built_error
        self.built_at = built_at
        self.created_at = created_at
        self.updated_at = updated_at

class ContainerImageBuildOptions:
    """
    Pydantic model for container image build options
    """
    def __init__(
        self,
        tags: Optional[List[str]] = None,
        build_args: Optional[dict] = None,
        cache_from: Optional[List[str]] = None,
        platform: Optional[str] = None,
        ssh: Optional[str] = None
    ):
        self.tags = tags or []
        self.build_args = build_args or {}
        self.cache_from = cache_from or []
        self.platform = platform
        self.ssh = ssh

class ContainerImageValidationResult:
    """
    Pydantic model for container image validation results
    """
    def __init__(
        self,
        dockerfile_analysis: str,
        security_best_practices: str,
        vulnerability_scan: str,
        optimization_score: int,
        recommendations: Optional[List[str]] = None
    ):
        self.dockerfile_analysis = dockerfile_analysis
        self.security_best_practices = security_best_practices
        self.vulnerability_scan = vulnerability_scan
        self.optimization_score = optimization_score
        self.recommendations = recommendations or []

class ContainerImageHealthCheck:
    """
    Pydantic model for container image health check
    """
    def __init__(
        self,
        image_exists: bool,
        size: Optional[float],
        last_built: Optional[datetime],
        status: str,
        security_compliance: str,
        registry_status: Optional[str] = None,
        vulnerabilities: Optional[int] = None
    ):
        self.image_exists = image_exists
        self.size = size
        self.last_built = last_built
        self.status = status
        self.security_compliance = security_compliance
        self.registry_status = registry_status
        self.vulnerabilities = vulnerabilities