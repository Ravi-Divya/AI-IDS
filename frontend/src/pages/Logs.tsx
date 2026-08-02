import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import api from '@/services/api'

const fadeUp = (i: number) => ({
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
  transition: { delay: i * 0.03, duration: 0.3 },
})

export default function Logs() {
  const { data, isLoading } = useQuery({
    queryKey: ['logs'],
    queryFn: async () => {
      const { data } = await api.get('/logs/', { params: { page: 1, page_size: 100 } })
      return data
    },
    refetchInterval: 10000,
  })

  const logs: any[] = data?.items ?? []

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ type: 'spring', stiffness: 200, damping: 20 }} className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Audit Logs</h1>
        <p className="text-sm text-muted-foreground">System audit trail</p>
      </div>

      <Card className="card-hover">
        <CardHeader>
          <CardTitle className="text-sm font-medium">Activity Log ({data?.total ?? 0})</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          ) : (
            <ScrollArea className="max-h-[600px]">
              <div className="divide-y divide-border/30">
                {logs.map((log: any, i: number) => (
                  <motion.div
                    key={log.id}
                    {...fadeUp(i)}
                    className="flex flex-col sm:flex-row sm:items-center justify-between px-4 py-3 gap-2 hover:bg-secondary/20 transition-colors"
                  >
                    <div className="flex flex-wrap items-center gap-2 min-w-0">
                      <Badge variant={log.status === 'success' ? 'success' : 'danger'} className="text-[10px] uppercase shrink-0">
                        {log.status}
                      </Badge>
                      <span className="font-medium text-sm truncate">{log.action}</span>
                      <span className="text-muted-foreground text-sm hidden sm:inline">·</span>
                      <span className="text-muted-foreground text-xs truncate">{log.resource}</span>
                      {log.ip_address && (
                        <span className="text-muted-foreground text-xs font-mono shrink-0">({log.ip_address})</span>
                      )}
                    </div>
                    <span className="text-xs text-muted-foreground shrink-0">
                      {new Date(log.created_at).toLocaleString()}
                    </span>
                  </motion.div>
                ))}
                {logs.length === 0 && (
                  <div className="text-center py-12 text-muted-foreground">No logs available</div>
                )}
              </div>
            </ScrollArea>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
