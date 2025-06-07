

import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Request
from fastapi import HTTPException



from .db import User, File as DBFile, Query, Session, SessionLocal
from .schemas import RegisterRequest
from .auth import get_db, get_password_hash, authenticate_user, create_access_token, get_current_user
from fastapi import HTTPException
from .llm import query_openai







router = APIRouter()
status_message = "Fittergem API is starting up..."

@router.get("/")
def root():
    """Root endpoint that shows API status and statistics.
    
    Returns:
        dict: API status message including current time and user count
    """
    return {"message": status_message}



@router.post("/register")
def register(req: RegisterRequest, db: SessionLocal = Depends(get_db)):
    """Register a new user in the system.
    
    Args:
        req: The registration request containing username and password
        db: Database session dependency
        
    Returns:
        dict: Registration confirmation with userId
        
    Raises:
        HTTPException: 400 error if username already exists
        HTTPException: 400 error if phone number already exists
    """
    # Check for existing user by username
    existing_user = db.query(User).filter(User.username == req.username).first()
    if existing_user:
        #logger.warning(f"[register] Registration attempt with existing username: {req.username}")
        raise HTTPException(status_code=400, detail="Username already registered")


    # Create new user
    hashed_password = get_password_hash(req.password)
    new_user = User(
        username=req.username, 
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Registered successfully", "userId": new_user.userId}


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: SessionLocal = Depends(get_db)):
    """Authenticate user and generate access token.
    
    This endpoint conforms to the OAuth2 password flow standard.
    
    Args:
        form_data: OAuth2 form containing username and password
        db: Database session dependency
        
    Returns:
        dict: JWT access token and token type
        
    Raises:
        HTTPException: 401 if authentication fails
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/query")
async def queryEndpoint(request: Request, user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)):
    """Process an AI query from a user.
    
    Sends the query to the OpenAI API and returns the response. The query and response
    are associated with a chat ID for maintaining conversation context.
    All queries and responses are stored in the database for future reference.
    
    Args:
        request: The HTTP request containing the query data
        user: The authenticated user making the query
        db: Database session dependency
        
    Returns:
        dict: The AI response along with query details

    Raises:
        HTTPException: 400 if required parameters are missing
        HTTPException: 500 if OpenAI API call fails
    
    """
    # First check if there's any content in the request body
    body_bytes = await request.body()
    if not body_bytes:
        return JSONResponse({"error": "Empty request body"}, status_code=400)
        
    # Try to parse the JSON body
    try:
        body = await request.json()
    except json.JSONDecodeError as json_err:
        return JSONResponse({"error": f"Invalid JSON in request body: {str(json_err)}"}, status_code=400)
        

    try:
        
        # Check for required fields
        if not body.get("query"):
            return JSONResponse(status_code=400, content={"error": "No query provided"})
            
        # Check for chat_id field - Make sure this runs BEFORE the try-except for the AI agent
        # Handle both camelCase (chatId) and snake_case (chat_id) formats for compatibility
        chat_id = body.get("chat_id") or body.get("chatId")
        if chat_id is None or chat_id == "":
            return JSONResponse(status_code=400, content={"error": "No chat ID provided"})
        
        user_query = body.get("query")
        # check pageContent field
        page_content = body.get("pageContent")
        if page_content :
            user_query += "\n\n" + "Here is the page content: " + page_content

        # Call your AI agent with try/except to handle Vercel environment limitations
        try:

            
            # Send query to AI agent using query_openai instead of ask_ai
            response = query_openai(
                query=user_query
            )
            

        except Exception as e:
            response = str(e)

        
        return {
            "response": response,
            "query": user_query,
            "chat_id": chat_id,
            "queryId": db_query.queryId
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
