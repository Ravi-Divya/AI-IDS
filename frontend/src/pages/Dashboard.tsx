import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Activity, Shield, Siren, Network, Gauge, Zap, Database, Building2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { dashboardApi, simulationApi } from '@/services/api'
import { useAuthStore } from '@/store/authStore'
import { AnimatedCounter } from '@/components/AnimatedCounter'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import type { DashboardStats, TrafficTimeline, Threat } from '@/types'
import toast from 'react-hot-toast'

const COLORS = ['#22c55e', '#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6', '#ec4899']

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 200, damping: 20 } },
}

export default function Dashboard() {
  const queryClient = useQueryClient()
  const user = useAuthStore((s) => s.user)

  const { data: stats, isLoading } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const { data } = await dashboardApi.stats(24)
      return data
    },
    refetchInterval: 10000,
  })

  const { data: threats = [] } = useQuery<Threat[]>({
    queryKey: ['recent-threats'],
    queryFn: async () => {
      const { data } = await dashboardApi.recentThreats(5)
      return data
    },
    refetchInterval: 15000,
  })

  const { data: timeline = [] } = useQuery<TrafficTimeline[]>({
    queryKey: ['traffic-timeline'],
    queryFn: async () => {
      const { data } = await dashboardApi.trafficTimeline(24)
      return data
    },
    refetchInterval: 30000,
  })

  const populateMutation = useMutation({
    mutationFn: () => simulationApi.populate(24),
    onSuccess: (res: any) => {
      queryClient.invalidateQueries()
      toast.success(`Data populated! ${res.data.packets} packets, ${res.data.threats} threats, ${res.data.alerts} alerts created`)
    },
    onError: () => toast.error('Failed to populate data'),
  })

  const generateMutation = useMutation({
    mutationFn: () => simulationApi.generate(30, 0.2),
    onSuccess: (res: any) => {
      queryClient.invalidateQueries()
      toast.success(`Live batch: ${res.data.packets} packets, ${res.data.threats} threats generated`)
    },
    onError: () => toast.error('Failed to generate traffic'),
  })

  const statCards = [
    { title: 'Packets Captured', value: stats?.total_packets ?? 0, icon: Network, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { title: 'Active Flows', value: stats?.active_flows ?? 0, icon: Activity, color: 'text-green-500', bg: 'bg-green-500/10' },
    { title: 'Threats Detected', value: stats?.total_threats ?? 0, icon: Siren, color: 'text-red-500', bg: 'bg-red-500/10' },
    { title: 'Packets/sec', value: stats?.packets_per_second ?? 0, icon: Gauge, color: 'text-yellow-500', bg: 'bg-yellow-500/10', suffix: '/s' },
  ]

  const pieData = stats?.threats_by_type
    ? Object.entries(stats.threats_by_type).map(([name, value]) => ({ name, value }))
    : []

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    )
  }

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item} className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            {user?.company_name && <Building2 className="h-4 w-4 text-primary" />}
            <h1 className="text-2xl font-bold">{user?.company_name ? `${user.company_name} Security` : 'Security Dashboard'}</h1>
          </div>
          <p className="text-sm text-muted-foreground">Real-time network security monitoring</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Button
            variant="outline"
            size="sm"
            onClick={() => populateMutation.mutate()}
            disabled={populateMutation.isPending}
            className="group"
          >
            <Database className="h-4 w-4 mr-1 transition-transform group-hover:scale-110" />
            {populateMutation.isPending ? 'Populating...' : 'Populate 24h Data'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="group"
          >
            <Zap className="h-4 w-4 mr-1 transition-transform group-hover:scale-110" />
            {generateMutation.isPending ? 'Generating...' : 'Generate Live Traffic'}
          </Button>
          <Badge variant="success" className="text-xs animate-pulse">
            <Shield className="h-3 w-3 mr-1" />
            System Active
          </Badge>
        </div>
      </motion.div>

      <motion.div variants={item} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => (
          <motion.div key={stat.title} whileHover={{ scale: 1.02 }} transition={{ type: 'spring', stiffness: 300, damping: 15 }}>
            <Card className="card-hover">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{stat.title}</p>
                    <p className="text-2xl font-bold mt-1">
                      <AnimatedCounter value={stat.value} suffix={stat.suffix} />
                    </p>
                  </div>
                  <div className={`p-3 rounded-full ${stat.bg} transition-transform group-hover:scale-110`}>
                    <stat.icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </motion.div>

      <motion.div variants={item} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="card-hover">
          <CardHeader>
            <CardTitle className="text-sm font-medium">Traffic Timeline (24h)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={timeline}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="time" tick={{ fontSize: 10 }} tickFormatter={(v) => v.split(' ')[1]?.slice(0, 2) + 'h' || v} />
                  <YAxis tick={{ fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px' }}
                    labelStyle={{ color: 'hsl(var(--foreground))' }}
                    itemStyle={{ color: 'hsl(var(--foreground))' }}
                  />
                  <Line type="monotone" dataKey="packets" stroke="#22c55e" strokeWidth={2} dot={false} name="Packets" />
                  <Line type="monotone" dataKey="threats" stroke="#ef4444" strokeWidth={2} dot={false} name="Threats" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="card-hover">
          <CardHeader>
            <CardTitle className="text-sm font-medium">Threat Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
                    {pieData.map((_, idx) => (
                      <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px' }}
                    labelStyle={{ color: 'hsl(var(--foreground))' }}
                    itemStyle={{ color: 'hsl(var(--foreground))' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex flex-wrap justify-center gap-2 mt-2">
                {pieData.map((entry, idx) => (
                  <div key={entry.name} className="flex items-center gap-1 text-xs">
                    <div className="w-2 h-2 rounded-full" style={{ background: COLORS[idx % COLORS.length] }} />
                    <span className="text-muted-foreground">{entry.name}</span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={item}>
        <Card className="card-hover">
          <CardHeader>
            <CardTitle className="text-sm font-medium">Recent Threats</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {threats.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">No threats detected</p>
              ) : (
                threats.map((threat, i) => (
                  <motion.div
                    key={threat.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-lg bg-secondary/50 gap-2 hover:bg-secondary/80 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`p-1.5 rounded-full ${threat.severity === 'critical' || threat.severity === 'high' ? 'bg-red-500/10' : 'bg-yellow-500/10'}`}>
                        <Siren className={`h-3.5 w-3.5 ${threat.severity === 'critical' || threat.severity === 'high' ? 'text-red-500' : 'text-yellow-500'}`} />
                      </div>
                      <div>
                        <p className="text-sm font-medium">{threat.threat_type}</p>
                        <p className="text-xs text-muted-foreground font-mono">{threat.src_ip} → {threat.dst_ip}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 self-start sm:self-auto pl-7 sm:pl-0">
                      <Badge variant={
                        threat.severity === 'critical' ? 'danger' :
                        threat.severity === 'high' ? 'warning' : 'info'
                      }>
                        {threat.severity}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(threat.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}
