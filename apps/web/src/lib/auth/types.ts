/**
 * Extended NextAuth types
 * Add custom properties to NextAuth session and JWT
 */

import 'next-auth'
import 'next-auth/jwt'

declare module 'next-auth' {
  interface Session {
    user: {
      id: string
      email: string
      name?: string | null
      image?: string | null
    }
  }

  interface User {
    id: string
    email: string
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    userId?: string
    email?: string
    accessToken?: string
    refreshToken?: string
  }
}
