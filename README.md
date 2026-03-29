# 🚀 FastAPI Observability Stack

A production-ready template for running a FastAPI application with built-in observability using:

- 📈 Prometheus (metrics)
- 📊 Grafana (visualization)
- 🔍 Jaeger (tracing)

The project uses modern Python packaging with uv, Docker, and a Makefile-driven workflow for simplicity and reproducibility.

---

## 📚 Table of Contents

- Overview
- Architecture
- Requirements
- Getting Started
- Makefile Commands
- Observability Stack
- Project Structure
- Best Practices
- License


---

## 🧭 Overview

This repository provides a clean and scalable setup for:

- Running a FastAPI application with middleware support
- Installing dependencies using uv
- Observing your application via metrics, logs, and traces
- Managing everything through a simple Makefile interface

---

## 🏗️ Architecture

```
┌────────────┐       ┌──────────────┐
│  FastAPI   │──────▶│  Prometheus  │
│   (App)    │       └──────┬───────┘
└─────┬──────┘              │
      │                     ▼
      │              ┌────────────┐
      │              │  Grafana   │
      │              └────────────┘
      ▼
┌────────────┐
│   Jaeger   │
└────────────┘
```

---

## ⚙️ Requirements

- Docker
- Docker Compose
- Make
- Python 3.13 (for local development)
- uv (Python package manager)

---

## 🚀 Getting Started

Clone the repository:

```bash
git clone <your-repo-url>
cd <your-repo>
```

Start the full stack using Make:

```bash
make up
```

This will:

- Build the Docker images
- Install dependencies using uv
- Start FastAPI
- Start Prometheus, Grafana, and Jaeger

---

## 🛠️ Makefile Commands

The project is fully managed via Makefile:

| Command | Description |
|----------------|--------------------------------------|
| make up | Start all services |
| make down | Stop all services |
| make build | Build Docker images |
| make logs | Show logs |
| make restart | Restart the stack |

Example:

```bash
make down && make up
```

---

## 📊 Observability Stack

Once running, access the services:

| Service | URL                     |
|------------|-------------------------|
| FastAPI | http://localhost:8000   |
| Grafana | http://localhost:3000   |
| Prometheus | http://localhost:9090   |
| Jaeger | http://localhost:16686  |


### 🔍 Features

- Middleware-based request tracing
- Prometheus metrics endpoint (/metrics)
- Distributed tracing with Jaeger
- Dashboards in Grafana

---

## 📁 Project Structure

```
.
├── src/
│   └── your_package/
│       ├── __main__.py
│       ├── api/
│       └── middleware/
├── cfg/
├── docker/
├── pyproject.toml
├── Makefile
└── README.md
```

---

## ✅ Best Practices

- Use uv for fast and reproducible dependency management
- Follow src/ layout for Python packaging
- Keep runtime images minimal (multi-stage builds recommended)
- Avoid using PYTHONPATH in production
- Instrument your app early (metrics + tracing)
- Use Makefile to standardize workflows

---

## 📄 License

This project is licensed under the MIT License.
