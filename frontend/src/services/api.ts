import axios from 'axios'
import { useAuthStore } from '@/store/authStore'

const API_URL = import.meta.env.VITE_API_URL || '/api/v1'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().tokens?.access_token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = useAuthStore.getState().tokens?.refresh_token
      if (refreshToken && !error.config._retry) {
        error.config._retry = true
        try {
          const { data } = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })
          useAuthStore.getState().setTokens(data)
          error.config.headers.Authorization = `Bearer ${data.access_token}`
          return api(error.config)
        } catch {
          useAuthStore.getState().logout()
        }
      } else {
        useAuthStore.getState().logout()
      }
    }
    return Promise.reject(error)
  }
)

export default api

export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),
  register: (data: { email: string; username: string; password: string; full_name?: string }) =>
    api.post('/auth/register', data),
  refresh: (refresh_token: string) =>
    api.post('/auth/refresh', { refresh_token }),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
  setupCompany: (company_name: string) =>
    api.post('/auth/setup-company', { company_name }),
}

export const dashboardApi = {
  stats: (hours = 24) => api.get('/dashboard/stats', { params: { hours } }),
  recentThreats: (limit = 10) =>
    api.get('/dashboard/recent-threats', { params: { limit } }),
  trafficTimeline: (hours = 24) =>
    api.get('/dashboard/traffic-timeline', { params: { hours } }),
}

export const packetsApi = {
  list: (params?: Record<string, unknown>) => api.get('/packets/', { params }),
  stats: (hours = 1) => api.get('/packets/stats', { params: { hours } }),
  flows: (params?: Record<string, unknown>) =>
    api.get('/packets/flows', { params }),
  flowStats: (hours = 1) =>
    api.get('/packets/flows/stats', { params: { hours } }),
}

export const threatsApi = {
  list: (params?: Record<string, unknown>) => api.get('/threats/', { params }),
  stats: (hours = 24) => api.get('/threats/stats', { params: { hours } }),
  get: (id: string) => api.get(`/threats/${id}`),
  predictions: (params?: Record<string, unknown>) =>
    api.get('/threats/predictions/all', { params }),
  predictionStats: (hours = 24) =>
    api.get('/threats/predictions/stats', { params: { hours } }),
}

export const alertsApi = {
  list: (params?: Record<string, unknown>) => api.get('/alerts/', { params }),
  get: (id: string) => api.get(`/alerts/${id}`),
  markRead: (id: string) => api.post(`/alerts/${id}/read`),
  acknowledge: (id: string) => api.post(`/alerts/${id}/acknowledge`),
  channelStatus: () => api.get('/alerts/channels/status'),
}

export const mlApi = {
  models: () => api.get('/ml/models'),
  activeModel: () => api.get('/ml/models/active'),
  train: (datasetPath: string) =>
    api.post('/ml/train', null, { params: { dataset_path: datasetPath } }),
  predict: (flowData: Record<string, unknown>) =>
    api.post('/ml/predict', flowData),
  activateModel: (id: string) => api.post(`/ml/models/${id}/activate`),
  generateSample: () => api.post('/ml/generate-sample'),
  uploadDataset: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/ml/upload-dataset', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
}

export const simulationApi = {
  generate: (count = 30, attackRatio = 0.2) =>
    api.post('/simulation/generate', null, { params: { count, attack_ratio: attackRatio } }),
  populate: (hours = 24) =>
    api.post('/simulation/populate', null, { params: { hours } }),
}

