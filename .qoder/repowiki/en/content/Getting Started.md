# Getting Started

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [backend/requirements.txt](file://backend/requirements.txt)
- [backend/app.py](file://backend/app.py)
- [backend/models.py](file://backend/models.py)
- [backend/crawler.py](file://backend/crawler.py)
- [frontend/package.json](file://frontend/package.json)
- [frontend/vite.config.js](file://frontend/vite.config.js)
- [frontend/src/main.js](file://frontend/src/main.js)
- [frontend/src/App.vue](file://frontend/src/App.vue)
- [.github/workflows/crawler.yml](file://.github/workflows/crawler.yml)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Project Structure](#project-structure)
4. [Local Development Setup](#local-development-setup)
5. [Environment Configuration](#environment-configuration)
6. [Development Workflow](#development-workflow)
7. [Verification Steps](#verification-steps)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
This guide helps you set up and run the News Aggregator application locally. It covers backend (Flask API) and frontend (Vue 3) components, environment setup, dependency installation, and initial startup procedures. You will learn how to run both servers simultaneously, configure the development proxy, and verify that everything works as expected.

## Prerequisites
Before starting, ensure you have the following installed on your development machine:

- Python 3.x (tested with Python 3.11 in CI)
- Node.js and npm (for frontend development)
- Git (recommended for cloning the repository)

These requirements are sufficient to run both the backend Flask API and the Vue.js frontend in development mode.

**Section sources**
- [README.md:28-47](file://README.md#L28-L47)
- [.github/workflows/crawler.yml:17-21](file://.github/workflows/crawler.yml#L17-L21)

## Project Structure
The repository is organized into two main parts:

- backend: Flask API server, database models, and RSS crawler
- frontend: Vue 3 SPA with Vite development server and proxy configuration

```mermaid
graph TB
subgraph "Backend"
A["backend/app.py<br/>Flask API"]
B["backend/models.py<br/>SQLAlchemy models"]
C["backend/crawler.py<br/>RSS crawler"]
D["backend/requirements.txt<br/>Python dependencies"]
end
subgraph "Frontend"
E["frontend/src/main.js<br/>Vue app entry"]
F["frontend/src/App.vue<br/>Main component"]
G["frontend/package.json<br/>NPM scripts and deps"]
H["frontend/vite.config.js<br/>Vite dev server + proxy"]
end
A --> B
C --> B
E --> F
H --> A
```

**Diagram sources**
- [backend/app.py:1-87](file://backend/app.py#L1-L87)
- [backend/models.py:1-39](file://backend/models.py#L1-L39)
- [backend/crawler.py:1-217](file://backend/crawler.py#L1-L217)
- [frontend/src/main.js:1-5](file://frontend/src/main.js#L1-L5)
- [frontend/src/App.vue:1-421](file://frontend/src/App.vue#L1-L421)
- [frontend/package.json:1-19](file://frontend/package.json#L1-L19)
- [frontend/vite.config.js:1-17](file://frontend/vite.config.js#L1-L17)

**Section sources**
- [README.md:5-26](file://README.md#L5-L26)

## Local Development Setup
Follow these step-by-step instructions to prepare your local environment.

### Backend Setup
1. Navigate to the backend directory.
2. Create a Python virtual environment.
3. Activate the virtual environment.
4. Install Python dependencies from requirements.txt.
5. Initialize the database and start the Flask API server.

Key commands and locations:
- Virtual environment creation and activation
- Installing dependencies
- Starting the Flask server

**Section sources**
- [README.md:30-39](file://README.md#L30-L39)
- [backend/requirements.txt:1-8](file://backend/requirements.txt#L1-L8)

### Frontend Setup
1. Navigate to the frontend directory.
2. Install Node.js dependencies using npm.
3. Start the Vite development server.

Key commands and locations:
- Installing dependencies
- Starting the development server

**Section sources**
- [README.md:41-47](file://README.md#L41-L47)
- [frontend/package.json:6-10](file://frontend/package.json#L6-L10)

## Environment Configuration
Configure your development environment to support both backend and frontend servers.

### Backend Database Configuration
- The Flask app uses SQLite and stores the database file under the backend directory.
- The database URI is constructed dynamically based on the backend directory path.

Important paths and configuration:
- Database file location
- Application configuration for SQLite

**Section sources**
- [backend/app.py:12-18](file://backend/app.py#L12-L18)

### Frontend Proxy Configuration
- Vite proxies API requests from the frontend to the backend Flask server.
- The proxy target is configured to forward requests from /api to http://localhost:5001.

Proxy behavior:
- Requests to /api/* are proxied to the backend
- Port 3000 is used by Vite dev server
- Port 5001 is used by Flask API server

**Section sources**
- [frontend/vite.config.js:7-16](file://frontend/vite.config.js#L7-L16)
- [backend/app.py:84-87](file://backend/app.py#L84-L87)

### Frontend API Base URL
- The frontend reads an environment variable to determine the API base URL.
- In development, the proxy handles API routing; in production, you can set VITE_API_BASE to override the base URL.

Environment variable usage:
- VITE_API_BASE for overriding API base URL

**Section sources**
- [frontend/src/App.vue:119-121](file://frontend/src/App.vue#L119-L121)

## Development Workflow
Run the backend and frontend servers concurrently during development.

### Step-by-step Workflow
1. Start the Flask API server in the backend directory.
2. Start the Vite development server in the frontend directory.
3. Access the frontend at http://localhost:3000.
4. The frontend will proxy API requests to http://localhost:5001.

### How the Proxy Works
```mermaid
sequenceDiagram
participant Browser as "Browser"
participant Vite as "Vite Dev Server (Port 3000)"
participant Proxy as "Vite Proxy Config"
participant Flask as "Flask API (Port 5001)"
Browser->>Vite : "GET /api/news?page=1"
Vite->>Proxy : "Forward request"
Proxy->>Flask : "GET http : //localhost : 5001/api/news?page=1"
Flask-->>Proxy : "JSON response"
Proxy-->>Vite : "Pass-through response"
Vite-->>Browser : "JSON response"
```

**Diagram sources**
- [frontend/vite.config.js:9-14](file://frontend/vite.config.js#L9-L14)
- [backend/app.py:21-55](file://backend/app.py#L21-L55)

**Section sources**
- [README.md:28-47](file://README.md#L28-L47)
- [frontend/vite.config.js:7-16](file://frontend/vite.config.js#L7-L16)
- [backend/app.py:84-87](file://backend/app.py#L84-L87)

## Verification Steps
After starting both servers, verify that the application is functioning correctly.

### Backend Health Check
- Access the health endpoint to confirm the backend is running.
- Expected response indicates the service is healthy.

Endpoint:
- GET /api/health

**Section sources**
- [backend/app.py:71-75](file://backend/app.py#L71-L75)

### Fetch News Data
- Load the frontend at http://localhost:3000.
- The frontend will automatically fetch news items from the backend.
- Verify that news cards appear and pagination controls are functional.

Frontend behavior:
- Automatic fetch on mount
- Category and sort options
- Pagination navigation

**Section sources**
- [frontend/src/App.vue:122-146](file://frontend/src/App.vue#L122-L146)
- [frontend/src/App.vue:164-166](file://frontend/src/App.vue#L164-L166)

### Database Initialization
- On first run, the backend initializes the SQLite database and creates tables.
- Confirm that the database file is created in the backend directory.

Initialization:
- Creates all tables defined in models
- Prints initialization message

**Section sources**
- [backend/app.py:77-82](file://backend/app.py#L77-L82)
- [backend/models.py:10-39](file://backend/models.py#L10-L39)

## Troubleshooting Guide
Common issues and their solutions during local development.

### Backend Issues
- Port conflicts: Flask defaults to port 5001. If this port is in use, adjust the port in the Flask server configuration.
- Database permissions: Ensure write permissions to the backend directory so the SQLite file can be created.
- Missing virtual environment: Always activate the Python virtual environment before installing dependencies.

**Section sources**
- [backend/app.py:84-87](file://backend/app.py#L84-L87)
- [backend/app.py:12-18](file://backend/app.py#L12-L18)

### Frontend Issues
- Proxy not forwarding requests: Verify the proxy target in Vite config points to the correct backend address and port.
- Node/npm not found: Ensure Node.js and npm are installed and available in your PATH.
- Missing dependencies: Reinstall frontend dependencies if the build fails.

**Section sources**
- [frontend/vite.config.js:9-14](file://frontend/vite.config.js#L9-L14)
- [frontend/package.json:6-10](file://frontend/package.json#L6-L10)

### Network and CORS
- Cross-origin errors: The backend enables CORS globally. If you encounter CORS issues, verify that the frontend and backend ports match the proxy configuration.
- API base URL: In development, the proxy handles routing; in production, set VITE_API_BASE if you need to override the base URL.

**Section sources**
- [backend/app.py:9-10](file://backend/app.py#L9-L10)
- [frontend/src/App.vue:119-121](file://frontend/src/App.vue#L119-L121)

## Conclusion
You now have the necessary steps to set up and run the News Aggregator application locally. By following the backend and frontend setup instructions, configuring the proxy, and verifying the health and data endpoints, you can develop and test features efficiently. For ongoing updates, the RSS crawler runs automatically via GitHub Actions daily, keeping the database fresh.