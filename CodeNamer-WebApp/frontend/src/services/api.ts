import axios from 'axios'
import type { CodeAnalysisRequest, CodeAnalysisResponse } from '../types'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const analyzeCode = async (request: CodeAnalysisRequest): Promise<CodeAnalysisResponse> => {
  const response = await api.post<CodeAnalysisResponse>('/analyze', request)
  return response.data
}

export const healthCheck = async (): Promise<{ status: string }> => {
  const response = await api.get<{ status: string }>('/health')
  return response.data
}
