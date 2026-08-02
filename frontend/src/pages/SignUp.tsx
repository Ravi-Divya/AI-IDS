import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Shield, Eye, EyeOff, ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { authApi } from '@/services/api'
import { useAuthStore } from '@/store/authStore'
import toast from 'react-hot-toast'

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  transition: { delay, duration: 0.4, ease: 'easeOut' },
})

export default function SignUp() {
  const [form, setForm] = useState({ email: '', username: '', password: '', full_name: '' })
  const [showPassword, setShowPassword] = useState(false)
  const queryClient = useQueryClient()
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.email || !form.username || !form.password) return
    setLoading(true)
    try {
      const { data } = await authApi.register({
        email: form.email,
        username: form.username,
        password: form.password,
        full_name: form.full_name || undefined,
      })
      setAuth(data.user, {
        access_token: data.access_token,
        refresh_token: data.refresh_token,
        token_type: 'bearer',
      })
      queryClient.invalidateQueries()
      toast.success('Account created!')
      navigate(data.user.company_name ? '/dashboard' : '/setup-company')
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-primary/5 p-4 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,hsl(var(--primary)/0.08),transparent_50%)]" />
      <motion.div className="w-full max-w-md relative" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, ease: 'easeOut' }}>
        <motion.div {...fadeUp(0)}>
          <Button variant="ghost" size="sm" onClick={() => navigate('/')} className="mb-4 gap-2 group">
            <ArrowLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
            Back to Home
          </Button>
        </motion.div>
        <Card className="border-primary/10">
          <CardHeader className="text-center">
            <motion.div {...fadeUp(0.1)}>
              <div className="flex justify-center mb-4">
                <div className="p-3 rounded-full bg-primary/10 glow-sm">
                  <Shield className="h-10 w-10 text-primary" />
                </div>
              </div>
            </motion.div>
            <motion.div {...fadeUp(0.15)}>
              <CardTitle className="text-2xl">Create Account</CardTitle>
            </motion.div>
            <motion.div {...fadeUp(0.2)}>
              <CardDescription>Set up your AI-IDS security platform</CardDescription>
            </motion.div>
          </CardHeader>
          <CardContent>
            <motion.form {...fadeUp(0.25)} onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Full Name</label>
                <input
                  type="text"
                  value={form.full_name}
                  onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                  className="w-full px-3 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-1 focus:ring-ring transition-shadow"
                  placeholder="John Doe"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Email</label>
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="w-full px-3 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-1 focus:ring-ring transition-shadow"
                  placeholder="admin@company.com"
                  required
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Username</label>
                <input
                  type="text"
                  value={form.username}
                  onChange={(e) => setForm({ ...form, username: e.target.value })}
                  className="w-full px-3 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-1 focus:ring-ring transition-shadow"
                  placeholder="admin"
                  required
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={form.password}
                    onChange={(e) => setForm({ ...form, password: e.target.value })}
                    className="w-full px-3 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-1 focus:ring-ring pr-10 transition-shadow"
                    placeholder="Min. 8 characters"
                    required
                    minLength={8}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-2.5 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? 'Creating account...' : 'Create Account'}
              </Button>
            </motion.form>
            <motion.p {...fadeUp(0.3)} className="mt-4 text-sm text-center text-muted-foreground">
              Already have an account?{' '}
              <Link to="/login" className="text-primary hover:underline">
                Sign in
              </Link>
            </motion.p>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
