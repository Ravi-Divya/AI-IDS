import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Menu, Shield } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/store/authStore'
import { NotificationManager } from '@/components/NotificationManager'
import { NotificationBell } from '@/components/NotificationBell'

export function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const user = useAuthStore((s) => s.user)

  return (
    <>
      <NotificationManager />
      <div className="flex h-screen overflow-hidden bg-background">
      {/* Responsive Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      {/* Main Content Area */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top Header */}
        <header className="flex h-14 items-center justify-between border-b border-border bg-card px-4 flex-shrink-0">
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(true)}
              className="md:hidden"
              aria-label="Open sidebar"
            >
              <Menu className="h-5 w-5" />
            </Button>
            <Shield className="h-5 w-5 text-primary hidden md:block" />
            <span className="font-bold text-sm">{user?.company_name || 'AI-IDS'}</span>
          </div>
          <NotificationBell />
        </header>

        {/* Responsive main padding */}
        <main className="flex-1 overflow-y-auto bg-background p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
    </>
  )
}
