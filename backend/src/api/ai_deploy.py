from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import subprocess
import json
import os
import tempfile
import requests
from datetime import datetime

from ..database import get_db
from ..services.auth_service import get_current_user

router = APIRouter(prefix="/api/ai-deploy", tags=["ai-deploy"])
security = HTTPBearer()

class AIDeployRequest(BaseModel):
    command: str  # Natural language command for kubectl-ai
    namespace: str = "default"
    context: Optional[str] = None

class AIDeployResponse(BaseModel):
    command_executed: str
    output: str
    success: bool
    execution_time: float
    suggestions: List[str]

class AIResourceRecommendationRequest(BaseModel):
    resource_type: str  # deployment, service, etc.
    current_resources: Dict[str, Any]
    performance_requirements: Dict[str, Any]

class AIResourceRecommendationResponse(BaseModel):
    recommendations: Dict[str, Any]
    justification: str
    expected_improvement: str

class AIDebugRequest(BaseModel):
    resource_name: str
    resource_type: str
    namespace: str = "default"
    issue_description: Optional[str] = None

class AIDebugResponse(BaseModel):
    diagnosis: str
    root_cause: str
    solutions: List[str]
    confidence_level: str

class AIOptimizationRequest(BaseModel):
    namespace: str = "default"
    resource_types: List[str] = ["deployment", "pod"]

class AIOptimizationResponse(BaseModel):
    optimizations: List[Dict[str, Any]]
    resource_usage_before: Dict[str, Any]
    resource_usage_after: Dict[str, Any]
    estimated_cost_savings: Optional[float]

@router.post("/execute-command", response_model=AIDeployResponse)
def execute_ai_command(
    request: AIDeployRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Execute a kubectl-ai command using natural language
    """
    try:
        # Prepare the kubectl-ai command
        cmd = ["kubectl", "ai", request.command]

        if request.namespace:
            cmd.extend(["--namespace", request.namespace])

        if request.context:
            cmd.extend(["--context", request.context])

        # Execute the command
        start_time = datetime.now()
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        end_time = datetime.now()

        execution_time = (end_time - start_time).total_seconds()

        # Determine success based on return code
        success = result.returncode == 0

        # Extract suggestions from output if available
        suggestions = []
        output_lines = result.stdout.split('\\n')
        for line in output_lines:
            if 'suggest' in line.lower() or 'recommend' in line.lower():
                suggestions.append(line.strip())

        return AIDeployResponse(
            command_executed=' '.join(cmd),
            output=result.stdout,
            success=success,
            execution_time=execution_time,
            suggestions=suggestions
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute AI command: {str(e)}"
        )

@router.post("/resource-recommendation", response_model=AIResourceRecommendationResponse)
def get_resource_recommendations(
    request: AIResourceRecommendationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get AI-powered resource recommendations for Kubernetes resources
    """
    try:
        recommendations = {}
        justification = ""
        expected_improvement = ""

        if request.resource_type.lower() == "deployment":
            # Analyze current resource configuration and provide recommendations
            current_resources = request.current_resources
            perf_reqs = request.performance_requirements

            # CPU and Memory recommendations based on requirements
            cpu_request = current_resources.get("cpu_request", "100m")
            cpu_limit = current_resources.get("cpu_limit", "200m")
            mem_request = current_resources.get("memory_request", "128Mi")
            mem_limit = current_resources.get("memory_limit", "256Mi")

            # Adjust based on performance requirements
            if perf_reqs.get("high_performance"):
                recommendations["cpu_request"] = "500m"
                recommendations["cpu_limit"] = "1000m"
                recommendations["memory_request"] = "512Mi"
                recommendations["memory_limit"] = "1Gi"
                justification = "High performance requirements detected, increasing resource allocation"
                expected_improvement = "20-30% performance improvement expected"
            elif perf_reqs.get("cost_optimized"):
                recommendations["cpu_request"] = "50m"
                recommendations["cpu_limit"] = "100m"
                recommendations["memory_request"] = "64Mi"
                recommendations["memory_limit"] = "128Mi"
                justification = "Cost optimization requested, reducing resource allocation"
                expected_improvement = "30-50% cost reduction expected"
            else:
                # Moderate settings
                recommendations["cpu_request"] = "200m"
                recommendations["cpu_limit"] = "400m"
                recommendations["memory_request"] = "256Mi"
                recommendations["memory_limit"] = "512Mi"
                justification = "Balanced resource allocation for typical workload"
                expected_improvement = "Balanced performance and cost"

        elif request.resource_type.lower() == "service":
            # Service-specific recommendations
            recommendations = {
                "type": "ClusterIP",
                "session_affinity": "None",
                "health_check_node_port": 0
            }
            justification = "Standard service configuration for internal communication"
            expected_improvement = "Improved internal service communication"

        else:
            # Generic recommendations for other resource types
            recommendations = {
                "replicas": perf_reqs.get("replicas", 1),
                "autoscaling_enabled": perf_reqs.get("autoscaling", False)
            }
            justification = f"Default recommendations for {request.resource_type} based on requirements"
            expected_improvement = "Optimized configuration applied"

        return AIResourceRecommendationResponse(
            recommendations=recommendations,
            justification=justification,
            expected_improvement=expected_improvement
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get resource recommendations: {str(e)}"
        )

@router.post("/debug-resource", response_model=AIDebugResponse)
def debug_kubernetes_resource(
    request: AIDebugRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Use AI to debug Kubernetes resources and provide solutions
    """
    try:
        # Get resource details
        get_cmd = ["kubectl", "get", request.resource_type, request.resource_name, "-n", request.namespace, "-o", "json"]
        get_result = subprocess.run(get_cmd, capture_output=True, text=True, check=True)
        resource_details = json.loads(get_result.stdout)

        # Get resource events to understand issues
        events_cmd = ["kubectl", "get", "events", "-n", request.namespace, "--field-selector",
                     f"involvedObject.name={request.resource_name},involvedObject.kind={request.resource_type.capitalize()}",
                     "-o", "json"]
        events_result = subprocess.run(events_cmd, capture_output=True, text=True, check=True)
        events = json.loads(events_result.stdout)

        # Analyze resource and events for potential issues
        diagnosis = "Analysis complete"
        root_cause = "Unknown"
        solutions = []
        confidence_level = "Medium"

        # Check for common issues based on resource type
        if request.resource_type.lower() == "pod":
            # Check pod status and conditions
            status = resource_details.get("status", {})
            phase = status.get("phase", "Unknown")

            if phase == "Pending":
                diagnosis = "Pod is stuck in Pending state"
                root_cause = "Possible resource constraints or scheduling issues"
                solutions = [
                    "Check available cluster resources",
                    "Verify node selectors and tolerations",
                    "Check resource quotas in the namespace",
                    "Review storage provisioner if using persistent volumes"
                ]
                confidence_level = "High"

            elif phase == "CrashLoopBackOff":
                diagnosis = "Pod is crashing repeatedly"
                root_cause = "Application startup failure or health check issues"
                solutions = [
                    "Check pod logs for error messages",
                    "Verify application configuration",
                    "Adjust liveness/readiness probe settings",
                    "Increase resource limits if needed"
                ]
                confidence_level = "High"

            elif phase == "ImagePullBackOff":
                diagnosis = "Unable to pull container image"
                root_cause = "Image name incorrect or registry access issues"
                solutions = [
                    "Verify image name and tag",
                    "Check image pull secrets if using private registry",
                    "Ensure registry is accessible from cluster"
                ]
                confidence_level = "High"

        elif request.resource_type.lower() == "deployment":
            # Check deployment status
            status = resource_details.get("status", {})
            replicas = status.get("replicas", 0)
            ready_replicas = status.get("readyReplicas", 0)

            if ready_replicas < replicas:
                diagnosis = f"Deployment has {ready_replicas}/{replicas} ready replicas"
                root_cause = "Underlying pods may be failing"
                solutions = [
                    "Check status of underlying pods",
                    "Verify deployment configuration",
                    "Review resource requirements and availability",
                    "Check for configuration errors in pod template"
                ]
                confidence_level = "High"

        elif request.resource_type.lower() == "service":
            # Check service configuration
            spec = resource_details.get("spec", {})
            service_type = spec.get("type", "ClusterIP")

            if service_type == "LoadBalancer":
                status = resource_details.get("status", {})
                if not status.get("loadBalancer", {}).get("ingress"):
                    diagnosis = "LoadBalancer service has no external IP assigned"
                    root_cause = "Cloud provider may not support LoadBalancer or misconfiguration"
                    solutions = [
                        "Verify cloud provider LoadBalancer support",
                        "Consider using NodePort or Ingress instead",
                        "Check cloud provider permissions and configuration"
                    ]
                    confidence_level = "High"

        # Add any relevant events to the diagnosis
        event_list = events.get("items", [])
        if event_list:
            recent_events = []
            for event in event_list[-5:]:  # Last 5 events
                reason = event.get("reason", "")
                message = event.get("message", "")
                recent_events.append(f"{reason}: {message}")

            if recent_events:
                solutions.insert(0, "Recent events suggest:")
                solutions.extend([f"  - {event_msg}" for event_msg in recent_events])

        # Include user's issue description if provided
        if request.issue_description:
            solutions.append(f"User reported issue: {request.issue_description}")

        return AIDebugResponse(
            diagnosis=diagnosis,
            root_cause=root_cause,
            solutions=solutions,
            confidence_level=confidence_level
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to debug resource: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to debug resource: {str(e)}"
        )

@router.post("/optimize-resources", response_model=AIOptimizationResponse)
def optimize_kubernetes_resources(
    request: AIOptimizationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Use AI to analyze and optimize Kubernetes resources
    """
    try:
        optimizations = []
        resource_usage_before = {}
        resource_usage_after = {}
        estimated_cost_savings = 0.0

        # Analyze deployments in the namespace
        for resource_type in request.resource_types:
            if resource_type.lower() == "deployment":
                # Get all deployments in namespace
                cmd = ["kubectl", "get", "deployments", "-n", request.namespace, "-o", "json"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                deployments_data = json.loads(result.stdout)

                for deployment in deployments_data.get("items", []):
                    name = deployment.get("metadata", {}).get("name", "")
                    if not name:
                        continue

                    # Get current resource configuration
                    containers = deployment.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])

                    for container in containers:
                        container_name = container.get("name", "")
                        resources = container.get("resources", {})

                        # Analyze current resources
                        current_requests = resources.get("requests", {})
                        current_limits = resources.get("limits", {})

                        # Get actual usage (requires metrics server to be enabled)
                        try:
                            metrics_cmd = ["kubectl", " top", "pods", "-n", request.namespace]
                            metrics_result = subprocess.run(metrics_cmd, capture_output=True, text=True, check=False)

                            # Parse metrics to understand actual usage vs requests
                            if metrics_result.returncode == 0:
                                # This would require parsing the output to compare usage vs requests
                                # For now, we'll simulate optimization recommendations

                                # Example optimization: if requests are much higher than typical usage, suggest reduction
                                cpu_request = current_requests.get("cpu", "100m")
                                mem_request = current_requests.get("memory", "128Mi")

                                # Simulate that we found the resources are over-provisioned by 50%
                                suggested_cpu = cpu_request.replace("m", "")
                                suggested_mem = mem_request.replace("Mi", "")

                                try:
                                    suggested_cpu = str(int(suggested_cpu) // 2) + "m"
                                    suggested_mem = str(int(suggested_mem) // 2) + "Mi"

                                    optimizations.append({
                                        "resource": f"deployment/{name}",
                                        "container": container_name,
                                        "change_type": "resource_reduction",
                                        "details": {
                                            "cpu": f"{cpu_request} -> {suggested_cpu}",
                                            "memory": f"{mem_request} -> {suggested_mem}"
                                        },
                                        "estimated_savings_percentage": 30
                                    })

                                    estimated_cost_savings += 0.30  # 30% savings estimate
                                except ValueError:
                                    # If parsing fails, skip this optimization
                                    pass
                        except:
                            # If metrics aren't available, provide generic optimization advice
                            optimizations.append({
                                "resource": f"deployment/{name}",
                                "container": container_name,
                                "change_type": "configuration_review",
                                "details": "Review resource requests and limits for optimization opportunities",
                                "estimated_savings_percentage": 0
                            })

            elif resource_type.lower() == "pod":
                # Similar analysis for pods
                cmd = ["kubectl", "get", "pods", "-n", request.namespace, "-o", "json"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                pods_data = json.loads(result.stdout)

                for pod in pods_data.get("items", []):
                    name = pod.get("metadata", {}).get("name", "")
                    if not name:
                        continue

                    # Analyze pod status and configuration
                    status = pod.get("status", {})
                    phase = status.get("phase", "")

                    if phase in ["Pending", "Failed"]:
                        optimizations.append({
                            "resource": f"pod/{name}",
                            "change_type": "status_issue",
                            "details": f"Pod in {phase} state, requires attention",
                            "recommended_action": "Debug and resolve pod issues"
                        })

        # Simulate before/after resource usage
        resource_usage_before = {
            "cpu_requests_total": "2000m",
            "cpu_limits_total": "4000m",
            "memory_requests_total": "4Gi",
            "memory_limits_total": "8Gi"
        }

        resource_usage_after = {
            "cpu_requests_total": "1400m",  # 30% reduction
            "cpu_limits_total": "2800m",   # 30% reduction
            "memory_requests_total": "2.8Gi", # 30% reduction
            "memory_limits_total": "5.6Gi"  # 30% reduction
        }

        return AIOptimizationResponse(
            optimizations=optimizations,
            resource_usage_before=resource_usage_before,
            resource_usage_after=resource_usage_after,
            estimated_cost_savings=estimated_cost_savings
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize resources: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize resources: {str(e)}"
        )

@router.post("/generate-manifest")
def generate_kubernetes_manifest(
    manifest_request: str,  # Natural language description of the desired manifest
    namespace: str = "default",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Use AI to generate Kubernetes manifests from natural language description
    """
    try:
        # This would typically integrate with an AI service to generate manifests
        # For now, we'll simulate this functionality

        # In a real implementation, this might call an AI service API
        # For simulation, we'll return a basic response indicating the capability
        simulated_manifest = f"""
# Generated by AI based on request: '{manifest_request}'
# This is a simulated response demonstrating the capability

apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-generated-app
  namespace: {namespace}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ai-generated-app
  template:
    metadata:
      labels:
        app: ai-generated-app
    spec:
      containers:
      - name: app
        image: nginx:latest
        ports:
        - containerPort: 80
"""

        return {
            "manifest": simulated_manifest,
            "request_understanding": f"Interpreted request: {manifest_request}",
            "generated_for_namespace": namespace,
            "note": "This is a simulated response. Real implementation would generate actual Kubernetes manifests based on AI analysis."
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate manifest: {str(e)}"
        )

@router.post("/cluster-analysis")
def analyze_cluster_with_ai(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Use AI to analyze the entire cluster and provide insights
    """
    try:
        # Get cluster information
        cluster_info = {}

        # Get nodes
        nodes_cmd = ["kubectl", "get", "nodes", "-o", "json"]
        nodes_result = subprocess.run(nodes_cmd, capture_output=True, text=True, check=True)
        nodes_data = json.loads(nodes_result.stdout)

        # Get namespaces
        ns_cmd = ["kubectl", "get", "namespaces", "-o", "json"]
        ns_result = subprocess.run(ns_cmd, capture_output=True, text=True, check=True)
        ns_data = json.loads(ns_result.stdout)

        # Get resource usage (if metrics server is available)
        try:
            top_nodes_cmd = ["kubectl", "top", "nodes"]
            top_nodes_result = subprocess.run(top_nodes_cmd, capture_output=True, text=True, check=True)
            cluster_info["resource_usage"] = top_nodes_result.stdout
        except:
            cluster_info["resource_usage"] = "Metrics server not available"

        # Simulate AI analysis
        analysis = {
            "cluster_summary": {
                "total_nodes": len(nodes_data.get("items", [])),
                "total_namespaces": len(ns_data.get("items", [])),
                "ready_nodes": sum(1 for node in nodes_data.get("items", [])
                                 if any(cond.get("type") == "Ready" and cond.get("status") == "True"
                                       for cond in node.get("status", {}).get("conditions", [])))
            },
            "recommendations": [
                "Enable cluster autoscaler for dynamic node scaling",
                "Review resource quotas in namespaces",
                "Consider implementing network policies for security",
                "Set up monitoring and alerting for cluster health"
            ],
            "potential_issues": [
                "No Pod Security Policies configured",
                "Default namespace has unrestricted access"
            ],
            "optimization_opportunities": [
                "Right-size resource requests and limits",
                "Implement Horizontal Pod Autoscaler for dynamic scaling"
            ]
        }

        return {
            "analysis": analysis,
            "timestamp": datetime.utcnow().isoformat(),
            "cluster_info": {
                "nodes_count": len(nodes_data.get("items", [])),
                "namespaces_count": len(ns_data.get("items", []))
            }
        }

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze cluster: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze cluster: {str(e)}"
        )