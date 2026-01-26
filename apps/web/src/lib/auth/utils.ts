/**
 * Auth utility functions
 * Helper functions for authentication
 */

import { getServerSession } from 'next-auth'
import { authOptions } from './config'

/**
 * Get current session on server side
 * Use this in Server Components and API routes
 */
export async function getSession() {
  return await getServerSession(authOptions)
}

/**
 * Check if user is authenticated on server side
 * Use this in Server Components and API routes
 */
export async function isAuthenticated() {
  const session = await getSession()
  return !!session?.user
}

/**
 * Get current user on server side
 * Returns null if not authenticated
 */
export async function getCurrentUser() {
  const session = await getSession()
  return session?.user || null
}
