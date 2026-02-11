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

router = APIRouter(prefix="/api/services", tags=["services"])
security = HTTPBearer()

class ServiceCreateRequest(BaseModel):
    name: str
    service_type: str = "ClusterIP"  # ClusterIP, NodePort, LoadBalancer, ExternalName
    selector: Dict[str, str]
    ports: List[Dict[str, Any]]  # e.g., [{"port": 80, "target_port": 8080, "protocol": "TCP"}]
    namespace: str = "default"
    labels: Optional[Dict[str, str]] = None
    annotations: Optional[Dict[str, str]] = None

class ServiceUpdateRequest(BaseModel):
    name: str
    namespace: str = "default"
    ports: Optional[List[Dict[str, Any]]] = None
    selector: Optional[Dict[str, str]] = None

class ServiceResponse(BaseModel):
    name: str
    namespace: str
    service_type: str
    cluster_ip: Optional[str]
    external_ips: List[str]
    ports: List[Dict[str, Any]]
    selector: Dict[str, str]
    status: str
    age: str

class ServiceEndpointResponse(BaseModel):
    name: str
    namespace: str
    endpoints: List[Dict[str, Any]]

@router.post("/", response_model=ServiceResponse)
def create_service(
    request: ServiceCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a Kubernetes service
    """
    try:
        # Create a temporary YAML file for the service
        service_yaml = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": request.name,
                "namespace": request.namespace,
                "labels": request.labels or {},
                "annotations": request.annotations or {}
            },
            "spec": {
                "type": request.service_type,
                "selector": request.selector,
                "ports": [
                    {
                        "port": port.get("port"),
                        "targetPort": port.get("target_port", port.get("port")),
                        "protocol": port.get("protocol", "TCP"),
                        "name": port.get("name", f"port-{port.get('port')}")
                    }
                    for port in request.ports
                ]
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(service_yaml, f)
            yaml_file = f.name

        # Apply the service
        cmd = ["kubectl", "apply", "-f", yaml_file]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Clean up the temporary file
        os.unlink(yaml_file)

        # Get service details
        details_cmd = [
            "kubectl", "get", "service", request.name,
            "-n", request.namespace,
            "-o", "json"
        ]
        details_result = subprocess.run(details_cmd, capture_output=True, text=True, check=True)
        service_details = json.loads(details_result.stdout)

        spec = service_details.get("spec", {})
        status = service_details.get("status", {})

        return ServiceResponse(
            name=request.name,
            namespace=request.namespace,
            service_type=spec.get("type", "ClusterIP"),
            cluster_ip=spec.get("clusterIP"),
            external_ips=spec.get("externalIPs", []),
            ports=[
                {
                    "port": port.get("port"),
                    "target_port": port.get("targetPort"),
                    "protocol": port.get("protocol", "TCP"),
                    "name": port.get("name")
                }
                for port in spec.get("ports", [])
            ],
            selector=spec.get("selector", {}),
            status=status.get("loadBalancer", {}).get("ingress", [{}])[0].get("ip", "Pending") if spec.get("type") == "LoadBalancer" else "Active",
            age=""  # Would need to calculate from metadata.creationTimestamp
        )

    except subprocess.CalledProcessError as e:
        if 'yaml_file' in locals():
            os.unlink(yaml_file)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create service: {e.stderr}"
        )
    except Exception as e:
        if 'yaml_file' in locals():
            os.unlink(yaml_file)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create service: {str(e)}"
        )

@router.get("/{name}", response_model=ServiceResponse)
def get_service(
    name: str,
    namespace: str = "default",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get details of a Kubernetes service
    """
    try:
        cmd = ["kubectl", "get", "service", name, "-n", namespace, "-o", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        service = json.loads(result.stdout)

        spec = service.get("spec", {})
        status = service.get("status", {})

        return ServiceResponse(
            name=name,
            namespace=namespace,
            service_type=spec.get("type", "ClusterIP"),
            cluster_ip=spec.get("clusterIP"),
            external_ips=spec.get("externalIPs", []),
            ports=[
                {
                    "port": port.get("port"),
                    "target_port": port.get("targetPort"),
                    "protocol": port.get("protocol", "TCP"),
                    "name": port.get("name")
                }
                for port in spec.get("ports", [])
            ],
            selector=spec.get("selector", {}),
            status=status.get("loadBalancer", {}).get("ingress", [{}])[0].get("ip", "Pending") if spec.get("type") == "LoadBalancer" else "Active",
            age=""  # Would need to calculate from metadata.creationTimestamp
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service {name} not found in namespace {namespace}: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get service: {str(e)}"
        )

@router.put("/{name}")
def update_service(
    name: str,
    request: ServiceUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a Kubernetes service
    """
    try:
        # Get current service
        get_cmd = ["kubectl", "get", "service", name, "-n", request.namespace, "-o", "json"]
        get_result = subprocess.run(get_cmd, capture_output=True, text=True, check=True)
        current_service = json.loads(get_result.stdout)

        # Update fields based on request
        if request.ports:
            current_service["spec"]["ports"] = [
                {
                    "port": port.get("port"),
                    "targetPort": port.get("target_port", port.get("port")),
                    "protocol": port.get("protocol", "TCP"),
                    "name": port.get("name", f"port-{port.get('port')}")
                }
                for port in request.ports
            ]

        if request.selector:
            current_service["spec"]["selector"].update(request.selector)

        # Create temporary file with updated service
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(current_service, f)
            yaml_file = f.name

        # Apply the updated service
        cmd = ["kubectl", "apply", "-f", yaml_file]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Clean up the temporary file
        os.unlink(yaml_file)

        return {
            "message": f"Service {name} updated successfully",
            "details": {
                "ports": request.ports,
                "selector": request.selector
            }
        }

    except subprocess.CalledProcessError as e:
        if 'yaml_file' in locals():
            os.unlink(yaml_file)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update service: {e.stderr}"
        )
    except Exception as e:
        if 'yaml_file' in locals():
            os.unlink(yaml_file)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update service: {str(e)}"
        )

@router.delete("/{name}")
def delete_service(
    name: str,
    namespace: str = "default",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a Kubernetes service
    """
    try:
        cmd = ["kubectl", "delete", "service", name, "-n", namespace]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        return {"message": f"Service {name} deleted successfully from namespace {namespace}"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete service: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete service: {str(e)}"
        )

@router.get("/", response_model=List[ServiceResponse])
def list_services(
    namespace: str = "default",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all services in a namespace
    """
    try:
        cmd = ["kubectl", "get", "services", "-n", namespace, "-o", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        services_data = json.loads(result.stdout)

        services = []
        for service in services_data.get("items", []):
            metadata = service.get("metadata", {})
            spec = service.get("spec", {})
            status = service.get("status", {})

            services.append(ServiceResponse(
                name=metadata.get("name", ""),
                namespace=metadata.get("namespace", namespace),
                service_type=spec.get("type", "ClusterIP"),
                cluster_ip=spec.get("clusterIP"),
                external_ips=spec.get("externalIPs", []),
                ports=[
                    {
                        "port": port.get("port"),
                        "target_port": port.get("targetPort"),
                        "protocol": port.get("protocol", "TCP"),
                        "name": port.get("name")
                    }
                    for port in spec.get("ports", [])
                ],
                selector=spec.get("selector", {}),
                status=status.get("loadBalancer", {}).get("ingress", [{}])[0].get("ip", "Pending") if spec.get("type") == "LoadBalancer" else "Active",
                age=""  # Would need to calculate from metadata.creationTimestamp
            ))

        return services

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list services: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list services: {str(e)}"
        )

@router.get("/{name}/endpoints", response_model=ServiceEndpointResponse)
def get_service_endpoints(
    name: str,
    namespace: str = "default",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get endpoints for a Kubernetes service
    """
    try:
        cmd = ["kubectl", "get", "endpoints", name, "-n", namespace, "-o", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        endpoints_data = json.loads(result.stdout)

        subsets = endpoints_data.get("subsets", [])

        endpoints = []
        for subset in subsets:
            addresses = subset.get("addresses", [])
            ports = subset.get("ports", [])

            for address in addresses:
                for port in ports:
                    endpoints.append({
                        "ip": address.get("ip"),
                        "hostname": address.get("hostname"),
                        "node_name": address.get("nodeName"),
                        "port": port.get("port"),
                        "protocol": port.get("protocol"),
                        "ready": True
                    })

            # Also add not ready addresses
            not_ready_addresses = subset.get("notReadyAddresses", [])
            for address in not_ready_addresses:
                for port in ports:
                    endpoints.append({
                        "ip": address.get("ip"),
                        "hostname": address.get("hostname"),
                        "node_name": address.get("nodeName"),
                        "port": port.get("port"),
                        "protocol": port.get("protocol"),
                        "ready": False
                    })

        return ServiceEndpointResponse(
            name=name,
            namespace=namespace,
            endpoints=endpoints
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Endpoints for service {name} not found in namespace {namespace}: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get service endpoints: {str(e)}"
        )

@router.get("/{name}/exposed-ip")
def get_service_exposed_ip(
    name: str,
    namespace: str = "default",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get the exposed IP for a service (useful for LoadBalancer services)
    """
    try:
        cmd = ["kubectl", "get", "service", name, "-n", namespace, "-o", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        service = json.loads(result.stdout)

        spec = service.get("spec", {})
        status = service.get("status", {})

        # For LoadBalancer services, return the ingress IP
        if spec.get("type") == "LoadBalancer":
            ingress_list = status.get("loadBalancer", {}).get("ingress", [])
            if ingress_list:
                ip = ingress_list[0].get("ip") or ingress_list[0].get("hostname")
                return {"exposed_ip": ip, "service_type": "LoadBalancer"}

        # For NodePort services, return the node IP and port
        elif spec.get("type") == "NodePort":
            # Get the node IP
            nodes_cmd = ["kubectl", "get", "nodes", "-o", "json"]
            nodes_result = subprocess.run(nodes_cmd, capture_output=True, text=True, check=True)
            nodes_data = json.loads(nodes_result.stdout)

            node_ip = None
            for node in nodes_data.get("items", []):
                addresses = node.get("status", {}).get("addresses", [])
                for addr in addresses:
                    if addr.get("type") == "InternalIP":
                        node_ip = addr.get("address")
                        break
                if node_ip:
                    break

            # Get NodePort from the service
            ports = spec.get("ports", [])
            node_ports = [port.get("nodePort") for port in ports if port.get("nodePort")]

            if node_ip and node_ports:
                return {
                    "exposed_ip": node_ip,
                    "node_ports": node_ports,
                    "service_type": "NodePort"
                }

        # For ClusterIP services, return the cluster IP
        else:
            return {
                "exposed_ip": spec.get("clusterIP"),
                "service_type": spec.get("type", "ClusterIP")
            }

        return {"exposed_ip": None, "service_type": spec.get("type", "ClusterIP")}

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get exposed IP for service: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get exposed IP for service: {str(e)}"
        )

@router.post("/{name}/expose")
def expose_service(
    name: str,
    service_type: str = "NodePort",
    port: Optional[int] = None,
    target_port: Optional[int] = None,
    namespace: str = "default",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Expose a deployment as a service
    """
    try:
        cmd = ["kubectl", "expose", "deployment", name, "-n", namespace, f"--type={service_type}"]

        if port:
            cmd.append(f"--port={port}")
        if target_port:
            cmd.append(f"--target-port={target_port}")

        cmd.append(f"--name={name}-svc")

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        return {
            "message": f"Deployment {name} exposed as service {name}-svc",
            "service_type": service_type,
            "port": port,
            "target_port": target_port
        }

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to expose service: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to expose service: {str(e)}"
        )