import { Bell } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { alertsApi } from '@/services/api'

export function NotificationBell() {
  const navigate = useNavigate()
  const { data } = useQuery({
    queryKey: ['unread-alert-count'],
    queryFn: async () => {
      const { data } = await alertsApi.list({ unread_only: true, page_size: 1 })
      return data?.total ?? 0
    },
    refetchInterval: 10000,
  })

  const count = data ?? 0

  return (
    <Button
      variant="ghost"
      size="icon"
      className="relative"
      onClick={() => navigate('/alerts')}
      aria-label={`${count} unread alerts`}
    >
      <Bell className="h-5 w-5" />
      {count > 0 && (
        <span className="absolute -top-0.5 -right-0.5 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-destructive text-[10px] font-bold text-destructive-foreground px-1">
          {count > 99 ? '99+' : count}
        </span>
      )}
    </Button>
  )
}
