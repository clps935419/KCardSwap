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
     * 
     * NOTE: This callback is no longer used for backend authentication.
     * Frontend now directly calls backend /api/v1/auth/google-login
     * to receive httpOnly cookies. This callback is kept for backward
     * compatibility but does nothing.
     */
    async jwt({ token, account }) {
      // No longer sending to backend - frontend handles this directly
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
