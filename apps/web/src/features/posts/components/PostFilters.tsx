'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import type { PostCategory } from '@/shared/api/generated'

const CATEGORIES: { value: PostCategory; label: string }[] = [
  { value: 'trade', label: '交換' },
  { value: 'giveaway', label: '贈送' },
  { value: 'group', label: '揪團' },
  { value: 'showcase', label: '展示' },
  { value: 'help', label: '求助' },
  { value: 'announcement', label: '公告' },
]

const CITIES = [
  { value: 'global', label: '不限（全域）' },
  { value: 'TPE', label: '台北市' },
  { value: 'TPH', label: '新北市' },
  { value: 'TXG', label: '台中市' },
  { value: 'TNN', label: '台南市' },
  { value: 'KHH', label: '高雄市' },
]

export function PostFilters() {
  const router = useRouter()
  const searchParams = useSearchParams()

  const currentCity = searchParams.get('city') || 'global'
  const currentCategory = searchParams.get('category') || 'all'

  const updateFilter = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams.toString())
    if (value === 'all' || value === 'global') {
      params.delete(key)
    } else {
      params.set(key, value)
    }
    router.push(`/posts?${params.toString()}`)
  }

  return (
    <div className="flex flex-wrap gap-4">
      <div className="flex flex-col gap-2">
        <Label htmlFor="city-filter">城市</Label>
        <Select value={currentCity} onValueChange={(value: string) => updateFilter('city', value)}>
          <SelectTrigger id="city-filter" className="w-[180px]">
            <SelectValue placeholder="選擇城市" />
          </SelectTrigger>
          <SelectContent>
            {CITIES.map((city) => (
              <SelectItem key={city.value} value={city.value}>
                {city.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex flex-col gap-2">
        <Label htmlFor="category-filter">分類</Label>
        <Select
          value={currentCategory}
          onValueChange={(value: string) => updateFilter('category', value)}
        >
          <SelectTrigger id="category-filter" className="w-[180px]">
            <SelectValue placeholder="選擇分類" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部分類</SelectItem>
            {CATEGORIES.map((category) => (
              <SelectItem key={category.value} value={category.value}>
                {category.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  )
}
