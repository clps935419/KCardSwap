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
  const { pathname, basePath } = request.nextUrl
  const normalizedPath =
    basePath && pathname.startsWith(basePath) ? pathname.slice(basePath.length) || '/' : pathname

  const withoutBasePath = (path: string) => {
    if (!basePath || !path.startsWith(basePath)) return path
    return path.slice(basePath.length) || '/'
  }

  // Check if path is public
  const _isPublicPath = PUBLIC_PATHS.some(path => normalizedPath.startsWith(path))

  // Check if path needs protection
  const isProtectedPath = PROTECTED_PATHS.some(path => normalizedPath.startsWith(path))

  // Get access token from cookies (backend httpOnly cookie)
  const accessToken = request.cookies.get('access_token')
  const hasAuth = !!accessToken

  if (process.env.NODE_ENV !== 'production') {
    console.log('[proxy]', {
      pathname,
      basePath,
      normalizedPath,
      url: request.nextUrl.href,
      hasAuth,
    })
  }

  // If accessing protected path without auth, redirect to login
  if (isProtectedPath && !hasAuth) {
    const loginUrl = request.nextUrl.clone()
    // Let Next.js apply basePath; avoid double-prefix in redirects.
    loginUrl.pathname = withoutBasePath('/login')
    return NextResponse.redirect(loginUrl)
  }

  // If accessing login page while authenticated, redirect to home
  if (normalizedPath === '/login' && hasAuth) {
    const homeUrl = request.nextUrl.clone()
    // Let Next.js apply basePath; avoid double-prefix in redirects.
    homeUrl.pathname = withoutBasePath('/posts')
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
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)'],
}
