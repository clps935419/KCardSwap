import * as React from 'react'

import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export interface FileInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string
  buttonClassName?: string
  containerClassName?: string
}

const FileInput = React.forwardRef<HTMLInputElement, FileInputProps>(
  ({ id, label, buttonClassName, containerClassName, className, ...props }, ref) => {
    if (!id) {
      throw new Error('FileInput requires an id prop')
    }

    return (
      <div className={cn('space-y-2', containerClassName)}>
        <input ref={ref} id={id} type="file" className="hidden" {...props} />
        <Button type="button" variant="outline" className={buttonClassName} asChild>
          <label htmlFor={id}>{label}</label>
        </Button>
      </div>
    )
  }
)

FileInput.displayName = 'FileInput'

export { FileInput }
