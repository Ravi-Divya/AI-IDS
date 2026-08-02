import { useEffect, useRef, useState } from 'react'

export function AnimatedCounter({ value, suffix = '' }: { value: number; suffix?: string }) {
  const [display, setDisplay] = useState(0)
  const prevRef = useRef(0)
  const rafRef = useRef<number>()

  useEffect(() => {
    const from = prevRef.current
    const to = value
    const duration = 600
    const start = performance.now()

    function tick(now: number) {
      const elapsed = now - start
      const t = Math.min(elapsed / duration, 1)
      const ease = 1 - Math.pow(1 - t, 3)
      const current = Math.round(from + (to - from) * ease)
      setDisplay(current)
      if (t < 1) rafRef.current = requestAnimationFrame(tick)
    }

    prevRef.current = to
    rafRef.current = requestAnimationFrame(tick)
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current) }
  }, [value])

  return <>{display.toLocaleString()}{suffix}</>
}
