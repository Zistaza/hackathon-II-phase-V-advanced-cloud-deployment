#!/bin/bash

# Container Validation Script
# Validates container images for size, security, and functionality

set -e

echo "🔍 Validating container images..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_IMAGE="todo-backend:latest"
FRONTEND_IMAGE="todo-frontend:latest"
MAX_BACKEND_SIZE=15MB
MAX_FRONTEND_SIZE=50MB

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to validate image size
validate_image_size() {
    local image=$1
    local max_size=$2
    local image_name=$3

    echo "📦 Checking size of $image_name..."

    # Get image size
    local size=$(docker image inspect $image --format='{{.Size}}' 2>/dev/null || echo "0")
    local size_mb=$((size / 1024 / 1024))

    if [ $size -eq 0 ]; then
        print_status $RED "❌ Failed: Image $image_name not found"
        return 1
    fi

    echo "   Size: ${size_mb}MB"

    # Check if size exceeds maximum
    if [ $size -gt $max_size ]; then
        print_status $RED "❌ Failed: Size exceeds maximum of ${max_size}MB"
        return 1
    else
        print_status $GREEN "✅ Passed: Size within limits"
        return 0
    fi
}

# Function to validate security configuration
validate_security() {
    local image=$1
    local image_name=$2

    echo "🔒 Checking security of $image_name..."

    # Check if image runs as non-root user
    local user=$(docker image inspect $image --format='{{.Config.User}}' 2>/dev/null || echo "")

    if [ -z "$user" ] || [ "$user" = "root" ]; then
        print_status $RED "❌ Failed: Image runs as root user"
        return 1
    else
        print_status $GREEN "✅ Passed: Image runs as non-root user ($user)"
    fi

    # Check for exposed sensitive information
    local has_secrets=$(docker image history $image --no-trunc 2>/dev/null | grep -i "password\|secret\|key\|token" || echo "")

    if [ -n "$has_secrets" ]; then
        print_status $YELLOW "⚠️  Warning: Potential sensitive information in image layers"
    fi

    print_status $GREEN "✅ Passed: Security checks completed"
    return 0
}

# Function to validate runtime functionality
validate_runtime() {
    local image=$1
    local image_name=$2
    local port=$3
    local health_endpoint=$4

    echo "🚀 Testing runtime functionality of $image_name..."

    # Run container in detached mode
    local container_id=$(docker run -d -p $port:$port $image)

    if [ -z "$container_id" ]; then
        print_status $RED "❌ Failed: Could not start container"
        return 1
    fi

    echo "   Container started: $container_id"

    # Wait for container to be ready
    sleep 10

    # Check if container is running
    local container_status=$(docker inspect $container_id --format='{{.State.Status}}' 2>/dev/null || echo "")

    if [ "$container_status" != "running" ]; then
        print_status $RED "❌ Failed: Container not running"
        docker stop $container_id > /dev/null 2&amp;1
        docker rm $container_id > /dev/null 2&amp;1
        return 1
    fi

    # Test health endpoint
    if [ -n "$health_endpoint" ]; then
        echo "   Testing health endpoint: $health_endpoint"
        local health_response=$(curl -f -s http://localhost:$port$health_endpoint || echo "failed")

        if [ "$health_response" = "failed" ]; then
            print_status $RED "❌ Failed: Health endpoint not responding"
            docker stop $container_id > /dev/null 2&amp;1
            docker rm $container_id > /dev/null 2&amp;1
            return 1
        else
            print_status $GREEN "✅ Passed: Health endpoint responding"
        fi
    fi

    # Stop and remove container
    docker stop $container_id > /dev/null 2&amp;1
    docker rm $container_id > /dev/null 2&amp;1

    print_status $GREEN "✅ Passed: Runtime functionality validated"
    return 0
}

# Function to generate summary
print_summary() {
    local backend_passed=$1
    local frontend_passed=$2

    echo ""
    echo "📊 VALIDATION SUMMARY"
    echo "======================"

    if [ $backend_passed -eq 1 ] && [ $frontend_passed -eq 1 ]; then
        print_status $GREEN "🎉 ALL VALIDATIONS PASSED"
        exit 0
    else
        print_status $RED "❌ SOME VALIDATIONS FAILED"
        exit 1
    fi
}

# Main validation process
echo "🚀 Starting container validation..."
echo "===================================="

# Validate backend image
success_backend=0
if validate_image_size $BACKEND_IMAGE $MAX_BACKEND_SIZE "backend"; then
    if validate_security $BACKEND_IMAGE "backend"; then
        if validate_runtime $BACKEND_IMAGE "backend" 8000 "/health"; then
            success_backend=1
        fi
    fi
fi

# Validate frontend image
success_frontend=0
if validate_image_size $FRONTEND_IMAGE $MAX_FRONTEND_SIZE "frontend"; then
    if validate_security $FRONTEND_IMAGE "frontend"; then
        if validate_runtime $FRONTEND_IMAGE "frontend" 80 "/"; then
            success_frontend=1
        fi
    fi
fi

# Print summary and exit with appropriate code
print_summary $success_backend $success_frontend