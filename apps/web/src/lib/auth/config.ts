/**
 * NextAuth Configuration
 *
 * Integrates with backend Google OAuth endpoints:
 * - POST /api/v1/auth/google-login - Submit Google ID token to backend
 * - Backend validates token and returns access/refresh tokens
 * - Tokens are stored in httpOnly cookies by backend
 */

import type { NextAuthOptions } from 'next-auth'
import GoogleProvider from 'next-auth/providers/google'

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],

  secret: process.env.NEXTAUTH_SECRET,

  pages: {
    signIn: '/login',
    error: '/login',
  },

  callbacks: {
    /**
     * JWT callback - Called when creating/updating JWT
     * We send Google ID token to backend and get our JWT tokens
     */
    async jwt({ token, account }) {
      // Initial sign in
      if (account?.id_token) {
        try {
          // Send Google ID token to our backend
          const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
          const response = await fetch(`${backendUrl}/api/v1/auth/google-login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include', // Important for cookies
            body: JSON.stringify({
              google_token: account.id_token,
            }),
          })

          if (!response.ok) {
            console.error('[NextAuth] Backend login failed:', response.status)
            throw new Error('Backend authentication failed')
          }

          const data = await response.json()

          // Store backend user info in token
          if (data.data) {
            token.userId = data.data.user_id
            token.email = data.data.email
            token.accessToken = data.data.access_token
            token.refreshToken = data.data.refresh_token
          }
        } catch (error) {
          console.error('[NextAuth] Error during backend authentication:', error)
          // Return token anyway to prevent breaking auth flow
          // User will be redirected to login if backend auth actually failed
        }
      }

      return token
    },

    /**
     * Session callback - Called when creating session object
     * Adds our backend user info to the session
     */
    async session({ session, token }) {
      if (token) {
        session.user.id = token.userId as string
        session.user.email = token.email as string
      }
      return session
    },
  },

  session: {
    strategy: 'jwt',
    maxAge: 7 * 24 * 60 * 60, // 7 days
  },
}
