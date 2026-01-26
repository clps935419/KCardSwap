import { redirect } from 'next/navigation'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth/config'

export default async function HomePage() {
  const session = await getServerSession(authOptions)

  // Redirect based on authentication status
  if (session) {
    // User is logged in, redirect to posts feed
    redirect('/posts')
  } else {
    // User is not logged in, redirect to login page
    redirect('/login')
  }
}
