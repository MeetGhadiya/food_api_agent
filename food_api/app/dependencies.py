from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from beanie import PydanticObjectId
from typing import Optional

from .models import User
from .security import SECRET_KEY, ALGORITHM

# Custom token extraction function - avoids FastAPI auto-generating OAuth2 schema
async def get_token_from_header(request: Request) -> str:
    """
    Extract Bearer token from Authorization header manually.
    This approach prevents FastAPI from auto-generating OAuth2 schema.
    """
    authorization: str = request.headers.get("Authorization", "")
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if it starts with "Bearer "
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract the token
    token = authorization[7:]  # Remove "Bearer " prefix
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is empty",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token

async def get_current_user(request: Request) -> User:
    """
    Dependency to get the current authenticated user from JWT Bearer token.
    
    This function:
    1. Extracts the Bearer token from the Authorization header (manually)
    2. Validates and decodes the JWT token
    3. Retrieves the user from the database
    4. Returns the authenticated user
    
    Raises:
    - 401 Unauthorized if token is invalid or user not found
    
    Note: We extract the token manually instead of using HTTPBearer dependency
    to prevent FastAPI from auto-generating OAuth2 schema in OpenAPI docs.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token manually from header
        token = await get_token_from_header(request)
        
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract the username from the token's "sub" claim
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    except HTTPException:
        # Re-raise HTTP exceptions from get_token_from_header
        raise
    
    # Find the user in the database by their username
    user = await User.find_one(User.username == username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to verify that the current user has admin role.
    Used for protected admin-only endpoints.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action. Admin access required."
        )
    return current_user