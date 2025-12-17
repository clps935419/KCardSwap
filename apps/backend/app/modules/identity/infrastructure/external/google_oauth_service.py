"""
Google OAuth Service - Handle Google OAuth authentication
"""
import os
from typing import Any, Dict, Optional

import httpx
from google.auth.transport import requests
from google.oauth2 import id_token


class GoogleOAuthService:
    """Service for Google OAuth operations"""

    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "")

    async def verify_google_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Google ID token and return user info
        Returns None if token is invalid
        """
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                self.client_id
            )

            # Verify issuer
            valid_issuers = [
                'accounts.google.com',
                'https://accounts.google.com',
            ]
            if idinfo['iss'] not in valid_issuers:
                return None

            return {
                "google_id": idinfo['sub'],
                "email": idinfo.get('email'),
                "name": idinfo.get('name'),
                "picture": idinfo.get('picture'),
                "email_verified": idinfo.get('email_verified', False)
            }
        except ValueError:
            # Invalid token
            return None

    async def exchange_code_for_token(self, code: str) -> Optional[str]:
        """
        Exchange authorization code for ID token
        Returns ID token or None if exchange fails
        """
        token_url = "https://oauth2.googleapis.com/token"

        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, data=data)

                if response.status_code == 200:
                    tokens = response.json()
                    return tokens.get("id_token")
                return None
        except Exception:
            return None

    async def exchange_code_with_pkce(
        self,
        code: str,
        code_verifier: str,
        redirect_uri: Optional[str] = None
    ) -> Optional[str]:
        """
        Exchange authorization code for ID token using PKCE flow (Expo AuthSession)
        
        Args:
            code: Authorization code from Google OAuth
            code_verifier: PKCE code verifier (43-128 characters)
            redirect_uri: Optional redirect URI (must match the one used in auth request)
        
        Returns:
            ID token or None if exchange fails
        """
        token_url = "https://oauth2.googleapis.com/token"
        
        # Use provided redirect_uri or fallback to configured one
        uri = redirect_uri or self.redirect_uri

        data = {
            "code": code,
            "client_id": self.client_id,
            "code_verifier": code_verifier,
            "redirect_uri": uri,
            "grant_type": "authorization_code"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(token_url, data=data)

                if response.status_code == 200:
                    tokens = response.json()
                    return tokens.get("id_token")
                return None
        except httpx.TimeoutException:
            # Timeout occurred
            return None
        except Exception:
            # Other exceptions
            return None
