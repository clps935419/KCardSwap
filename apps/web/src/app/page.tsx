import { redirect } from 'next/navigation'
import { getSession } from '@/lib/auth/utils'

export default async function HomePage() {
  const session = await getSession()

  // Redirect based on authentication status
  if (session) {
    // User is logged in, redirect to posts feed
    redirect('/posts')
  } else {
    // User is not logged in, redirect to login page
    redirect('/login')
  }
}
