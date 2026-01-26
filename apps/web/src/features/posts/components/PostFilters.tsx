'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import type { PostCategory } from '@/shared/api/generated'

const CATEGORIES: { value: PostCategory | 'all'; label: string }[] = [
  { value: 'all', label: '全部' },
  { value: 'trade', label: '求換' },
  { value: 'giveaway', label: '送出' },
  { value: 'group', label: '揪團' },
  { value: 'showcase', label: '展示' },
  { value: 'help', label: '求助' },
  { value: 'announcement', label: '公告' },
]

const CITIES = [
  { value: 'ALL', label: '全部城市' },
  { value: 'TPE', label: '台北 TPE' },
  { value: 'TPH', label: '新北 TPH' },
  { value: 'TXG', label: '台中 TXG' },
  { value: 'TNN', label: '台南 TNN' },
  { value: 'KHH', label: '高雄 KHH' },
]

export function PostFilters() {
  const router = useRouter()
  const searchParams = useSearchParams()

  const currentCity = searchParams.get('city') || 'ALL'
  const currentCategory = searchParams.get('category') || 'all'

  const updateFilter = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams.toString())
    if (value === 'all' || value === 'ALL') {
      params.delete(key)
    } else {
      params.set(key, value)
    }
    router.push(`/posts?${params.toString()}`)
  }

  return (
    <div className="space-y-4">
      {/* Info Header */}
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-black text-foreground">全域列表（顯示全部貼文）</p>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="text-[11px] font-black text-primary-500 hover:text-primary-500/80 h-auto p-0"
        >
          規則
        </Button>
      </div>

      {/* City Filters */}
      <div className="flex flex-wrap gap-2">
        {CITIES.map(city => (
          <Button
            key={city.value}
            variant="outline"
            size="sm"
            onClick={() => updateFilter('city', city.value)}
            className={`px-3 py-2 rounded-full text-[11px] font-black border transition-all ${
              currentCity === city.value
                ? 'border-foreground bg-foreground text-card hover:bg-foreground/90'
                : 'border-border bg-card text-muted-foreground hover:bg-muted hover:text-foreground'
            }`}
          >
            {city.label}
          </Button>
        ))}
      </div>

      {/* Category Filters */}
      <div className="flex flex-wrap gap-2">
        {CATEGORIES.map(category => (
          <Button
            key={category.value}
            variant="outline"
            size="sm"
            onClick={() => updateFilter('category', category.value)}
            className={`px-3 py-2 rounded-full text-[11px] font-black border transition-all ${
              currentCategory === category.value
                ? 'border-primary-500 bg-accent text-primary-500 hover:bg-accent/80'
                : 'border-border bg-card text-muted-foreground hover:bg-muted hover:text-foreground'
            }`}
          >
            {category.label}
          </Button>
        ))}
      </div>
    </div>
  )
}
