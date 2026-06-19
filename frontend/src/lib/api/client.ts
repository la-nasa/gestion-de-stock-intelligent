import axios, { AxiosError, InternalAxiosRequestConfig } from "axios"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
})

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token")
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - Handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem("refresh_token")
        if (!refreshToken) throw new Error("No refresh token")

        const response = await axios.post(`${API_URL}/api/v1/auth/refresh/`, {
          refresh_token: refreshToken,
        })

        const { access_token, refresh_token } = response.data.data
        localStorage.setItem("access_token", access_token)
        localStorage.setItem("refresh_token", refresh_token)

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`
        }

        return apiClient(originalRequest)
      } catch (refreshError) {
        localStorage.removeItem("access_token")
        localStorage.removeItem("refresh_token")
        window.location.href = "/login"
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// API helper functions
export async function get<T>(url: string, params?: Record<string, any>) {
  const response = await apiClient.get<T>(url, { params })
  return response.data
}

export async function post<T>(url: string, data?: any) {
  const response = await apiClient.post<T>(url, data)
  return response.data
}

export async function patch<T>(url: string, data?: any) {
  const response = await apiClient.patch<T>(url, data)
  return response.data
}

export async function del<T>(url: string) {
  const response = await apiClient.delete<T>(url)
  return response.data
}

export default apiClient
