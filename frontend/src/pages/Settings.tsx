import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Bell } from 'lucide-react'
import api from '@/services/api'
import { useNotifications } from '@/hooks/useNotifications'

export default function Settings() {
  const { data, isLoading } = useQuery({
    queryKey: ['settings'],
    queryFn: async () => {
      const { data } = await api.get('/settings/')
      return data
    },
  })

  const { data: channelStatus } = useQuery({
    queryKey: ['channel-status'],
    queryFn: async () => {
      const { data } = await api.get('/alerts/channels/status')
      return data as Record<string, boolean>
    },
  })

  const { enabled: notifEnabled, permission, enable, disable } = useNotifications()

  const settings: any[] = data?.items ?? []

  const permissionLabel: Record<NotificationPermission, string> = {
    granted: 'Granted',
    denied: 'Blocked',
    default: 'Not Requested',
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-sm text-muted-foreground">System configuration</p>
      </div>

      {/* Browser Notifications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-sm font-medium">
            <Bell className="h-4 w-4" />
            Browser Notifications
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm">
                {notifEnabled ? 'Notifications are enabled' : 'Notifications are disabled'}
              </p>
              <p className="text-xs text-muted-foreground">
                Permission: {permissionLabel[permission]}
              </p>
            </div>
            <div className="flex items-center gap-3">
              {permission === 'default' && (
                <Button size="sm" onClick={enable}>
                  <Bell className="h-4 w-4 mr-1" />
                  Allow Notifications
                </Button>
              )}
              {permission === 'granted' && (
                <Switch checked={notifEnabled} onCheckedChange={(v) => (v ? enable() : disable())} />
              )}
              {permission === 'denied' && (
                <p className="text-xs text-muted-foreground">Unblock in browser settings</p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Channel Status */}
      {channelStatus && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Notification Channels (Server)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(channelStatus).map(([channel, active]) => (
                <div key={channel} className="flex items-center justify-between p-2 rounded-lg bg-secondary/50">
                  <span className="text-sm capitalize">{channel}</span>
                  {active ? (
                    <Badge variant="success" className="text-xs">Connected</Badge>
                  ) : (
                    <Badge variant="secondary" className="text-xs">Not Configured</Badge>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* System Config */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          ) : (
            <div className="space-y-2">
              {settings.map((s) => (
                <div key={s.id} className="flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-lg bg-secondary/50 gap-2">
                  <div>
                    <p className="text-sm font-medium">{s.key}</p>
                    <p className="text-xs text-muted-foreground">{s.description}</p>
                  </div>
                  <div className="flex flex-wrap items-center gap-2 self-start sm:self-auto">
                    <Badge variant="outline">{s.category}</Badge>
                    <code className="text-xs bg-background px-2 py-1 rounded break-all max-w-full">
                      {typeof s.value === 'object' ? JSON.stringify(s.value) : String(s.value)}
                    </code>
                  </div>
                </div>
              ))}
              {settings.length === 0 && (
                <p className="text-center py-8 text-muted-foreground">No settings configured</p>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
