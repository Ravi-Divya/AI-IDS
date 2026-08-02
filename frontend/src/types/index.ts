export interface User {
  id: string
  email: string
  username: string
  full_name?: string
  is_active: boolean
  is_verified: boolean
  roles: string[]
  last_login?: string
  created_at: string
  company_name?: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginResponse extends AuthTokens {
  user: User
}

export interface Packet {
  id: string
  timestamp: string
  src_ip: string
  dst_ip: string
  protocol: string
  src_port?: number
  dst_port?: number
  packet_size: number
  ttl?: number
  window_size?: number
  tcp_flags?: string
}

export interface Flow {
  id: string
  flow_key: string
  src_ip: string
  dst_ip: string
  src_port: number
  dst_port: number
  protocol: string
  start_time: string
  duration?: number
  packets_forward: number
  packets_backward: number
  bytes_forward: number
  bytes_backward: number
  is_active: boolean
}

export interface Threat {
  id: string
  threat_type: string
  severity: string
  confidence: number
  src_ip: string
  dst_ip: string
  src_port?: number
  dst_port?: number
  protocol?: string
  description?: string
  explanation?: string
  recommendation?: string
  is_mitigated: boolean
  created_at: string
}

export interface Alert {
  id: string
  threat_id: string
  alert_type: string
  title: string
  message: string
  severity: string
  confidence: number
  threat_type: string
  src_ip: string
  dst_ip: string
  explanation?: string
  recommendation?: string
  is_read: boolean
  is_acknowledged: boolean
  created_at: string
}

export interface DashboardStats {
  total_packets: number
  total_flows: number
  active_flows: number
  total_threats: number
  total_alerts: number
  total_predictions: number
  threats_by_type: Record<string, number>
  threats_by_severity: Record<string, number>
  prediction_threat_percentage: number
  model_accuracy?: number
  packets_per_second: number
  recent_threats?: number
  unread_alerts?: number
}

export interface MLModel {
  id: string
  name: string
  model_type: string
  version: string
  accuracy?: number
  f1_macro?: number
  is_active: boolean
  is_trained: boolean
  training_dataset?: string
  training_samples?: number
  created_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface TrafficTimeline {
  time: string
  packets: number
  threats: number
}
