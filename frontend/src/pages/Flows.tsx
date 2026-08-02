import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { packetsApi } from '@/services/api'
import type { Flow } from '@/types'

export default function Flows() {
  const { data, isLoading } = useQuery({
    queryKey: ['flows'],
    queryFn: async () => {
      const { data } = await packetsApi.flows({ page: 1, page_size: 50 })
      return data
    },
    refetchInterval: 5000,
  })

  const flows: Flow[] = data?.items ?? []

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Network Flows</h1>
        <p className="text-sm text-muted-foreground">Aggregated network flow data</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Flows ({data?.total ?? 0})</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-3 font-medium">Status</th>
                    <th className="text-left py-3 font-medium">Protocol</th>
                    <th className="text-left py-3 font-medium">Source</th>
                    <th className="text-left py-3 font-medium">Destination</th>
                    <th className="text-right py-3 font-medium">Pkts Fwd</th>
                    <th className="text-right py-3 font-medium">Pkts Bwd</th>
                    <th className="text-right py-3 font-medium">Bytes Fwd</th>
                    <th className="text-right py-3 font-medium">Bytes Bwd</th>
                    <th className="text-right py-3 font-medium">Duration</th>
                  </tr>
                </thead>
                <tbody>
                  {flows.map((f) => (
                    <tr key={f.id} className="border-b border-border/50 hover:bg-secondary/30 transition-colors">
                      <td className="py-2">
                        {f.is_active ? (
                          <Badge variant="success" className="text-xs">Active</Badge>
                        ) : (
                          <Badge variant="secondary" className="text-xs">Complete</Badge>
                        )}
                      </td>
                      <td className="py-2">
                        <Badge variant="outline" className="text-xs">{f.protocol}</Badge>
                      </td>
                      <td className="py-2 font-mono text-xs">{f.src_ip}:{f.src_port}</td>
                      <td className="py-2 font-mono text-xs">{f.dst_ip}:{f.dst_port}</td>
                      <td className="py-2 text-right">{f.packets_forward}</td>
                      <td className="py-2 text-right">{f.packets_backward}</td>
                      <td className="py-2 text-right">{(f.bytes_forward / 1024).toFixed(1)} KB</td>
                      <td className="py-2 text-right">{(f.bytes_backward / 1024).toFixed(1)} KB</td>
                      <td className="py-2 text-right text-muted-foreground">
                        {f.duration ? `${f.duration.toFixed(1)}s` : '-'}
                      </td>
                    </tr>
                  ))}
                  {flows.length === 0 && (
                    <tr>
                      <td colSpan={9} className="py-8 text-center text-muted-foreground">
                        No flows captured yet
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
