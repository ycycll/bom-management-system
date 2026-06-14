# BOM Management System

The BOM (Bill of Materials) Management System is a full-stack management platform built with a FastAPI backend and Vue 3 frontend, designed to help enterprises efficiently manage material lists and associated agreement documents. The system integrates AI-assisted features such as intelligent recommendation algorithms and data validation/cleaning, making it suitable for applications in manufacturing, project management, and similar fields.

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.10, FastAPI, Pydantic |
| Frontend | Vue 3, Vite, Element Plus |
| Database | MongoDB (configuration file located at `back/db/config.py`) |

## Functional Modules

### 1. Sample Management (Sample)
Manage various types of material sample data, supporting filtering and querying by type, voltage, frequency, material, and other criteria. Provides comprehensive CRUD interfaces.

### 2. Agreement Management (Agreement)
Manage and maintain cooperation agreements, technical agreements, and other documents. Supports keyword search, pagination, and version updates.

### 3. Copilot (Intelligent Assistant)
- **File Upload**: Supports uploading and parsing technical documents
- **Intelligent Recommendations**: Recommends suitable materials or solutions based on technical readiness, product type, environmental conditions, and other factors
- **Data Validation**: Automatically validates and verifies material data
- **Data Maintenance**: Bulk processing and maintenance of material data

### 4. Intelligent Q&A (Defog)
A question-answering module based on RAG (Retrieval-Augmented Generation) technology, enabling intelligent queries against technical documentation.

### 5. Drawing Management (Drawing)
Manage technical drawing files, supporting search by name and remarks, and retrieval of drawing content.

### 6. Hub Management
Centralized management of recommendation data, supporting conditional filtering, deletion, and other operations.

### 7. Data Validation Tool
Provides standard feature cleaning and validation functions, including:
- Removal of common values
- Description field validation
- Detection of non-standard configurations

## Project Structure

```
bom-management-system/
├── back/                    # Backend service
│   ├── crud/               # Business interface layer
│   │   ├── agreement.py    # Agreement management
│   │   ├── copilot.py      # Intelligent assistant
│   │   ├── defog.py        # Intelligent Q&A
│   │   ├── draw.py         # Drawing management
│   │   ├── hub.py          # Hub management
│   │   ├── tool_function.py # Utility functions
│   │   └── we.py           # Sample management
│   ├── db/                # Database configuration
│   ├── model.py           # Data model definitions
│   ├── main.py            # Application entry point
│   └── static/            # Static resources
│
└── front/                 # Frontend application
    ├── src/
    │   ├── views/        # Page views
    │   │   ├── agreement.vue
    │   │   ├── copilot.vue
    │   │   ├── defog.vue
    │   │   ├── draw.vue
    │   │   ├── home.vue
    │   │   ├── hub.vue
    │   │   ├── login.vue
    │   │   └── sample.vue
    │   ├── component/    # Common components
    │   ├── router/       # Routing configuration
    │   └── main.js       # Application entry point
    └── package.json
```

## Quick Start

### Start Backend

```bash
cd back
pip install -r requirements.txt  # Install dependencies
uvicorn main:app --reload        # Start server
```

The backend service runs by default at `http://localhost:8000`

### Start Frontend

```bash
cd front
npm install
npm run dev
```

The frontend runs by default at `http://localhost:5173`

## API Documentation

After starting the services, access the following URLs to view the API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

Please refer to the LICENSE file in the project root directory for licensing information.