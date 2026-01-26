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
      // For now, just console.log
      if (variant === 'destructive') {
        console.error(title, description)
      } else {
        console.log(title, description)
      }
    },
  }
}
