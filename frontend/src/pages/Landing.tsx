import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, useScroll, useTransform, useInView } from 'framer-motion'
import { Shield, Activity, Brain, Siren, ArrowRight, Server, Lock, Zap, BarChart3 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/store/authStore'

const Section = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-80px' })
  return (
    <motion.section
      ref={ref}
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className={`py-20 md:py-28 px-4 md:px-8 ${className}`}
    >
      {children}
    </motion.section>
  )
}

function FloatingOrbs() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {[...Array(3)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full opacity-20"
          style={{
            width: `${280 + i * 180}px`,
            height: `${280 + i * 180}px`,
            background: `radial-gradient(circle, hsl(var(--primary)) 0%, transparent 70%)`,
            left: `${18 + i * 28}%`,
            top: `${8 + i * 22}%`,
          }}
          animate={{
            x: [0, 60, 0, -40, 0],
            y: [0, -50, 30, -20, 0],
            scale: [1, 1.08, 0.96, 1.04, 1],
          }}
          transition={{ duration: 14 + i * 4, repeat: Infinity, ease: 'easeInOut' }}
        />
      ))}
    </div>
  )
}

function ParticleField() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animId: number
    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    resize()
    window.addEventListener('resize', resize)

    const particles: { x: number; y: number; vx: number; vy: number; size: number }[] = []
    for (let i = 0; i < 70; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.6,
        vy: (Math.random() - 0.5) * 0.6,
        size: Math.random() * 1.8 + 0.3,
      })
    }

    function animate() {
      if (!ctx || !canvas) return
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      for (const p of particles) {
        p.x += p.vx
        p.y += p.vy
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
        ctx.fillStyle = 'hsl(var(--primary) / 0.25)'
        ctx.fill()
      }
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x
          const dy = particles[i].y - particles[j].y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < 130) {
            ctx.strokeStyle = `hsl(var(--primary) / ${0.08 * (1 - dist / 130)})`
            ctx.lineWidth = 0.5
            ctx.beginPath()
            ctx.moveTo(particles[i].x, particles[i].y)
            ctx.lineTo(particles[j].x, particles[j].y)
            ctx.stroke()
          }
        }
      }
      animId = requestAnimationFrame(animate)
    }
    animate()
    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener('resize', resize)
    }
  }, [])

  return <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none" />
}

export default function Landing() {
  const navigate = useNavigate()
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const { scrollYProgress } = useScroll()
  const heroScale = useTransform(scrollYProgress, [0, 0.4], [1, 0.92])
  const heroOpacity = useTransform(scrollYProgress, [0, 0.3], [1, 0])

  const features = [
    { icon: Brain, title: 'AI-Powered Detection', description: 'Machine learning models that detect network intrusions with 99.2% accuracy in real-time.' },
    { icon: Activity, title: 'Real-Time Monitoring', description: 'Continuous packet capture and flow analysis with instant threat identification and alerting.' },
    { icon: Siren, title: 'Smart Alerting', description: 'Multi-channel notifications via Discord, Slack, Telegram, Email, and more.' },
    { icon: BarChart3, title: 'Advanced Analytics', description: 'Comprehensive dashboards with traffic patterns, threat distribution, and trend analysis.' },
    { icon: Server, title: 'Network Flow Analysis', description: 'Deep packet inspection with 60+ extracted features per flow for maximum visibility.' },
    { icon: Lock, title: 'Enterprise Security', description: 'Role-based access control, audit logging, and compliance-ready security features.' },
  ]

  return (
    <div>
      {/* Hero */}
      <motion.section style={{ scale: heroScale, opacity: heroOpacity }} className="relative min-h-[90vh] flex flex-col items-center justify-center overflow-hidden">
        <FloatingOrbs />
        <ParticleField />

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="relative z-10 text-center max-w-4xl mx-auto px-4"
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200, delay: 0.1 }}
            className="flex justify-center mb-8"
          >
            <div className="p-4 rounded-full bg-primary/10 border border-primary/20 glow-sm">
              <Shield className="h-14 w-14 text-primary" />
            </div>
          </motion.div>

          <motion.h1
            className="text-5xl md:text-7xl font-bold tracking-tight mb-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
          >
            <span className="text-gradient">AI-IDS</span>
          </motion.h1>

          <motion.p
            className="text-xl md:text-2xl text-muted-foreground mb-3"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
          >
            AI-Driven Intrusion Detection System
          </motion.p>

          <motion.p
            className="text-base md:text-lg text-muted-foreground/70 mb-10 max-w-xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.7 }}
          >
            Enterprise-grade network security powered by machine learning. Detect, analyze, and respond to threats in real-time.
          </motion.p>

          <motion.div
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.9 }}
          >
            <Button size="lg" onClick={() => navigate(isAuthenticated ? '/dashboard' : '/signup')} className="gap-2 text-base px-8 py-6">
              {isAuthenticated ? 'Go to Dashboard' : 'Get Started'}
              <ArrowRight className="h-5 w-5" />
            </Button>
            <Button variant="outline" size="lg" onClick={() => navigate('/login')} className="text-base px-8 py-6">
              Sign In
            </Button>
          </motion.div>
        </motion.div>
      </motion.section>

      {/* How It Works */}
      <Section className="bg-secondary/30">
        <div className="max-w-5xl mx-auto w-full">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">How It Works</h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              From raw network traffic to actionable security insights in four simple steps.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              { step: '01', title: 'Capture', desc: 'Continuous packet capture from your network interfaces with zero packet loss.', icon: Activity },
              { step: '02', title: 'Analyze', desc: '60+ features extracted per flow. ML models analyze patterns in real-time.', icon: Brain },
              { step: '03', title: 'Detect', desc: 'Threats identified with confidence scoring. False positives minimized by ensemble models.', icon: Siren },
              { step: '04', title: 'Respond', desc: 'Instant alerts via your preferred channels. Detailed forensics for every incident.', icon: Zap },
            ].map((item, i) => (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.12, duration: 0.5 }}
                className="text-center group"
              >
                <div className="w-16 h-16 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center mx-auto mb-4 group-hover:border-primary/40 group-hover:glow-sm transition-all duration-300">
                  <item.icon className="h-7 w-7 text-primary" />
                </div>
                <div className="text-sm text-primary font-mono mb-2">{item.step}</div>
                <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>

      {/* Features */}
      <Section>
        <div className="max-w-6xl mx-auto w-full">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">Everything You Need</h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Comprehensive security monitoring platform built for modern networks.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.06, duration: 0.4 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
                className="p-6 rounded-xl border border-border bg-card card-hover"
              >
                <div className="p-3 rounded-lg bg-primary/10 w-fit mb-4">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>

      {/* Stats */}
      <Section className="bg-secondary/30">
        <div className="max-w-5xl mx-auto w-full text-center">
          <h2 className="text-3xl md:text-5xl font-bold mb-14">Trusted by Security Teams</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { value: '99.2%', label: 'Detection Accuracy' },
              { value: '<50ms', label: 'Response Time' },
              { value: '60+', label: 'Features Extracted' },
              { value: '24/7', label: 'Threat Monitoring' },
            ].map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.5 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, type: 'spring', stiffness: 120, damping: 12 }}
              >
                <div className="text-4xl md:text-5xl font-bold text-gradient mb-2">{stat.value}</div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>

      {/* CTA */}
      <Section>
        <div className="max-w-3xl mx-auto w-full text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="p-12 md:p-16 rounded-2xl border border-primary/20 bg-gradient-to-br from-primary/[0.04] to-primary/[0.08] card-hover"
          >
            <Shield className="h-12 w-12 text-primary mx-auto mb-6" />
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to Secure Your Network?
            </h2>
            <p className="text-muted-foreground text-lg mb-8 max-w-xl mx-auto leading-relaxed">
              Get started with AI-IDS today. Deploy in minutes and gain enterprise-grade intrusion detection powered by machine learning.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button size="lg" onClick={() => navigate('/signup')} className="gap-2 text-base px-8 py-6">
                Get Started Free
                <ArrowRight className="h-5 w-5" />
              </Button>
              <Button variant="outline" size="lg" onClick={() => navigate('/login')} className="text-base px-8 py-6">
                Sign In
              </Button>
            </div>
          </motion.div>
        </div>
      </Section>

      {/* Footer */}
      <footer className="border-t border-border py-10 text-center text-sm text-muted-foreground">
        <div className="flex items-center justify-center gap-2 mb-2">
          <Shield className="h-4 w-4 text-primary" />
          <span className="font-semibold text-foreground">AI-IDS</span>
        </div>
        <p>AI-Driven Intrusion Detection System &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  )
}
