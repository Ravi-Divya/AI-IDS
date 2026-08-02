import { useState, useEffect, useCallback, useRef } from 'react'
import api, { alertsApi } from '@/services/api'
import type { Alert } from '@/types'

const LS_ENABLED = 'notifications_enabled'

let _globalEnabled = localStorage.getItem(LS_ENABLED) === 'true'

export function useNotifications() {
  const [enabled, setEnabled] = useState(_globalEnabled)
  const [permission, setPermission] = useState<NotificationPermission>(
    'Notification' in window ? Notification.permission : 'denied'
  )
  const notifiedIdsRef = useRef(new Set<string>())
  const isFirstPollRef = useRef(true)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }, [])

  const startPolling = useCallback(() => {
    stopPolling()
    isFirstPollRef.current = true
    intervalRef.current = setInterval(async () => {
      try {
        const { data } = await alertsApi.list({ unread_only: true, page_size: 20 })
        const alerts: Alert[] = data?.items ?? []
        if (alerts.length === 0) return

        if (isFirstPollRef.current) {
          isFirstPollRef.current = false
          alerts.forEach((a) => notifiedIdsRef.current.add(a.id))
          return
        }

        for (const alert of alerts) {
          if (notifiedIdsRef.current.has(alert.id)) continue
          notifiedIdsRef.current.add(alert.id)
          showDesktopNotification(alert)
        }

        if (notifiedIdsRef.current.size > 500) {
          notifiedIdsRef.current = new Set(
            [...notifiedIdsRef.current].slice(-250)
          )
        }
      } catch { /* ignore polling errors */ }
    }, 10000)
  }, [stopPolling])

  useEffect(() => {
    if (enabled && permission === 'granted') {
      startPolling()
    } else {
      stopPolling()
    }
    return stopPolling
  }, [enabled, permission, startPolling, stopPolling])

  const enable = useCallback(async () => {
    if (!('Notification' in window)) return

    const result = await Notification.requestPermission()
    setPermission(result)

    if (result === 'granted') {
      _globalEnabled = true
      localStorage.setItem(LS_ENABLED, 'true')
      setEnabled(true)
      try { await api.put('/settings/notifications_enabled', { enabled: true }) } catch { /* ignore */ }
    }
  }, [])

  const disable = useCallback(() => {
    _globalEnabled = false
    localStorage.setItem(LS_ENABLED, 'false')
    setEnabled(false)
    stopPolling()
    try { api.put('/settings/notifications_enabled', { enabled: false }) } catch { /* ignore */ }
  }, [stopPolling])

  return { enabled, permission, enable, disable }
}

function showDesktopNotification(alert: Alert) {
  const sev = alert.severity?.toUpperCase() || 'INFO'
  const body = `[${sev}] ${alert.threat_type}\n${alert.src_ip} → ${alert.dst_ip}\n${alert.message?.slice(0, 120)}`

  try {
    const n = new Notification(alert.title || 'Security Alert', {
      body,
      tag: alert.id,
      requireInteraction: alert.severity === 'critical' || alert.severity === 'high',
    })
    n.onclick = () => {
      window.focus()
      window.open('/alerts', '_self')
    }
  } catch { /* notification failed silently */ }
}
