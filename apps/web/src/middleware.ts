/**
 * NextAuth Middleware
 * Protects routes that require authentication
 */

export { default } from 'next-auth/middleware'

export const config = {
  // Protect all routes except login and public pages
  matcher: [
    /*
     * Match all request paths except:
     * - /login (login page)
     * - /api/auth (NextAuth API routes)
     * - /_next (Next.js internals)
     * - /favicon.ico, /robots.txt (static files)
     */
    '/((?!login|api/auth|_next|favicon.ico|robots.txt).*)',
  ],
}
