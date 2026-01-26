import { redirect } from 'next/navigation'
import { cookies } from 'next/headers'

export default async function HomePage() {
  const cookieStore = await cookies()
  const accessToken = cookieStore.get('access_token')

  // Redirect based on authentication status
  if (accessToken) {
    // User is logged in, redirect to posts feed
    redirect('/posts')
  } else {
    // User is not logged in, redirect to login page
    redirect('/login')
  }
}
