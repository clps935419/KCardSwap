// Placeholder toast hook for now
// This will be replaced with proper shadcn/ui toast implementation

export function useToast() {
  return {
    toast: ({
      title,
      description,
      variant,
    }: {
      title?: string
      description?: string
      variant?: 'default' | 'destructive'
    }) => {
      if (variant === 'destructive') {
        console.error(title, description)
      }
    },
  }
}
