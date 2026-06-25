# Traplanner

## Introduction
Traplanner is an intelligent travel planning platform designed to generate personalized itineraries, recommend activities, and simplify the overall trip-planning process. By leveraging AI-driven agents and a dual-database architecture (MongoDB for fast document retrieval and Neo4j for geospatial/graph relationships), Traplanner provides optimized, reliable, and real-world grounded travel suggestions.

## Prerequisites
Before running the project, ensure you have the following installed:
- **Node.js** (v18 or higher)
- **Python** (v3.10 or higher)
- **Docker** (for running the Neo4j graph database)

## Installation and Setup

### 1. Database Setup (Neo4j)
Traplanner requires a Neo4j database to handle location graphs, routing, and spatial relationships.
```bash
# Start the Neo4j container
docker run -d \
    --name neo4j \
    --restart always \
    --publish=7474:7474 --publish=7687:7687 \
    --env NEO4J_AUTH=neo4j/12345678 \
    --volume=$(pwd)/SourceCode/neo4j-data:/data \
    neo4j:latest
```
*(Note: If you have a `.dump` backup file, make sure to load it into the database to restore the travel locations data).*

### 2. Backend Setup
The backend handles the AI agents, business logic, and API endpoints.

```bash
# Navigate to the backend directory
cd SourceCode/backend

# Activate the Python virtual environment
source .venv/bin/activate

# Install all the dependencies
uv sync

# Start the development server
python manage.py runserver 5000
```

### 3. Frontend Setup
The frontend provides the user interface, built with React and Vite.

```bash
# Navigate to the frontend directory
cd SourceCode/frontend

# Install dependencies
npm install

# Start the development server
npm run dev 
```

Once all services are running, open `http://localhost:5173` (or the port specified by Vite) in your browser to start using Traplanner!
