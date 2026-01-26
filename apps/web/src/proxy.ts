/**
 * Next.js 16 Proxy
 * Replaces middleware.ts in Next.js 16+
 *
 * Performs lightweight authentication checks at the network edge.
 * Full session validation happens in Server Components and API routes.
 */

import type { NextRequest } from 'next/server'
import { NextResponse } from 'next/server'

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Check for NextAuth session token (lightweight check only)
  const sessionToken =
    request.cookies.get('next-auth.session-token') ||
    request.cookies.get('__Secure-next-auth.session-token')

  // Public routes that don't require authentication
  const isPublicRoute = pathname.startsWith('/login') || pathname.startsWith('/auth-test')

  // Allow access to public routes
  if (isPublicRoute) {
    return NextResponse.next()
  }

  // Redirect to login if no session token found
  if (!sessionToken) {
    const loginUrl = new URL('/login', request.url)
    return NextResponse.redirect(loginUrl)
  }

  // Allow authenticated requests to proceed
  return NextResponse.next()
}

export const config = {
  // Match all routes except:
  // - /api/auth (NextAuth API routes)
  // - /_next (Next.js internals)
  // - Static files (favicon, robots, images, etc.)
  matcher: ['/((?!api/auth|_next/static|_next/image|favicon.ico|robots.txt).*)'],
}
