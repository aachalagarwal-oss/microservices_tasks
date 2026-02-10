from fastapi import FastAPI, Request, HTTPException, Depends, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx

app = FastAPI(title="API Gateway")

# ---------------- MICROSERVICE URLS ----------------
AUTH_SERVICE = "http://localhost:8001"
USER_SERVICE = "http://localhost:8002"
TASK_SERVICE = "http://localhost:8003"

# ---------------- SECURITY ----------------
security = HTTPBearer()  # Enables Swagger lock icon

async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validate the token with the auth service.
    Returns the user info if valid.
    """
    token = credentials.credentials
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{AUTH_SERVICE}/auth/validate-token",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Auth service unavailable")

        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")

        data = resp.json()
        data["token"] = token  # Keep token to forward it to other services
        return data

# ---------------- USER SERVICE PROXY ----------------
@app.get("/users/me", tags=["Users"])
async def proxy_me(user: dict = Depends(validate_token)):
    """
    Proxy GET /users/me to the user service
    """
    token = f"Bearer {user['token']}"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{USER_SERVICE}/users/me",
                headers={"Authorization": token},
                timeout=5.0,
                params=None,
            )
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="User service unavailable")

        # Return downstream response verbatim (status, headers, body)
        content = resp.content
        headers = {}
        if resp.headers.get("content-type"):
            headers["content-type"] = resp.headers.get("content-type")
        return Response(content=content, status_code=resp.status_code, headers=headers)

# ---------------- TASK SERVICE PROXY ----------------
async def _proxy_task_request(method: str, user: dict, path: str = "", body: bytes = None, query_params = None):
    """
    Helper function to proxy requests to task service
    """
    token = f"Bearer {user['token']}"
    # Build downstream URL
    if path:
        downstream_url = f"{TASK_SERVICE}/tasks/{path}"
    else:
        downstream_url = f"{TASK_SERVICE}/tasks"

    # Forward headers (keep Authorization and content-type)
    forward_headers = {"Authorization": token}
    if body is not None:
        forward_headers["content-type"] = "application/json"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method=method,
                url=downstream_url,
                headers=forward_headers,
                params=query_params,
                content=body,
                timeout=10.0,
            )
        
        # Return downstream response verbatim
        content = resp.content
        headers = {}
        if resp.headers.get("content-type"):
            headers["content-type"] = resp.headers.get("content-type")
        return Response(content=content, status_code=resp.status_code, headers=headers)
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Task service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gateway error: {str(e)}")


@app.get("/tasks", tags=["Tasks"])
async def proxy_get_tasks(request: Request, user: dict = Depends(validate_token)):
    """
    Proxy GET /tasks to the task service
    """
    return await _proxy_task_request("GET", user, "", None, request.query_params)


from schemas import TaskCreate, TaskUpdate

# ... (omitted code) ...

@app.post("/tasks", tags=["Tasks"])
async def proxy_post_tasks(task: TaskCreate, request: Request, user: dict = Depends(validate_token)):
    """
    Proxy POST /tasks to the task service
    """
    # Serialize Pydantic model to dict, then to JSON bytes
    body = task.model_dump_json().encode("utf-8")
    return await _proxy_task_request("POST", user, "", body, request.query_params)


@app.get("/tasks/{task_id}", tags=["Tasks"])
async def proxy_get_task_by_id(task_id: int, request: Request, user: dict = Depends(validate_token)):
    """
    Proxy GET /tasks/{task_id} to the task service
    """
    return await _proxy_task_request("GET", user, str(task_id), None, request.query_params)


@app.put("/tasks/{task_id}", tags=["Tasks"])
async def proxy_put_task(task_id: int, task: TaskUpdate, request: Request, user: dict = Depends(validate_token)):
    """
    Proxy PUT /tasks/{task_id} to the task service
    """
    body = task.model_dump_json(exclude_unset=True).encode("utf-8")
    return await _proxy_task_request("PUT", user, str(task_id), body, request.query_params)


@app.delete("/tasks/{task_id}", tags=["Tasks"])
async def proxy_delete_task(task_id: int, request: Request, user: dict = Depends(validate_token)):
    """
    Proxy DELETE /tasks/{task_id} to the task service
    """
    return await _proxy_task_request("DELETE", user, str(task_id), None, request.query_params)
