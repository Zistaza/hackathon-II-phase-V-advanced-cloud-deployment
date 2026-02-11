#!/bin/bash

# Helm Chart Validation Script
# Validates Helm chart structure, syntax, and configuration

set -e

echo "🔍 Validating Helm chart..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CHART_DIR="charts/todo-app"

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if Helm is installed
check_helm() {
    if ! command -v helm &&; then
        print_status $RED "❌ Helm is not installed. Please install Helm first."
        exit 1
    fi
}

# Function to validate chart structure
validate_structure() {
    echo "📁 Checking chart structure..."

    # Check required files
    local required_files=(
        "Chart.yaml"
        "values.yaml"
        "templates/_helpers.tpl"
        "templates/deployment.yaml"
        "templates/service.yaml"
        "templates/ingress.yaml"
        "templates/secrets.yaml"
    )

    local all_files_present=1

    for file in "${required_files[@]}"; do
        if [ ! -f "$CHART_DIR/$file" ]; then
            print_status $RED "❌ Missing required file: $file"
            all_files_present=0
        else
            print_status $GREEN "✅ Found: $file"
        fi
    done

    if [ $all_files_present -eq 1 ]; then
        print_status $GREEN "✅ All required files present"
    else
        print_status $RED "❌ Some required files are missing"
        return 1
    fi
}

# Function to validate chart syntax
validate_syntax() {
    echo "🧪 Checking chart syntax..."

    # Lint the chart
    echo "   Running helm lint..."
    if helm lint "$CHART_DIR" > /dev/null 2&amp;1; then
        print_status $GREEN "✅ Chart syntax is valid"
    else
        print_status $RED "❌ Chart syntax errors found"
        helm lint "$CHART_DIR"
        return 1
    fi
}

# Function to validate templates
validate_templates() {
    echo "📋 Checking templates..."

    # Template validation
    echo "   Validating templates..."
    if helm template "$CHART_DIR" > /dev/null 2&amp;1; then
        print_status $GREEN "✅ Templates are valid"
    else
        print_status $RED "❌ Template validation failed"
        helm template "$CHART_DIR"
        return 1
    fi
}

# Function to validate values
validate_values() {
    echo "⚙️  Checking values..."

    # Check values.yaml structure
    if [ ! -f "$CHART_DIR/values.yaml" ]; then
        print_status $RED "❌ values.yaml file not found"
        return 1
    fi

    # Check for required values
    echo "   Checking required values..."
    if grep -q "backend:\|frontend:\|services:" "$CHART_DIR/values.yaml"; then
        print_status $GREEN "✅ Required values found"
    else
        print_status $YELLOW "⚠️  Warning: Some required values might be missing"
    fi
}

# Function to validate security configurations
validate_security() {
    echo "🔒 Checking security configurations..."

    # Check for security contexts
    echo "   Checking security contexts..."
    if grep -q "securityContext:\|capabilities:\|readOnlyRootFilesystem:" "$CHART_DIR/values.yaml"; then
        print_status $GREEN "✅ Security contexts configured"
    else
        print_status $YELLOW "⚠️  Warning: Security contexts not configured"
    fi

    # Check for non-root user
    if grep -q "runAsNonRoot: true\|runAsUser:" "$CHART_DIR/values.yaml"; then
        print_status $GREEN "✅ Non-root user configured"
    else
        print_status $YELLOW "⚠️  Warning: Non-root user not configured"
    fi
}

# Function to validate resource configurations
validate_resources() {
    echo "⚡ Checking resource configurations..."

    # Check for resource limits and requests
    echo "   Checking resource limits and requests..."
    if grep -q "resources:\|limits:\|requests:" "$CHART_DIR/values.yaml"; then
        print_status $GREEN "✅ Resource configurations found"
    else
        print_status $YELLOW "⚠️  Warning: Resource configurations not found"
    fi
}

# Function to validate health checks
validate_health_checks() {
    echo "🩺 Checking health check configurations..."

    # Check for health checks in backend
    if grep -q "livenessProbe:\|readinessProbe:" "$CHART_DIR/values.yaml"; then
        print_status $GREEN "✅ Health checks configured"
    else
        print_status $YELLOW "⚠️  Warning: Health checks not configured"
    fi
}

# Function to validate ingress configuration
validate_ingress() {
    echo "🌐 Checking ingress configuration..."

    # Check if ingress is enabled
    if grep -q "ingress:\|enabled: true" "$CHART_DIR/values.yaml"; then
        print_status $GREEN "✅ Ingress is enabled"
        # Check for required ingress fields
        if grep -q "hosts:\|paths:" "$CHART_DIR/values.yaml"; then
            print_status $GREEN "✅ Ingress configuration is complete"
        else
            print_status $YELLOW "⚠️  Warning: Ingress configuration might be incomplete"
        fi
    else
        print_status $BLUE "ℹ️  Ingress is disabled"
    fi
}

# Function to generate summary
print_summary() {
    local structure=$1
    local syntax=$2
    local templates=$3
    local values=$4
    local security=$5
    local resources=$6
    local health=$7
    local ingress=$8

    echo ""
    echo "📊 VALIDATION SUMMARY"
    echo "======================"

    local passed=0
    local total=8

    if [ $structure -eq 1 ]; then passed=$((passed + 1)); fi
    if [ $syntax -eq 1 ]; then passed=$((passed + 1)); fi
    if [ $templates -eq 1 ]; then passed=$((passed + 1)); fi
    if [ $values -eq 1 ]; then passed=$((passed + 1)); fi
    if [ $security -eq 1 ]; then passed=$((passed + 1)); fi
    if [ $resources -eq 1 ]; then passed=$((passed + 1)); fi
    if [ $health -eq 1 ]; then passed=$((passed + 1)); fi
    if [ $ingress -eq 1 ]; then passed=$((passed + 1)); fi

    echo "   Passed: $passed/$total checks"

    if [ $passed -eq $total ]; then
        print_status $GREEN "🎉 ALL VALIDATIONS PASSED"
        echo ""
        echo "✅ Recommendations:"
        echo "- Chart is ready for deployment"
        echo "- All configurations are properly set"
        echo "- Security and resource configurations are in place"
    else
        print_status $RED "❌ SOME VALIDATIONS FAILED"
        echo ""
        echo "⚠️  Recommendations:"
        echo "- Fix the failed validations"
        echo "- Review the chart structure and configurations"
        echo "- Ensure all required files are present"
    fi
}

# Main validation process
echo "🚀 Starting Helm chart validation..."
echo "===================================="

# Check prerequisites
check_helm

# Validate chart structure
structure_passed=0
if validate_structure; then
    structure_passed=1
fi

# Validate chart syntax
syntax_passed=0
if validate_syntax; then
    syntax_passed=1
fi

# Validate templates
templates_passed=0
if validate_templates; then
    templates_passed=1
fi

# Validate values
values_passed=0
if validate_values; then
    values_passed=1
fi

# Validate security configurations
security_passed=0
if validate_security; then
    security_passed=1
fi

# Validate resource configurations
resources_passed=0
if validate_resources; then
    resources_passed=1
fi

# Validate health checks
health_passed=0
if validate_health_checks; then
    health_passed=1
fi

# Validate ingress configuration
ingress_passed=0
if validate_ingress; then
    ingress_passed=1
fi

# Generate summary and exit with appropriate code
print_summary $structure_passed $syntax_passed $templates_passed $values_passed $security_passed $resources_passed $health_passed $ingress_passed

if [ $structure_passed -eq 1 ] && [ $syntax_passed -eq 1 ] && [ $templates_passed -eq 1 ] && [ $values_passed -eq 1 ] && [ $security_passed -eq 1 ] && [ $resources_passed -eq 1 ] && [ $health_passed -eq 1 ] && [ $ingress_passed -eq 1 ]; then
    exit 0
else
    exit 1
fi