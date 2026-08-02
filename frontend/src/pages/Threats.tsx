import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Siren } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { threatsApi } from '@/services/api'
import type { Threat } from '@/types'

const severityColors = {
  critical: 'danger',
  high: 'warning',
  medium: 'info',
  low: 'secondary',
} as const

export default function Threats() {
  const { data, isLoading } = useQuery({
    queryKey: ['threats'],
    queryFn: async () => {
      const { data } = await threatsApi.list({ page: 1, page_size: 100 })
      return data
    },
    refetchInterval: 10000,
  })

  const threats: Threat[] = data?.items ?? []

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Threats</h1>
        <p className="text-sm text-muted-foreground">Detected security threats and attacks</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">All Threats ({data?.total ?? 0})</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          ) : (
            <div className="space-y-3">
              {threats.map((threat) => (
                <div key={threat.id} className="p-4 rounded-lg border border-border bg-card">
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-full bg-red-500/10 flex-shrink-0">
                        <Siren className="h-5 w-5 text-red-500" />
                      </div>
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="font-medium">{threat.threat_type}</h3>
                          <Badge variant={severityColors[threat.severity as keyof typeof severityColors] || 'secondary'}>
                            {threat.severity}
                          </Badge>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1 font-mono">
                          {threat.src_ip}:{threat.src_port} → {threat.dst_ip}:{threat.dst_port}
                        </p>
                        {threat.explanation && (
                          <p className="text-sm mt-2 text-muted-foreground">{threat.explanation}</p>
                        )}
                      </div>
                    </div>
                    <div className="text-left sm:text-right text-xs text-muted-foreground pl-11 sm:pl-0">
                      <div className="mb-1">{(threat.confidence * 100).toFixed(1)}% confidence</div>
                      <div>{new Date(threat.created_at).toLocaleString()}</div>
                    </div>
                  </div>
                  {threat.recommendation && (
                    <div className="mt-2 p-2 rounded bg-yellow-500/10 border border-yellow-500/20">
                      <p className="text-xs text-yellow-500">
                        <span className="font-medium">Recommendation:</span> {threat.recommendation}
                      </p>
                    </div>
                  )}
                </div>
              ))}
              {threats.length === 0 && (
                <p className="text-center py-8 text-muted-foreground">No threats detected</p>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
