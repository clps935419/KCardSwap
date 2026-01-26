/**
 * Middleware for route protection
 *
 * This middleware checks if user is authenticated by verifying
 * the presence of backend httpOnly cookies (access_token).
 *
 * Note: In Next.js 15+, middleware runs on edge runtime,
 * so we can only check for cookie presence, not validate the JWT.
 * Full validation happens in Server Components and API routes.
 */

import type { NextRequest } from 'next/server'
import { NextResponse } from 'next/server'

// Public paths that don't require authentication
const PUBLIC_PATHS = ['/login', '/api/auth']

// Paths that require authentication
const PROTECTED_PATHS = ['/posts', '/inbox', '/me']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Check if path is public
  const isPublicPath = PUBLIC_PATHS.some(path => pathname.startsWith(path))

  // Check if path needs protection
  const isProtectedPath = PROTECTED_PATHS.some(path => pathname.startsWith(path))

  // Get access token from cookies
  const accessToken = request.cookies.get('access_token')
  const hasAuth = !!accessToken

  // If accessing protected path without auth, redirect to login
  if (isProtectedPath && !hasAuth) {
    const loginUrl = new URL('/login', request.url)
    return NextResponse.redirect(loginUrl)
  }

  // If accessing login page while authenticated, redirect to home
  if (pathname === '/login' && hasAuth) {
    const homeUrl = new URL('/posts', request.url)
    return NextResponse.redirect(homeUrl)
  }

  // Allow the request to proceed
  return NextResponse.next()
}

// Configure which routes use this middleware
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico (favicon)
     * - public files (public folder)
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
