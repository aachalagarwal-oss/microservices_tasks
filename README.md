Microservices Task Management System (API Gateway + Auth + User + Task)

Services
1) API Gateway (Port 8000)

Responsibilities:

Single entry point for frontend

Validates JWT token via Auth Service

Forwards requests to correct service

Returns response unchanged (transparent proxy)

Routes exposed to client:

GET /users/me

GET /tasks

POST /tasks

GET /tasks/{id}

PUT /tasks/{id}

DELETE /tasks/{id}

2) Auth Service (Port 8001)

Responsibilities:

Register user

Login user

Generate JWT token

Validate token (used by gateway)

Important endpoint:

POST /auth/validate-token

Gateway depends on this endpoint for authentication.

3) User Service (Port 8002)

Responsibilities:

Manage user profile

Return logged-in user details

Endpoint used by gateway:

GET /users/me

4) Task Service (Port 8003)

Responsibilities:

CRUD operations for tasks

Task ownership per user

Endpoints used by gateway:

GET /tasks

POST /tasks

GET /tasks/{id}

PUT /tasks/{id}

DELETE /tasks/{id}