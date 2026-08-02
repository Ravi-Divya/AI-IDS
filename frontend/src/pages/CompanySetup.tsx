import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Shield, Building2, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { authApi } from '@/services/api'
import { useAuthStore } from '@/store/authStore'
import toast from 'react-hot-toast'

export default function CompanySetup() {
  const [companyName, setCompanyName] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const setUser = useAuthStore((s) => s.setUser)
  const user = useAuthStore((s) => s.user)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!companyName.trim()) return
    setLoading(true)
    try {
      const { data } = await authApi.setupCompany(companyName.trim())
      if (user) {
        setUser({ ...user, company_name: data.company_name })
      }
      toast.success(`Welcome to ${data.company_name}!`)
      navigate('/dashboard')
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Failed to setup company')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-primary/5 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-lg"
      >
        <Card>
          <CardHeader className="text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200, delay: 0.1 }}
              className="flex justify-center mb-4"
            >
              <div className="p-3 rounded-full bg-primary/10">
                <Building2 className="h-10 w-10 text-primary" />
              </div>
            </motion.div>
            <CardTitle className="text-2xl">Welcome to AI-IDS</CardTitle>
            <CardDescription>
              You're the first user! Let's set up your company.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <motion.form
              onSubmit={handleSubmit}
              className="space-y-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="text-center space-y-2">
                <Shield className="h-8 w-8 text-primary mx-auto" />
                <p className="text-sm text-muted-foreground">
                  Enter your company name to personalize your security dashboard.
                </p>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Company Name</label>
                <input
                  type="text"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  className="w-full px-4 py-3 rounded-md border border-input bg-background text-base focus:outline-none focus:ring-2 focus:ring-ring"
                  placeholder="e.g. Acme Corp"
                  required
                  autoFocus
                />
              </div>
              <Button type="submit" className="w-full gap-2 py-6 text-base" disabled={loading || !companyName.trim()}>
                {loading ? 'Setting up...' : 'Launch Dashboard'}
                <ArrowRight className="h-5 w-5" />
              </Button>
            </motion.form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
