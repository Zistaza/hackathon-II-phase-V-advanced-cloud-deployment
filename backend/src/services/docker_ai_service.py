import requests
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DockerAIService:
    """
    Docker AI Service for container image optimization and creation
    """
    def __init__(
        self,
        api_url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()

        # Set headers if API key is provided
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def create_container_image(
        self,
        name: str,
        path: str,
        base_image: str,
        optimization_level: str
    ) -> Dict[str, Any]:
        """
        Create a container image using Docker AI optimization

        Args:
            name: Name of the container image
            path: Path to the application source code
            base_image: Base image to use (e.g., python:3.11-slim)
            optimization_level: Optimization level (basic, advanced, security-first)

        Returns:
            Dictionary with Dockerfile content, size estimate, and security score
        """
        try:
            logger.info(f"Creating container image {name} with optimization level {optimization_level}")

            # Prepare request payload
            payload = {
                "name": name,
                "path": path,
                "base_image": base_image,
                "optimization_level": optimization_level,
                "features": {
                    "multi_stage": True,
                    "security_hardening": optimization_level == "security-first",
                    "size_optimization": optimization_level in ["advanced", "security-first"],
                    "non_root_user": optimization_level in ["advanced", "security-first"]
                }
            }

            # Send request to Docker AI
            response = self.session.post(
                f"{self.api_url}/v1/images/create",
                json=payload,
                timeout=self.timeout
            )

            response.raise_for_status()
            result = response.json()

            # Process response
            dockerfile_content = result.get("dockerfile", "")
            size_estimate = result.get("size_estimate", 0)
            security_score = result.get("security_score", 0)

            return {
                "dockerfile": dockerfile_content,
                "size": size_estimate,
                "security_score": security_score,
                "optimization_level": optimization_level,
                "created_at": datetime.now().isoformat()
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create container image: {str(e)}")
            raise Exception(f"Docker AI API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Docker AI response: {str(e)}")
            raise Exception(f"Failed to parse Docker AI response: {str(e)}")
        except KeyError as e:
            logger.error(f"Missing expected field in Docker AI response: {str(e)}")
            raise Exception(f"Missing expected field in Docker AI response: {str(e)}")

    def optimize_container_image(
        self,
        name: str,
        optimization_level: str
    ) -> Dict[str, Any]:
        """
        Optimize an existing container image

        Args:
            name: Name of the container image to optimize
            optimization_level: New optimization level

        Returns:
            Dictionary with optimization results
        """
        try:
            logger.info(f"Optimizing container image {name} to level {optimization_level}")

            # Prepare request payload
            payload = {
                "name": name,
                "optimization_level": optimization_level,
                "optimization_type": "rebuild"
            }

            # Send request to Docker AI
            response = self.session.post(
                f"{self.api_url}/v1/images/{name}/optimize",
                json=payload,
                timeout=self.timeout
            )

            response.raise_for_status()
            result = response.json()

            # Process response
            optimization_results = {
                "original_size": result.get("original_size", 0),
                "optimized_size": result.get("optimized_size", 0),
                "size_reduction": result.get("size_reduction", 0),
                "security_improvements": result.get("security_improvements", []),
                "optimization_time": result.get("optimization_time", 0),
                "optimization_level": optimization_level
            }

            return optimization_results

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to optimize container image: {str(e)}")
            raise Exception(f"Docker AI API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Docker AI response: {str(e)}")
            raise Exception(f"Failed to parse Docker AI response: {str(e)}")
        except KeyError as e:
            logger.error(f"Missing expected field in Docker AI response: {str(e)}")
            raise Exception(f"Missing expected field in Docker AI response: {str(e)}")

    def analyze_container_image(
        self,
        name: str
    ) -> Dict[str, Any]:
        """
        Analyze container image for security and performance

        Args:
            name: Name of the container image to analyze

        Returns:
            Dictionary with analysis results
        """
        try:
            logger.info(f"Analyzing container image {name}")

            # Send request to Docker AI
            response = self.session.get(
                f"{self.api_url}/v1/images/{name}/analyze",
                timeout=self.timeout
            )

            response.raise_for_status()
            result = response.json()

            # Process response
            analysis_results = {
                "security_score": result.get("security_score", 0),
                "vulnerabilities": result.get("vulnerabilities", []),
                "compliance_status": result.get("compliance_status", "unknown"),
                "recommendations": result.get("recommendations", []),
                "last_scan": result.get("last_scan", datetime.now().isoformat()),
                "image_size": result.get("image_size", 0),
                "layers": result.get("layers", [])
            }

            return analysis_results

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to analyze container image: {str(e)}")
            raise Exception(f"Docker AI API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Docker AI response: {str(e)}")
            raise Exception(f"Failed to parse Docker AI response: {str(e)}")
        except KeyError as e:
            logger.error(f"Missing expected field in Docker AI response: {str(e)}")
            raise Exception(f"Missing expected field in Docker AI response: {str(e)}")

    def get_container_image_details(
        self,
        name: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a container image

        Args:
            name: Name of the container image

        Returns:
            Dictionary with image details
        """
        try:
            logger.info(f"Getting details for container image {name}")

            # Send request to Docker AI
            response = self.session.get(
                f"{self.api_url}/v1/images/{name}/details",
                timeout=self.timeout
            )

            response.raise_for_status()
            result = response.json()

            # Process response
            image_details = {
                "name": result.get("name", name),
                "created_at": result.get("created_at", datetime.now().isoformat()),
                "size": result.get("size", 0),
                "layers": result.get("layers", []),
                "base_image": result.get("base_image", "unknown"),
                "optimization_level": result.get("optimization_level", "basic"),
                "security_score": result.get("security_score", 0),
                "vulnerabilities": result.get("vulnerabilities", []),
                "compliance_status": result.get("compliance_status", "unknown")
            }

            return image_details

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get image details: {str(e)}")
            raise Exception(f"Docker AI API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Docker AI response: {str(e)}")
            raise Exception(f"Failed to parse Docker AI response: {str(e)}")
        except KeyError as e:
            logger.error(f"Missing expected field in Docker AI response: {str(e)}")
            raise Exception(f"Missing expected field in Docker AI response: {str(e)}")

    def list_container_images(
        self,
        user_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List container images for a user

        Args:
            user_id: User ID to filter images (optional)
            limit: Maximum number of images to return
            offset: Offset for pagination

        Returns:
            List of container image summaries
        """
        try:
            logger.info(f"Listing container images for user {user_id}")

            # Prepare query parameters
            params = {
                "limit": limit,
                "offset": offset
            }
            if user_id:
                params["user_id"] = user_id

            # Send request to Docker AI
            response = self.session.get(
                f"{self.api_url}/v1/images",
                params=params,
                timeout=self.timeout
            )

            response.raise_for_status()
            result = response.json()

            # Process response
            images = []
            for image_data in result.get("images", []):
                images.append({
                    "id": image_data.get("id"),
                    "name": image_data.get("name"),
                    "created_at": image_data.get("created_at"),
                    "size": image_data.get("size"),
                    "security_score": image_data.get("security_score"),
                    "status": image_data.get("status", "ready")
                })

            return images

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list container images: {str(e)}")
            raise Exception(f"Docker AI API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Docker AI response: {str(e)}")
            raise Exception(f"Failed to parse Docker AI response: {str(e)}")
        except KeyError as e:
            logger.error(f"Missing expected field in Docker AI response: {str(e)}")
            raise Exception(f"Missing expected field in Docker AI response: {str(e)}")

    def validate_docker_ai_connection(self) -> bool:
        """
        Validate connection to Docker AI service

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            logger.info("Validating Docker AI connection")

            # Send request to Docker AI
            response = self.session.get(
                f"{self.api_url}/v1/health",
                timeout=5
            )

            response.raise_for_status()
            health_status = response.json()

            return health_status.get("status") == "healthy"

        except requests.exceptions.RequestException:
            logger.error("Docker AI connection validation failed")
            return False
        except json.JSONDecodeError:
            logger.error("Failed to parse Docker AI health response")
            return False

    def get_optimization_recommendations(
        self,
        name: str
    ) -> List[str]:
        """
        Get optimization recommendations for a container image

        Args:
            name: Name of the container image

        Returns:
            List of optimization recommendations
        """
        try:
            logger.info(f"Getting optimization recommendations for {name}")

            # Send request to Docker AI
            response = self.session.get(
                f"{self.api_url}/v1/images/{name}/recommendations",
                timeout=self.timeout
            )

            response.raise_for_status()
            result = response.json()

            return result.get("recommendations", [])

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get recommendations: {str(e)}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Docker AI response: {str(e)}")
            return []
        except KeyError as e:
            logger.error(f"Missing expected field in Docker AI response: {str(e)}")
            return []