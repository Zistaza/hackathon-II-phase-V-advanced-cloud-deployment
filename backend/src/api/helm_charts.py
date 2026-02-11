from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import subprocess
import yaml
import json
import tempfile
import os

from ..database import get_db
from ..services.auth_service import get_current_user

router = APIRouter(prefix="/api/helm-charts", tags=["helm-charts"])
security = HTTPBearer()

class HelmChartCreateRequest(BaseModel):
    name: str
    chart_repo: Optional[str] = None
    chart_ref: str
    version: Optional[str] = None
    values: Optional[Dict[str, Any]] = None
    namespace: Optional[str] = "default"

class HelmChartUpdateRequest(BaseModel):
    release_name: str
    chart_ref: Optional[str] = None
    version: Optional[str] = None
    values: Optional[Dict[str, Any]] = None
    namespace: Optional[str] = "default"

class HelmChartResponse(BaseModel):
    release_name: str
    status: str
    chart: str
    app_version: Optional[str]
    revision: int
    updated: str
    namespace: str

class HelmLintResponse(BaseModel):
    success: bool
    messages: List[str]
    chart_name: str

class HelmStatusResponse(BaseModel):
    name: str
    revision: str
    released: str
    status: str
    chart: str
    app_version: str
    namespace: str
    notes: Optional[str]

class HelmHistoryResponse(BaseModel):
    revision: int
    updated: str
    status: str
    chart: str
    app_version: str
    description: str

@router.post("/", response_model=HelmChartResponse)
def install_helm_chart(
    request: HelmChartCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Install a Helm chart to the Kubernetes cluster
    """
    try:
        # Prepare values file if provided
        values_file = None
        if request.values:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(request.values, f)
                values_file = f.name

        # Construct helm install command
        cmd = [
            "helm", "install", request.name, request.chart_ref,
            "--namespace", request.namespace,
            "--wait",
            "--timeout", "10m"
        ]

        if request.version:
            cmd.extend(["--version", request.version])

        if values_file:
            cmd.extend(["-f", values_file])

        if request.chart_repo:
            cmd.extend(["--repo", request.chart_repo])

        # Execute helm install
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Clean up values file if created
        if values_file:
            os.unlink(values_file)

        # Return success status (would normally query helm status to get details)
        return HelmChartResponse(
            release_name=request.name,
            status="deployed",
            chart=f"{request.chart_ref}-{request.version or 'latest'}",
            app_version=None,
            revision=1,
            updated="just now",
            namespace=request.namespace
        )

    except subprocess.CalledProcessError as e:
        if values_file:
            os.unlink(values_file)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Helm install failed: {e.stderr}"
        )
    except Exception as e:
        if values_file:
            os.unlink(values_file)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to install Helm chart: {str(e)}"
        )

@router.put("/{release_name}", response_model=HelmChartResponse)
def upgrade_helm_chart(
    release_name: str,
    request: HelmChartUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Upgrade an existing Helm release
    """
    try:
        # Prepare values file if provided
        values_file = None
        if request.values:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(request.values, f)
                values_file = f.name

        # Construct helm upgrade command
        cmd = [
            "helm", "upgrade", release_name,
            request.chart_ref or f"./{release_name}",
            "--namespace", request.namespace,
            "--wait",
            "--timeout", "10m"
        ]

        if request.version:
            cmd.extend(["--version", request.version])

        if values_file:
            cmd.extend(["-f", values_file])

        # Execute helm upgrade
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Clean up values file if created
        if values_file:
            os.unlink(values_file)

        # Query the status after upgrade
        status_cmd = ["helm", "status", release_name, "--namespace", request.namespace, "--output", "json"]
        status_result = subprocess.run(status_cmd, capture_output=True, text=True, check=True)
        status_data = json.loads(status_result.stdout)

        return HelmChartResponse(
            release_name=release_name,
            status=status_data.get("info", {}).get("status", "unknown"),
            chart=status_data.get("chart", ""),
            app_version=status_data.get("app_version", ""),
            revision=status_data.get("version", 0),
            updated=status_data.get("info", {}).get("last_deployed", "unknown"),
            namespace=request.namespace
        )

    except subprocess.CalledProcessError as e:
        if values_file:
            os.unlink(values_file)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Helm upgrade failed: {e.stderr}"
        )
    except Exception as e:
        if values_file:
            os.unlink(values_file)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upgrade Helm chart: {str(e)}"
        )

@router.delete("/{release_name}")
def uninstall_helm_chart(
    release_name: str,
    namespace: str = "default",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Uninstall a Helm release
    """
    try:
        cmd = ["helm", "uninstall", release_name, "--namespace", namespace]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        return {"message": f"Helm release {release_name} uninstalled successfully"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Helm uninstall failed: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to uninstall Helm chart: {str(e)}"
        )

@router.get("/{release_name}/status", response_model=HelmStatusResponse)
def get_helm_chart_status(
    release_name: str,
    namespace: str = "default",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get status of a Helm release
    """
    try:
        cmd = ["helm", "status", release_name, "--namespace", namespace, "--output", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        return HelmStatusResponse(
            name=data.get("name", release_name),
            revision=str(data.get("version", "")),
            released=data.get("info", {}).get("last_deployed", ""),
            status=data.get("info", {}).get("status", ""),
            chart=data.get("chart", ""),
            app_version=data.get("app_version", ""),
            namespace=namespace,
            notes=data.get("info", {}).get("notes", "")
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Helm status failed: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Helm chart status: {str(e)}"
        )

@router.get("/{release_name}/history", response_model=List[HelmHistoryResponse])
def get_helm_chart_history(
    release_name: str,
    namespace: str = "default",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get history of a Helm release
    """
    try:
        cmd = ["helm", "history", release_name, "--namespace", namespace, "--output", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        history = json.loads(result.stdout)

        return [
            HelmHistoryResponse(
                revision=item.get("revision", 0),
                updated=item.get("updated", ""),
                status=item.get("status", ""),
                chart=item.get("chart", ""),
                app_version=item.get("app_version", ""),
                description=item.get("description", "")
            )
            for item in history
        ]

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Helm history failed: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Helm chart history: {str(e)}"
        )

@router.post("/lint", response_model=HelmLintResponse)
def lint_helm_chart(
    chart_path: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Lint a Helm chart for potential issues
    """
    try:
        cmd = ["helm", "lint", chart_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Parse output to extract lint messages
        messages = []
        if result.stdout:
            messages.extend([line.strip() for line in result.stdout.split('\n') if line.strip()])
        if result.stderr:
            messages.extend([f"ERROR: {line.strip()}" for line in result.stderr.split('\n') if line.strip()])

        return HelmLintResponse(
            success=True,
            messages=messages,
            chart_name=os.path.basename(chart_path)
        )

    except subprocess.CalledProcessError as e:
        messages = [f"ERROR: {line.strip()}" for line in e.stderr.split('\n') if line.strip()]
        return HelmLintResponse(
            success=False,
            messages=messages,
            chart_name=os.path.basename(chart_path) if 'chart_path' in locals() else "unknown"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to lint Helm chart: {str(e)}"
        )

@router.get("/releases", response_model=List[HelmChartResponse])
def list_helm_releases(
    namespace: str = "default",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all Helm releases in a namespace
    """
    try:
        cmd = ["helm", "list", "--namespace", namespace, "--output", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        releases = json.loads(result.stdout)

        return [
            HelmChartResponse(
                release_name=release.get("name", ""),
                status=release.get("status", ""),
                chart=release.get("chart", ""),
                app_version=release.get("app_version", ""),
                revision=release.get("revision", 0),
                updated=release.get("updated", ""),
                namespace=release.get("namespace", namespace)
            )
            for release in releases
        ]

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Helm list failed: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list Helm releases: {str(e)}"
        )