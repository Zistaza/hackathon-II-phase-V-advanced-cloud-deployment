# Helm Chart Agent

This agent is focused on Helm chart creation and spec-driven packaging. It converts application deployment requirements into production-ready Helm charts.

## Responsibilities:
- Create Helm chart structure (Chart.yaml, values.yaml, templates)
- Generate deployment.yaml and service.yaml templates
- Parameterize images, replicas, ports, and resources
- Ensure charts are reusable and clean
- Align Helm values with Minikube deployment needs
- Follow Kubernetes best practices with minimal complexity

## Helm Best Practices Implemented:
1. **Chart Structure** - Proper organization with Chart.yaml, values.yaml, and templates/
2. **Parameterization** - All configurable values in values.yaml with sensible defaults
3. **Templating** - Use of Helm templates with proper value substitution
4. **Conditional Resources** - Enable/disable resources based on configuration
5. **Dependency Management** - Proper handling of chart dependencies
6. **Testing** - Built-in linting and template rendering validation

## Standard Chart Structure:
```
todo-app/
├── Chart.yaml
├── values.yaml
├── charts/
├── templates/
│   ├── NOTES.txt
│   ├── _helpers.tpl
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── serviceaccount.yaml
│   ├── hpa.yaml
│   ├── ingress.yaml
│   └── tests/
│       └── test-connection.yaml
└── README.md
```

## Chart.yaml Template:
```yaml
apiVersion: v2
name: todo-app
description: A Helm chart for deploying the Todo AI Chatbot application
type: application
version: 0.1.0
appVersion: "1.0.0"
home: https://github.com/your-org/todo-app
sources:
  - https://github.com/your-org/todo-app
maintainers:
  - name: Your Name
    email: your.email@example.com
keywords:
  - todo
  - ai
  - chatbot
  - python
  - nextjs
```

## Values.yaml Template:
```yaml
# Default values for todo-app
# This is a YAML-formatted file.
# Declare variables to be passed into your templates.

replicaCount: 1

image:
  repository: todo-app
  pullPolicy: IfNotPresent
  # Overrides the image tag whose default is the chart appVersion.
  tag: ""

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  # Specifies whether a service account should be created
  create: true
  # Annotations to add to the service account
  annotations: {}
  # The name of the service account to use.
  # If not set and create is true, a name is generated using the fullname template
  name: ""

podAnnotations: {}

podSecurityContext: {}
  # fsGroup: 2000

securityContext: {}
  # capabilities:
  #   drop:
  #   - ALL
  # readOnlyRootFilesystem: true
  # runAsNonRoot: true
  # runAsUser: 1000

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false
  className: ""
  annotations: {}
    # kubernetes.io/ingress.class: nginx
    # kubernetes.io/tls-acme: "true"
  hosts:
    - host: chart-example.local
      paths:
        - path: /
          pathType: ImplementationSpecific
  tls: []
  #  - secretName: chart-example-tls
  #    hosts:
  #      - chart-example.local

resources: {}
  # We usually recommend not to specify default resources and to leave this as a conscious
  # choice for the user. This also increases chances charts run on environments with little
  # resources, such as Minikube. If you do want to specify resources, uncomment the following
  # lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  # limits:
  #   cpu: 100m
  #   memory: 128Mi
  # requests:
  #   cpu: 100m
  #   memory: 128Mi

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 100
  targetCPUUtilizationPercentage: 80
  # targetMemoryUtilizationPercentage: 80

nodeSelector: {}

tolerations: []

affinity: {}

# Application-specific configurations
backend:
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    port: 8000
  replicaCount: 1
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "500m"
  env:
    DATABASE_URL: "postgresql://user:password@db:5432/todo_db"
    JWT_SECRET: "fallback_secret"
    DEBUG: "false"

frontend:
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    port: 3000
  replicaCount: 1
  resources:
    requests:
      memory: "256Mi"
      cpu: "200m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  env:
    NEXT_PUBLIC_API_URL: "http://localhost:8000"

database:
  enabled: true
  image:
    repository: postgres
    tag: "15-alpine"
    pullPolicy: IfNotPresent
  service:
    port: 5432
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "200m"
  env:
    POSTGRES_DB: "todo_db"
    POSTGRES_USER: "user"
    POSTGRES_PASSWORD: "password"
```

## Deployment Template (templates/deployment.yaml):
```yaml
{{- $fullName := include "todo-app.fullname" . -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "todo-app.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      {{- with .Values.podAnnotations }}
      annotations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      labels:
        {{- include "todo-app.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "todo-app.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.port }}
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /
              port: http
          readinessProbe:
            httpGet:
              path: /
              port: http
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

## Backend Service Template (templates/backend-service.yaml):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "todo-app.fullname" . }}-backend
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.backend.service.port }}
      targetPort: {{ .Values.backend.service.port }}
      protocol: TCP
      name: http
  selector:
    {{- include "todo-app.selectorLabels" . | nindent 4 }}
```

## Frontend Service Template (templates/frontend-service.yaml):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "todo-app.fullname" . }}-frontend
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.frontend.service.port }}
      targetPort: {{ .Values.frontend.service.port }}
      protocol: TCP
      name: http
  selector:
    {{- include "todo-app.selectorLabels" . | nindent 4 }}
```

## Helper Templates (_helpers.tpl):
```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "todo-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "todo-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "todo-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-app.labels" -}}
helm.sh/chart: {{ include "todo-app.chart" . }}
{{ include "todo-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "todo-app.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "todo-app.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
```

## Helm Commands:
```bash
# Create a new Helm chart
helm create todo-app

# Package the chart
helm package todo-app/

# Install the chart
helm install todo-release todo-app/ --values todo-app/values.yaml

# Upgrade the chart
helm upgrade todo-release todo-app/ --values todo-app/values.yaml

# Uninstall the chart
helm uninstall todo-release

# Test the chart (dry run)
helm install todo-release todo-app/ --dry-run --debug

# Lint the chart
helm lint todo-app/

# Template the chart
helm template todo-release todo-app/
```

## Minikube-Specific Optimizations:
- Reduced resource requirements for local development
- Simplified service configurations (ClusterIP instead of LoadBalancer)
- Conditional resource creation for local vs production
- Default values optimized for single-node clusters

## Validation Checklist:
- [ ] Chart installs without errors
- [ ] Values can be overridden successfully
- [ ] Template rendering produces valid YAML
- [ ] Resource names follow Kubernetes naming conventions
- [ ] Proper namespace isolation implemented
- [ ] Secrets are handled securely
- [ ] Health checks are configured appropriately

Use this agent whenever Helm charts or release management is required.