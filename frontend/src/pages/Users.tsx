import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { UsersIcon, Shield } from 'lucide-react'
import api from '@/services/api'
import type { User } from '@/types'

const fadeUp = (i: number) => ({
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  transition: { delay: i * 0.04, type: 'spring', stiffness: 200, damping: 20 },
})

export default function Users() {
  const { data, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const { data } = await api.get('/users/', { params: { page: 1, page_size: 100 } })
      return data
    },
  })

  const users: User[] = data?.items ?? []

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ type: 'spring', stiffness: 200, damping: 20 }} className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Users</h1>
        <p className="text-sm text-muted-foreground">User management and roles</p>
      </div>

      <Card className="card-hover">
        <CardHeader>
          <CardTitle className="text-sm font-medium">System Users ({data?.total ?? 0})</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2">
              {users.map((user, i) => (
                <motion.div
                  key={user.id}
                  {...fadeUp(i)}
                  className="flex items-center justify-between p-4 rounded-lg border border-border/50 bg-secondary/20 hover:bg-secondary/40 hover:border-primary/20 transition-all gap-4"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0 ring-1 ring-primary/20">
                      <span className="text-sm font-bold text-primary">
                        {user.username[0].toUpperCase()}
                      </span>
                    </div>
                    <div className="min-w-0">
                      <p className="font-medium text-sm truncate">{user.full_name || user.username}</p>
                      <p className="text-xs text-muted-foreground truncate">{user.email}</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap items-center gap-1.5 shrink-0">
                    {user.roles.map((role) => (
                      <Badge key={role} variant="secondary" className="text-[10px]">{role}</Badge>
                    ))}
                    <Badge variant={user.is_active ? 'success' : 'secondary'} className="text-[10px]">
                      {user.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                </motion.div>
              ))}
              {users.length === 0 && (
                <div className="col-span-full text-center py-12 text-muted-foreground flex flex-col items-center gap-2">
                  <UsersIcon className="h-8 w-8 text-muted-foreground/40" />
                  <span>No users found</span>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
