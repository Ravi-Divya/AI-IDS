import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { packetsApi } from '@/services/api'
import type { Packet } from '@/types'

const rowVariant = {
  hidden: { opacity: 0, x: -8 },
  show: (i: number) => ({ opacity: 1, x: 0, transition: { delay: i * 0.02 } }),
}

export default function Packets() {
  const { data, isLoading } = useQuery({
    queryKey: ['packets'],
    queryFn: async () => {
      const { data } = await packetsApi.list({ page: 1, page_size: 50 })
      return data
    },
    refetchInterval: 5000,
  })

  const packets: Packet[] = data?.items ?? []

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ type: 'spring', stiffness: 200, damping: 20 }} className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Live Packets</h1>
        <p className="text-sm text-muted-foreground">Real-time packet capture data</p>
      </div>

      <Card className="card-hover">
        <CardHeader>
          <CardTitle className="text-sm font-medium">Captured Packets ({data?.total ?? 0})</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-secondary/30">
                    <th className="text-left py-3 px-4 font-medium text-xs uppercase tracking-wider text-muted-foreground">Time</th>
                    <th className="text-left py-3 px-4 font-medium text-xs uppercase tracking-wider text-muted-foreground">Protocol</th>
                    <th className="text-left py-3 px-4 font-medium text-xs uppercase tracking-wider text-muted-foreground">Source</th>
                    <th className="text-left py-3 px-4 font-medium text-xs uppercase tracking-wider text-muted-foreground">Destination</th>
                    <th className="text-right py-3 px-4 font-medium text-xs uppercase tracking-wider text-muted-foreground">Size</th>
                    <th className="text-left py-3 px-4 font-medium text-xs uppercase tracking-wider text-muted-foreground">Flags</th>
                  </tr>
                </thead>
                <tbody>
                  {packets.map((p, i) => (
                    <motion.tr
                      key={p.id}
                      custom={i}
                      variants={rowVariant}
                      initial="hidden"
                      animate="show"
                      className="border-b border-border/30 hover:bg-secondary/20 transition-colors even:bg-secondary/10"
                    >
                      <td className="py-2.5 px-4 text-muted-foreground text-xs font-mono">
                        {new Date(p.timestamp).toLocaleTimeString()}
                      </td>
                      <td className="py-2.5 px-4">
                        <Badge variant="outline" className="text-xs font-mono">{p.protocol}</Badge>
                      </td>
                      <td className="py-2.5 px-4 font-mono text-xs">{p.src_ip}:{p.src_port ?? '-'}</td>
                      <td className="py-2.5 px-4 font-mono text-xs">{p.dst_ip}:{p.dst_port ?? '-'}</td>
                      <td className="py-2.5 px-4 text-right font-mono text-xs">{p.packet_size} B</td>
                      <td className="py-2.5 px-4 text-xs font-mono text-muted-foreground">{p.tcp_flags || '-'}</td>
                    </motion.tr>
                  ))}
                  {packets.length === 0 && (
                    <tr>
                      <td colSpan={6} className="py-12 text-center text-muted-foreground">
                        <div className="flex flex-col items-center gap-2">
                          <NetworkIcon />
                          <span>No packets captured yet</span>
                        </div>
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

function NetworkIcon() {
  return (
    <svg className="h-8 w-8 text-muted-foreground/40" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.858 15.355-5.858 21.213 0" />
    </svg>
  )
}
