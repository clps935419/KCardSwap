/**
 * Google OAuth Service with PKCE Flow (M101)
 * 
 * Implements the Authorization Code Flow with PKCE for secure Google OAuth
 * on mobile devices. This follows OAuth 2.0 best practices.
 * 
 * Flow:
 * 1. Generate code_verifier and code_challenge
 * 2. Start OAuth flow with Google
 * 3. User authorizes in browser
 * 4. Receive authorization code
 * 5. Send code + code_verifier to backend
 * 6. Backend exchanges with Google and returns JWT tokens
 */

import * as AuthSession from 'expo-auth-session';
import * as Crypto from 'expo-crypto';
import { Platform } from 'react-native';
import { config } from '@/src/shared/config';
import { apiClient } from '@/src/shared/api/client';

// Google OAuth configuration
const GOOGLE_OAUTH_CONFIG = {
  clientId: config.googleClientId,
  scopes: ['openid', 'profile', 'email'],
  redirectUri: AuthSession.makeRedirectUri({
    scheme: config.appScheme,
    // For development
    path: 'auth/callback',
  }),
};

/**
 * Generate a random code verifier for PKCE
 * Must be 43-128 characters from [A-Z][a-z][0-9]-._~
 */
export async function generateCodeVerifier(): Promise<string> {
  const randomBytes = await Crypto.getRandomBytesAsync(32);
  const codeVerifier = base64UrlEncode(randomBytes);
  return codeVerifier;
}

/**
 * Generate code challenge from code verifier
 * challenge = BASE64URL(SHA256(verifier))
 */
export async function generateCodeChallenge(codeVerifier: string): Promise<string> {
  const digest = await Crypto.digestStringAsync(
    Crypto.CryptoDigestAlgorithm.SHA256,
    codeVerifier,
    { encoding: Crypto.CryptoEncoding.BASE64 }
  );
  return base64UrlEncode(digest);
}

/**
 * Base64 URL encoding (without padding)
 */
function base64UrlEncode(input: string | Uint8Array): string {
  let base64: string;

  if (typeof input === 'string') {
    base64 = input;
  } else {
    // Convert Uint8Array to base64
    base64 = Buffer.from(input).toString('base64');
  }

  // Convert base64 to base64url (RFC 7636 section 4.2)
  return base64
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

/**
 * Google OAuth Response from backend
 */
export interface GoogleOAuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user_id: string;
  email: string;
}

/**
 * Start Google OAuth flow with PKCE
 * 
 * @returns Authorization result with code or error
 */
export async function startGoogleOAuthFlow(): Promise<AuthSession.AuthSessionResult> {
  try {
    // Generate PKCE values
    const codeVerifier = await generateCodeVerifier();
    const codeChallenge = await generateCodeChallenge(codeVerifier);

    console.log('Starting Google OAuth with PKCE...');
    console.log('Redirect URI:', GOOGLE_OAUTH_CONFIG.redirectUri);

    // Build authorization URL
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?${new URLSearchParams({
      client_id: GOOGLE_OAUTH_CONFIG.clientId,
      redirect_uri: GOOGLE_OAUTH_CONFIG.redirectUri,
      response_type: 'code',
      scope: GOOGLE_OAUTH_CONFIG.scopes.join(' '),
      code_challenge: codeChallenge,
      code_challenge_method: 'S256',
      access_type: 'offline',
      prompt: 'consent',
    }).toString()}`;

    // Start OAuth flow
    const result = await AuthSession.startAsync({
      authUrl,
      returnUrl: GOOGLE_OAUTH_CONFIG.redirectUri,
    });

    // Store code verifier for exchange
    if (result.type === 'success' && result.params.code) {
      (result as any).codeVerifier = codeVerifier;
    }

    return result;
  } catch (error) {
    console.error('Google OAuth flow error:', error);
    throw new Error('Failed to start Google OAuth flow');
  }
}

/**
 * Exchange authorization code for tokens via backend
 * 
 * @param code - Authorization code from Google
 * @param codeVerifier - Code verifier used in PKCE challenge
 * @returns Token response from backend
 */
export async function exchangeCodeForTokens(
  code: string,
  codeVerifier: string
): Promise<GoogleOAuthResponse> {
  try {
    console.log('Exchanging authorization code for tokens...');

    const response = await apiClient.post<{ data: GoogleOAuthResponse; error: null }>(
      '/auth/google-callback',
      {
        code,
        code_verifier: codeVerifier,
        redirect_uri: GOOGLE_OAUTH_CONFIG.redirectUri,
      }
    );

    if (!response.data || !response.data.data) {
      throw new Error('Invalid response from server');
    }

    return response.data.data;
  } catch (error: any) {
    console.error('Token exchange error:', error);

    // Handle specific error cases
    if (error.response?.status === 401) {
      throw new Error('Invalid authorization code. Please try again.');
    } else if (error.response?.status === 422) {
      throw new Error('Invalid request. Please check your configuration.');
    } else if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      throw new Error('Server timeout. Please try again.');
    }

    throw new Error(error.message || 'Failed to exchange code for tokens');
  }
}

/**
 * Complete Google login flow with PKCE
 * 
 * This is the main function to call for Google authentication
 * 
 * @returns Token response or throws error
 */
export async function googleLoginWithPKCE(): Promise<GoogleOAuthResponse> {
  try {
    // Step 1: Start OAuth flow and get authorization code
    const authResult = await startGoogleOAuthFlow();

    console.log('OAuth result type:', authResult.type);

    // Handle different result types
    if (authResult.type === 'error') {
      throw new Error(authResult.params?.error_description || 'OAuth flow failed');
    }

    if (authResult.type === 'dismiss' || authResult.type === 'cancel') {
      throw new Error('User cancelled login');
    }

    if (authResult.type !== 'success' || !authResult.params.code) {
      throw new Error('No authorization code received');
    }

    // Step 2: Exchange code for tokens via backend
    const code = authResult.params.code;
    const codeVerifier = (authResult as any).codeVerifier;

    if (!codeVerifier) {
      throw new Error('Code verifier not found');
    }

    const tokens = await exchangeCodeForTokens(code, codeVerifier);

    console.log('Successfully obtained tokens');
    return tokens;
  } catch (error: any) {
    console.error('Google login with PKCE failed:', error);
    throw error;
  }
}

/**
 * Check if Google OAuth is configured properly
 */
export function isGoogleOAuthConfigured(): boolean {
  return !!(
    config.googleClientId &&
    config.googleClientId !== 'YOUR_GOOGLE_CLIENT_ID'
  );
}

/**
 * Get OAuth configuration for debugging
 */
export function getOAuthConfig() {
  return {
    clientId: config.googleClientId,
    redirectUri: GOOGLE_OAUTH_CONFIG.redirectUri,
    scopes: GOOGLE_OAUTH_CONFIG.scopes,
  };
}
