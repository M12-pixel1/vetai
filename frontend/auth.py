"""
Authentication module for user management and security.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages user authentication and authorization."""

    def __init__(self, secret_key: str = None):
        """
        Initialize the auth manager.
        
        Args:
            secret_key: Secret key for token generation
        """
        self.secret_key = secret_key or secrets.token_hex(32)
        self.sessions = {}  # In-memory session storage (use Redis in production)
        logger.info("Auth manager initialized")

    def hash_password(self, password: str, salt: str = None) -> tuple:
        """
        Hash a password with salt.
        
        Args:
            password: Plain text password
            salt: Optional salt (generated if not provided)
            
        Returns:
            Tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use SHA-256 for hashing (use bcrypt/argon2 in production)
        hashed = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
        return hashed, salt

    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """
        Verify a password against a hash.
        
        Args:
            password: Plain text password
            hashed_password: Stored hashed password
            salt: Salt used in hashing
            
        Returns:
            True if password matches, False otherwise
        """
        test_hash, _ = self.hash_password(password, salt)
        return test_hash == hashed_password

    def create_session(
        self,
        user_id: int,
        username: str,
        role: str,
        duration_hours: int = 24
    ) -> str:
        """
        Create a user session.
        
        Args:
            user_id: User ID
            username: Username
            role: User role
            duration_hours: Session duration in hours
            
        Returns:
            Session token
        """
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        
        self.sessions[token] = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
        }
        
        logger.info(f"Session created for user: {username}")
        return token

    def validate_session(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a session token.
        
        Args:
            token: Session token
            
        Returns:
            Session data if valid, None otherwise
        """
        session = self.sessions.get(token)
        
        if not session:
            return None
        
        # Check if session expired
        if datetime.utcnow() > session["expires_at"]:
            del self.sessions[token]
            logger.info(f"Session expired for user: {session['username']}")
            return None
        
        return session

    def destroy_session(self, token: str) -> bool:
        """
        Destroy a session (logout).
        
        Args:
            token: Session token
            
        Returns:
            True if session destroyed, False if not found
        """
        if token in self.sessions:
            username = self.sessions[token]["username"]
            del self.sessions[token]
            logger.info(f"Session destroyed for user: {username}")
            return True
        return False

    def check_permission(self, session_token: str, required_role: str) -> bool:
        """
        Check if user has required permission.
        
        Args:
            session_token: User's session token
            required_role: Required role for the action
            
        Returns:
            True if user has permission, False otherwise
        """
        session = self.validate_session(session_token)
        
        if not session:
            return False
        
        # Role hierarchy: admin > veterinarian > technician > viewer
        role_hierarchy = {
            "admin": 4,
            "veterinarian": 3,
            "technician": 2,
            "viewer": 1,
        }
        
        user_level = role_hierarchy.get(session["role"], 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level

    def get_active_sessions(self) -> list:
        """
        Get list of active sessions.
        
        Returns:
            List of active session info
        """
        active = []
        now = datetime.utcnow()
        
        for token, session in list(self.sessions.items()):
            if now <= session["expires_at"]:
                active.append({
                    "user_id": session["user_id"],
                    "username": session["username"],
                    "role": session["role"],
                    "created_at": session["created_at"].isoformat(),
                    "expires_at": session["expires_at"].isoformat(),
                })
            else:
                # Clean up expired session
                del self.sessions[token]
        
        return active

    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        now = datetime.utcnow()
        expired_tokens = [
            token for token, session in self.sessions.items()
            if now > session["expires_at"]
        ]
        
        for token in expired_tokens:
            del self.sessions[token]
        
        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired sessions")
        
        return len(expired_tokens)


# Global auth manager instance
auth_manager = AuthManager()


def require_auth(role: str = "viewer"):
    """
    Decorator to require authentication for a function.
    
    Args:
        role: Minimum required role
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This is a placeholder - implement actual auth checking
            # In Streamlit, you would check st.session_state
            return func(*args, **kwargs)
        return wrapper
    return decorator


def login_user(username: str, password: str) -> Optional[str]:
    """
    Login a user.
    
    Args:
        username: Username
        password: Password
        
    Returns:
        Session token if successful, None otherwise
    """
    # This is a placeholder - implement actual user lookup from database
    logger.info(f"Login attempt for user: {username}")
    
    # Mock successful login
    if username and password:
        return auth_manager.create_session(
            user_id=1,
            username=username,
            role="veterinarian"
        )
    
    return None


def logout_user(session_token: str) -> bool:
    """
    Logout a user.
    
    Args:
        session_token: Session token
        
    Returns:
        True if successful, False otherwise
    """
    return auth_manager.destroy_session(session_token)
