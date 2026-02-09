'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { getCitiesApiV1LocationsCitiesGetOptions } from '@/shared/api/generated/@tanstack/react-query.gen'
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

export function PostFilters() {
  const router = useRouter()
  const searchParams = useSearchParams()

  const citiesQuery = useQuery({
    ...getCitiesApiV1LocationsCitiesGetOptions(),
    staleTime: 24 * 60 * 60 * 1000,
  })

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

  const cityOptions = [
    { value: 'ALL', label: '全部城市' },
    ...(citiesQuery.data?.data.cities ?? []).map(city => ({
      value: city.code,
      label: `${city.name_zh}`,
    })),
  ]

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

      {/* City Filter */}
      <div className="space-y-2">
        <p className="text-[10px] font-bold text-muted-foreground uppercase">城市</p>
        <Select
          value={currentCity}
          onValueChange={value => updateFilter('city', value)}
        >
          <SelectTrigger className="bg-card border-border rounded-xl font-black">
            <SelectValue placeholder={citiesQuery.isLoading ? '城市載入中...' : '選擇城市'} />
          </SelectTrigger>
          <SelectContent>
            {citiesQuery.isError && (
              <SelectItem value="__error__" disabled>
                城市載入失敗
              </SelectItem>
            )}
            {!citiesQuery.isError && cityOptions.length === 0 && (
              <SelectItem value="__empty__" disabled>
                沒有可用城市
              </SelectItem>
            )}
            {cityOptions.map(city => (
              <SelectItem key={city.value} value={city.value}>
                {city.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
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
