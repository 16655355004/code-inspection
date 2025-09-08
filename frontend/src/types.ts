export interface AnalysisResult {
  line: number
  name: string
  rule_id: string
  message: string
  severity: 'warning' | 'error' | 'info'
}

export interface CodeAnalysisRequest {
  language: string
  code: string
}

export interface CodeAnalysisResponse {
  results: AnalysisResult[]
  total_issues: number
  parser_errors: Array<{ message: string; line: number }>
}

export interface ApiError {
  detail: string
}
