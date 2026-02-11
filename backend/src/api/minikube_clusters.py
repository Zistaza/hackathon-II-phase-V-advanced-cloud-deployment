from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import subprocess
import json
import time
import os

from ..database import get_db
from ..services.auth_service import get_current_user

router = APIRouter(prefix="/api/minikube-clusters", tags=["minikube-clusters"])
security = HTTPBearer()

class MinikubeStartRequest(BaseModel):
    cluster_name: str = "minikube"
    driver: str = "docker"
    cpus: int = 2
    memory: str = "4g"
    disk_size: str = "20g"
    extra_config: Optional[Dict[str, Any]] = None

class MinikubeConfigRequest(BaseModel):
    cluster_name: str = "minikube"
    cpus: Optional[int] = None
    memory: Optional[str] = None
    disk_size: Optional[str] = None

class MinikubeStatusResponse(BaseModel):
    name: str
    status: str
    apiserver_url: Optional[str]
    kubeconfig_path: Optional[str]
    node_ip: Optional[str]
    driver: Optional[str]
    details: Optional[Dict[str, Any]]

class MinikubeClusterInfo(BaseModel):
    name: str
    driver: str
    state: str
    nodes: List[Dict[str, Any]]
    kubernetes_version: str
    control_plane: bool
    docker_env: Optional[bool]
    is_admin: bool

@router.post("/start", response_model=MinikubeStatusResponse)
def start_minikube_cluster(
    request: MinikubeStartRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Start a Minikube cluster
    """
    try:
        cmd = [
            "minikube", "start",
            "--profile", request.cluster_name,
            "--driver", request.driver,
            "--cpus", str(request.cpus),
            "--memory", request.memory,
            "--disk-size", request.disk_size,
            "--wait", "true",
            "--timeout", "10m"
        ]

        # Add extra config if provided
        if request.extra_config:
            for key, value in request.extra_config.items():
                cmd.extend([f"--{key}", str(value)])

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Get cluster status after starting
        status_cmd = ["minikube", "status", "--profile", request.cluster_name, "--output", "json"]
        status_result = subprocess.run(status_cmd, capture_output=True, text=True, check=True)
        status_data = json.loads(status_result.stdout)

        return MinikubeStatusResponse(
            name=request.cluster_name,
            status=status_data.get("Host", "unknown"),
            apiserver_url=status_data.get("Kubelet", {}).get("apiserver_url"),
            kubeconfig_path=status_data.get("Kubelet", {}).get("kubeconfig_path"),
            node_ip=status_data.get("Kubelet", {}).get("node_ip"),
            driver=status_data.get("Driver", request.driver),
            details=status_data
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start Minikube cluster: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start Minikube cluster: {str(e)}"
        )

@router.post("/stop")
def stop_minikube_cluster(
    cluster_name: str = "minikube",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Stop a Minikube cluster
    """
    try:
        cmd = ["minikube", "stop", "--profile", cluster_name]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        return {"message": f"Minikube cluster {cluster_name} stopped successfully"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop Minikube cluster: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop Minikube cluster: {str(e)}"
        )

@router.post("/delete")
def delete_minikube_cluster(
    cluster_name: str = "minikube",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a Minikube cluster
    """
    try:
        cmd = ["minikube", "delete", "--profile", cluster_name]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        return {"message": f"Minikube cluster {cluster_name} deleted successfully"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete Minikube cluster: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete Minikube cluster: {str(e)}"
        )

@router.get("/status", response_model=MinikubeStatusResponse)
def get_minikube_cluster_status(
    cluster_name: str = "minikube",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get status of a Minikube cluster
    """
    try:
        cmd = ["minikube", "status", "--profile", cluster_name, "--output", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        status_data = json.loads(result.stdout)

        return MinikubeStatusResponse(
            name=cluster_name,
            status=status_data.get("Host", "unknown"),
            apiserver_url=status_data.get("Kubelet", {}).get("apiserver_url"),
            kubeconfig_path=status_data.get("Kubelet", {}).get("kubeconfig_path"),
            node_ip=status_data.get("Kubelet", {}).get("node_ip"),
            driver=status_data.get("Driver", "unknown"),
            details=status_data
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Minikube cluster status: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Minikube cluster status: {str(e)}"
        )

@router.get("/list", response_model=List[MinikubeClusterInfo])
def list_minikube_clusters(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all Minikube clusters
    """
    try:
        cmd = ["minikube", "profile", "list", "--output", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # The output format may vary, so handle both cases
        try:
            profiles_data = json.loads(result.stdout)
            profiles_list = profiles_data.get('valid', []) if isinstance(profiles_data, dict) else profiles_data
        except json.JSONDecodeError:
            # If the output is not JSON, parse it as text
            lines = result.stdout.strip().split('\n')
            profiles_list = []
            for line in lines[1:]:  # Skip header
                if line.strip() and '|' in line:
                    parts = [part.strip() for part in line.split('|')]
                    if len(parts) >= 3:
                        profiles_list.append({
                            "Name": parts[0],
                            "Status": parts[1],
                            "Config": parts[2]
                        })

        clusters = []
        for profile in profiles_list:
            cluster_info = MinikubeClusterInfo(
                name=profile.get("Name", profile.get("name", "unknown")),
                driver=profile.get("Config", {}).get("MachineConfig", {}).get("VMDriver", "unknown"),
                state=profile.get("Status", profile.get("status", "unknown")),
                nodes=[],
                kubernetes_version="",
                control_plane=False,
                docker_env=False,
                is_admin=False
            )
            clusters.append(cluster_info)

        return clusters

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list Minikube clusters: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list Minikube clusters: {str(e)}"
        )

@router.post("/configure")
def configure_minikube_cluster(
    request: MinikubeConfigRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Configure a Minikube cluster settings
    """
    try:
        # First stop the cluster if it's running
        status_cmd = ["minikube", "status", "--profile", request.cluster_name, "--output", "json"]
        status_result = subprocess.run(status_cmd, capture_output=True, text=True)

        cluster_running = False
        if status_result.returncode == 0:
            try:
                status_data = json.loads(status_result.stdout)
                cluster_running = status_data.get("Host", "") == "Running"
            except:
                pass

        if cluster_running:
            stop_cmd = ["minikube", "stop", "--profile", request.cluster_name]
            subprocess.run(stop_cmd, capture_output=True, text=True)

        # Apply configuration changes
        if request.cpus is not None:
            cpus_cmd = ["minikube", "config", "set", "cpus", str(request.cpus)]
            subprocess.run(cpus_cmd, capture_output=True, text=True)

        if request.memory is not None:
            memory_cmd = ["minikube", "config", "set", "memory", request.memory]
            subprocess.run(memory_cmd, capture_output=True, text=True)

        if request.disk_size is not None:
            disk_cmd = ["minikube", "config", "set", "disk-size", request.disk_size]
            subprocess.run(disk_cmd, capture_output=True, text=True)

        # Restart the cluster if it was running
        if cluster_running:
            start_cmd = ["minikube", "start", "--profile", request.cluster_name]
            subprocess.run(start_cmd, capture_output=True, text=True)

        return {
            "message": f"Configuration updated for cluster {request.cluster_name}",
            "updated_settings": {
                "cpus": request.cpus,
                "memory": request.memory,
                "disk_size": request.disk_size
            }
        }

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to configure Minikube cluster: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to configure Minikube cluster: {str(e)}"
        )

@router.get("/dashboard-url")
def get_minikube_dashboard_url(
    cluster_name: str = "minikube",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get the URL for the Minikube dashboard
    """
    try:
        cmd = ["minikube", "dashboard", "--profile", cluster_name, "--url", "--format", "{{.URL}}"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        dashboard_url = result.stdout.strip()

        return {"dashboard_url": dashboard_url}

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Minikube dashboard URL: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Minikube dashboard URL: {str(e)}"
        )

@router.post("/enable-addon")
def enable_minikube_addon(
    addon_name: str,
    cluster_name: str = "minikube",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Enable a Minikube addon
    """
    try:
        cmd = ["minikube", "addons", "enable", addon_name, "--profile", cluster_name]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        return {"message": f"Addon {addon_name} enabled successfully for cluster {cluster_name}"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable Minikube addon: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable Minikube addon: {str(e)}"
        )

@router.post("/disable-addon")
def disable_minikube_addon(
    addon_name: str,
    cluster_name: str = "minikube",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Disable a Minikube addon
    """
    try:
        cmd = ["minikube", "addons", "disable", addon_name, "--profile", cluster_name]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        return {"message": f"Addon {addon_name} disabled successfully for cluster {cluster_name}"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable Minikube addon: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable Minikube addon: {str(e)}"
        )