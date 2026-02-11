from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import subprocess
import json
import yaml
import tempfile
import os

from ..database import get_db
from ..services.auth_service import get_current_user

router = APIRouter(prefix="/api/deployments", tags=["deployments"])
security = HTTPBearer()

class DeploymentCreateRequest(BaseModel):
    name: str
    image: str
    replicas: int = 1
    namespace: str = "default"
    port: Optional[int] = None
    env_vars: Optional[Dict[str, str]] = None
    resources: Optional[Dict[str, Any]] = None
    labels: Optional[Dict[str, str]] = None
    annotations: Optional[Dict[str, str]] = None

class DeploymentUpdateRequest(BaseModel):
    name: str
    image: Optional[str] = None
    replicas: Optional[int] = None
    namespace: str = "default"
    env_vars: Optional[Dict[str, str]] = None
    resources: Optional[Dict[str, Any]] = None

class DeploymentResponse(BaseModel):
    name: str
    namespace: str
    replicas: int
    ready_replicas: int
    updated_replicas: int
    available_replicas: int
    status: str
    age: str
    image: str

class DeploymentScaleRequest(BaseModel):
    replicas: int
    namespace: str = "default"

class DeploymentStatusResponse(BaseModel):
    name: str
    namespace: str
    status: Dict[str, Any]

@router.post("/", response_model=DeploymentResponse)
def create_deployment(
    request: DeploymentCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a Kubernetes deployment
    """
    try:
        # Create a temporary YAML file for the deployment
        deployment_yaml = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": request.name,
                "namespace": request.namespace,
                "labels": request.labels or {},
                "annotations": request.annotations or {}
            },
            "spec": {
                "replicas": request.replicas,
                "selector": {
                    "matchLabels": {
                        "app": request.name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": request.name
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": request.name,
                            "image": request.image,
                            "ports": [{"containerPort": request.port}] if request.port else [],
                            "env": [{"name": k, "value": v} for k, v in (request.env_vars or {}).items()],
                            "resources": request.resources or {}
                        }]
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(deployment_yaml, f)
            yaml_file = f.name

        # Apply the deployment
        cmd = ["kubectl", "apply", "-f", yaml_file]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Clean up the temporary file
        os.unlink(yaml_file)

        # Get deployment details
        details_cmd = [
            "kubectl", "get", "deployment", request.name,
            "-n", request.namespace,
            "-o", "json"
        ]
        details_result = subprocess.run(details_cmd, capture_output=True, text=True, check=True)
        deployment_details = json.loads(details_result.stdout)

        spec = deployment_details.get("spec", {})
        status = deployment_details.get("status", {})

        return DeploymentResponse(
            name=request.name,
            namespace=request.namespace,
            replicas=spec.get("replicas", 0),
            ready_replicas=status.get("readyReplicas", 0) or 0,
            updated_replicas=status.get("updatedReplicas", 0) or 0,
            available_replicas=status.get("availableReplicas", 0) or 0,
            status=status.get("conditions", [{}])[0].get("type", "Unknown") if status.get("conditions") else "Unknown",
            age="",  # Would need to calculate from metadata.creationTimestamp
            image=spec.get("template", {}).get("spec", {}).get("containers", [{}])[0].get("image", "")
        )

    except subprocess.CalledProcessError as e:
        if 'yaml_file' in locals():
            os.unlink(yaml_file)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create deployment: {e.stderr}"
        )
    except Exception as e:
        if 'yaml_file' in locals():
            os.unlink(yaml_file)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create deployment: {str(e)}"
        )

@router.get("/{name}", response_model=DeploymentResponse)
def get_deployment(
    name: str,
    namespace: str = "default",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get details of a Kubernetes deployment
    """
    try:
        cmd = ["kubectl", "get", "deployment", name, "-n", namespace, "-o", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        deployment = json.loads(result.stdout)

        spec = deployment.get("spec", {})
        status = deployment.get("status", {})

        return DeploymentResponse(
            name=name,
            namespace=namespace,
            replicas=spec.get("replicas", 0),
            ready_replicas=status.get("readyReplicas", 0) or 0,
            updated_replicas=status.get("updatedReplicas", 0) or 0,
            available_replicas=status.get("availableReplicas", 0) or 0,
            status=status.get("conditions", [{}])[0].get("type", "Unknown") if status.get("conditions") else "Unknown",
            age="",  # Would need to calculate from metadata.creationTimestamp
            image=spec.get("template", {}).get("spec", {}).get("containers", [{}])[0].get("image", "")
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {name} not found in namespace {namespace}: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get deployment: {str(e)}"
        )

@router.put("/{name}")
def update_deployment(
    name: str,
    request: DeploymentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a Kubernetes deployment
    """
    try:
        # Get current deployment
        get_cmd = ["kubectl", "get", "deployment", name, "-n", request.namespace, "-o", "json"]
        get_result = subprocess.run(get_cmd, capture_output=True, text=True, check=True)
        current_deployment = json.loads(get_result.stdout)

        # Update fields based on request
        if request.image:
            current_deployment["spec"]["template"]["spec"]["containers"][0]["image"] = request.image

        if request.replicas is not None:
            current_deployment["spec"]["replicas"] = request.replicas

        if request.env_vars:
            # Update environment variables
            current_containers = current_deployment["spec"]["template"]["spec"]["containers"]
            for container in current_containers:
                container["env"] = [{"name": k, "value": v} for k, v in request.env_vars.items()]

        if request.resources:
            # Update resources
            current_containers = current_deployment["spec"]["template"]["spec"]["containers"]
            for container in current_containers:
                container["resources"] = request.resources

        # Create temporary file with updated deployment
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(current_deployment, f)
            yaml_file = f.name

        # Apply the updated deployment
        cmd = ["kubectl", "apply", "-f", yaml_file]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Clean up the temporary file
        os.unlink(yaml_file)

        return {
            "message": f"Deployment {name} updated successfully",
            "details": {
                "image": request.image,
                "replicas": request.replicas,
                "env_vars": request.env_vars,
                "resources": request.resources
            }
        }

    except subprocess.CalledProcessError as e:
        if 'yaml_file' in locals():
            os.unlink(yaml_file)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update deployment: {e.stderr}"
        )
    except Exception as e:
        if 'yaml_file' in locals():
            os.unlink(yaml_file)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update deployment: {str(e)}"
        )

@router.delete("/{name}")
def delete_deployment(
    name: str,
    namespace: str = "default",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a Kubernetes deployment
    """
    try:
        cmd = ["kubectl", "delete", "deployment", name, "-n", namespace]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        return {"message": f"Deployment {name} deleted successfully from namespace {namespace}"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete deployment: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete deployment: {str(e)}"
        )

@router.post("/{name}/scale")
def scale_deployment(
    name: str,
    request: DeploymentScaleRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Scale a Kubernetes deployment
    """
    try:
        cmd = ["kubectl", "scale", "deployment", name, f"--replicas={request.replicas}", "-n", request.namespace]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        return {
            "message": f"Deployment {name} scaled to {request.replicas} replicas",
            "namespace": request.namespace,
            "requested_replicas": request.replicas
        }

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to scale deployment: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to scale deployment: {str(e)}"
        )

@router.get("/", response_model=List[DeploymentResponse])
def list_deployments(
    namespace: str = "default",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all deployments in a namespace
    """
    try:
        cmd = ["kubectl", "get", "deployments", "-n", namespace, "-o", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        deployments_data = json.loads(result.stdout)

        deployments = []
        for deployment in deployments_data.get("items", []):
            metadata = deployment.get("metadata", {})
            spec = deployment.get("spec", {})
            status = deployment.get("status", {})

            deployments.append(DeploymentResponse(
                name=metadata.get("name", ""),
                namespace=metadata.get("namespace", namespace),
                replicas=spec.get("replicas", 0),
                ready_replicas=status.get("readyReplicas", 0) or 0,
                updated_replicas=status.get("updatedReplicas", 0) or 0,
                available_replicas=status.get("availableReplicas", 0) or 0,
                status=status.get("conditions", [{}])[0].get("type", "Unknown") if status.get("conditions") else "Unknown",
                age="",  # Would need to calculate from metadata.creationTimestamp
                image=spec.get("template", {}).get("spec", {}).get("containers", [{}])[0].get("image", "")
            ))

        return deployments

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list deployments: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list deployments: {str(e)}"
        )

@router.get("/{name}/status", response_model=DeploymentStatusResponse)
def get_deployment_status(
    name: str,
    namespace: str = "default",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed status of a Kubernetes deployment
    """
    try:
        cmd = ["kubectl", "get", "deployment", name, "-n", namespace, "-o", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        deployment = json.loads(result.stdout)

        return DeploymentStatusResponse(
            name=name,
            namespace=namespace,
            status=deployment
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {name} not found in namespace {namespace}: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get deployment status: {str(e)}"
        )

@router.post("/{name}/rollback")
def rollback_deployment(
    name: str,
    namespace: str = "default",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Rollback a Kubernetes deployment to the previous revision
    """
    try:
        cmd = ["kubectl", "rollout", "undo", "deployment", name, "-n", namespace]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        return {"message": f"Deployment {name} rolled back successfully in namespace {namespace}"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rollback deployment: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rollback deployment: {str(e)}"
        )

@router.post("/{name}/pause")
def pause_deployment(
    name: str,
    namespace: str = "default",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Pause a Kubernetes deployment
    """
    try:
        cmd = ["kubectl", "rollout", "pause", "deployment", name, "-n", namespace]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        return {"message": f"Deployment {name} paused successfully in namespace {namespace}"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause deployment: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause deployment: {str(e)}"
        )

@router.post("/{name}/resume")
def resume_deployment(
    name: str,
    namespace: str = "default",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Resume a Kubernetes deployment
    """
    try:
        cmd = ["kubectl", "rollout", "resume", "deployment", name, "-n", namespace]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        return {"message": f"Deployment {name} resumed successfully in namespace {namespace}"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume deployment: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume deployment: {str(e)}"
        )