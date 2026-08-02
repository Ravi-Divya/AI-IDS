import { NavLink } from 'react-router-dom'
import {
  Shield, Activity, BarChart3, Siren, AlertTriangle,
  Brain, Settings, Users, LogOut, ChevronLeft,
  Network, FileText, X
} from 'lucide-react'
import { cn } from '@/utils/cn'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/store/authStore'
import { useState } from 'react'

const navItems = [
  { to: '/dashboard', icon: Activity, label: 'Dashboard' },
  { to: '/packets', icon: Network, label: 'Live Packets' },
  { to: '/flows', icon: BarChart3, label: 'Network Flows' },
  { to: '/threats', icon: Siren, label: 'Threats' },
  { to: '/alerts', icon: AlertTriangle, label: 'Alerts' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/ml', icon: Brain, label: 'Machine Learning' },
  { to: '/users', icon: Users, label: 'Users' },
  { to: '/logs', icon: FileText, label: 'Logs' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false)
  const logout = useAuthStore((s) => s.logout)
  const user = useAuthStore((s) => s.user)

  return (
    <>
      {/* Backdrop overlay for mobile screen viewports */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm transition-opacity md:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={cn(
          // Base transition and border
          'flex flex-col border-r border-border bg-sidebar transition-all duration-300 z-50',
          // Desktop width settings
          collapsed ? 'md:w-16' : 'md:w-64',
          // Mobile responsive slide-out positioning
          'fixed inset-y-0 left-0 w-64 transform md:relative md:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <Shield className="h-8 w-8 text-primary flex-shrink-0" />
            {(!collapsed || isOpen) && (
              <div className="flex flex-col">
                <span className="font-bold text-sm">{user?.company_name || 'AI-IDS'}</span>
                <span className="text-[10px] text-muted-foreground">Security Dashboard</span>
              </div>
            )}
          </div>
          {/* Close button for Mobile screen widths */}
          <button
            onClick={onClose}
            className="p-1.5 rounded-md text-muted-foreground hover:bg-secondary md:hidden"
            aria-label="Close sidebar"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              onClick={onClose}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors',
                  isActive
                    ? 'bg-primary/10 text-primary font-medium'
                    : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                )
              }
            >
              <Icon className="h-4 w-4 flex-shrink-0" />
              {(!collapsed || isOpen) && <span>{label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* Collapse toggle (only for desktop screen widths) */}
        <div className="p-2 border-t border-border hidden md:block">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex items-center gap-3 px-3 py-2 w-full rounded-md text-sm text-muted-foreground hover:bg-secondary transition-colors"
          >
            <ChevronLeft className={cn('h-4 w-4 transition-transform', collapsed && 'rotate-180')} />
            {!collapsed && <span>Collapse</span>}
          </button>
        </div>

        <div className="p-2 border-t border-border">
          {(!collapsed || isOpen) && user && (
            <div className="px-3 py-2 text-xs text-muted-foreground truncate">
              {user.email}
            </div>
          )}
          <Button variant="ghost" size="sm" className="w-full justify-start gap-3" onClick={logout}>
            <LogOut className="h-4 w-4" />
            {(!collapsed || isOpen) && <span>Logout</span>}
          </Button>
        </div>
      </aside>
    </>
  )
}
