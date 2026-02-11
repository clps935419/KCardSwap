'use client'

import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

export function InboxPageLoading() {
  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-3 w-16" />
        </div>
        {[...Array(2)].map((_, index) => (
          <Card
            key={`request-skeleton-${index}`}
            className="p-4 rounded-2xl shadow-sm border border-border/30 bg-card"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <Skeleton className="h-10 w-10 rounded-full" />
                <div className="space-y-2">
                  <Skeleton className="h-3 w-24" />
                  <Skeleton className="h-3 w-16" />
                </div>
              </div>
              <Skeleton className="h-4 w-12 rounded-full" />
            </div>
            <div className="mt-3 grid grid-cols-2 gap-3">
              <Skeleton className="h-11 w-full rounded-2xl" />
              <Skeleton className="h-11 w-full rounded-2xl" />
            </div>
          </Card>
        ))}
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-3 w-16" />
        </div>
        {[...Array(2)].map((_, index) => (
          <Card
            key={`sent-skeleton-${index}`}
            className="p-4 rounded-2xl shadow-sm border border-border/30 bg-card"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <Skeleton className="h-10 w-10 rounded-full" />
                <div className="space-y-2">
                  <Skeleton className="h-3 w-24" />
                  <Skeleton className="h-3 w-20" />
                </div>
              </div>
              <Skeleton className="h-4 w-12 rounded-full" />
            </div>
          </Card>
        ))}
      </div>

      <div className="space-y-3">
        <Skeleton className="h-4 w-16" />
        {[...Array(3)].map((_, index) => (
          <Card
            key={`thread-skeleton-${index}`}
            className="p-4 rounded-2xl shadow-sm border border-border/30 bg-card"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Skeleton className="h-10 w-10 rounded-full" />
                <div className="space-y-2">
                  <Skeleton className="h-3 w-24" />
                  <Skeleton className="h-3 w-20" />
                </div>
              </div>
              <Skeleton className="h-4 w-4" />
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
