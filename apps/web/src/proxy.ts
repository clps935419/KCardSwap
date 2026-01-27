/**
 * Next.js 16 Proxy
 * Replaces middleware.ts in Next.js 16+
 *
 * Performs lightweight authentication checks at the network edge.
 * Now checks for backend httpOnly cookies instead of NextAuth session tokens.
 * Full JWT validation happens in Server Components and API routes.
 */

import type { NextRequest } from 'next/server'
import { NextResponse } from 'next/server'

// Public paths that don't require authentication
const PUBLIC_PATHS = ['/login', '/api/auth']

// Paths that require authentication
const PROTECTED_PATHS = ['/posts', '/inbox', '/me']

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // Check if path is public
  const isPublicPath = PUBLIC_PATHS.some(path => pathname.startsWith(path))
  
  // Check if path needs protection
  const isProtectedPath = PROTECTED_PATHS.some(path => pathname.startsWith(path))
  
  // Get access token from cookies (backend httpOnly cookie)
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

export const config = {
  // Match all routes except:
  // - /api/auth (Auth API routes)
  // - /_next (Next.js internals)
  // - Static files (favicon, robots, images, etc.)
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
