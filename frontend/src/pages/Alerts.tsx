import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { AlertTriangle, CheckCircle, Eye } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { alertsApi } from '@/services/api'
import toast from 'react-hot-toast'
import type { Alert } from '@/types'

const severityColors = {
  critical: 'danger',
  high: 'warning',
  medium: 'info',
  low: 'secondary',
} as const

export default function Alerts() {
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      const { data } = await alertsApi.list({ page: 1, page_size: 100 })
      return data
    },
    refetchInterval: 10000,
  })

  const markRead = useMutation({
    mutationFn: (id: string) => alertsApi.markRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      toast.success('Alert marked as read')
    },
  })

  const acknowledge = useMutation({
    mutationFn: (id: string) => alertsApi.acknowledge(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      toast.success('Alert acknowledged')
    },
  })

  const alerts: Alert[] = data?.items ?? []

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Alerts</h1>
        <p className="text-sm text-muted-foreground">Security alerts and notifications</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">All Alerts ({data?.total ?? 0})</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          ) : (
            <div className="space-y-3">
              {alerts.map((alert) => (
                <div key={alert.id} className={`p-4 rounded-lg border ${
                  !alert.is_read ? 'border-primary/50 bg-primary/5' : 'border-border'
                }`}>
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <AlertTriangle className={`h-5 w-5 flex-shrink-0 mt-0.5 ${
                        alert.severity === 'critical' ? 'text-red-500' : 'text-yellow-500'
                      }`} />
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="font-medium">{alert.title}</h3>
                          <Badge variant={severityColors[alert.severity as keyof typeof severityColors] || 'secondary'}>
                            {alert.severity}
                          </Badge>
                          {!alert.is_read && (
                            <Badge variant="default" className="text-[10px]">NEW</Badge>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground mt-1 font-mono">
                          {alert.src_ip} → {alert.dst_ip} | {alert.threat_type}
                        </p>
                      </div>
                    </div>
                    <div className="flex flex-wrap items-center gap-2 pl-8 sm:pl-0">
                      {!alert.is_read && (
                        <Button variant="ghost" size="sm" onClick={() => markRead.mutate(alert.id)}>
                          <Eye className="h-4 w-4 mr-1" /> Read
                        </Button>
                      )}
                      {!alert.is_acknowledged && (
                        <Button variant="ghost" size="sm" onClick={() => acknowledge.mutate(alert.id)}>
                          <CheckCircle className="h-4 w-4 mr-1" /> Acknowledge
                        </Button>
                      )}
                    </div>
                  </div>
                  <p className="text-sm mt-2 text-muted-foreground">{alert.message}</p>
                  {alert.recommendation && (
                    <div className="mt-2 p-2 rounded bg-blue-500/10 border border-blue-500/20">
                      <p className="text-xs text-blue-500">
                        <span className="font-medium">Recommendation:</span> {alert.recommendation}
                      </p>
                    </div>
                  )}
                </div>
              ))}
              {alerts.length === 0 && (
                <p className="text-center py-8 text-muted-foreground">No alerts</p>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
