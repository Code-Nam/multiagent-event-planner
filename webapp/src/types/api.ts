export interface TokenUsage {
  input_tokens: number
  output_tokens: number
  cache_creation_input_tokens: number
  cache_read_input_tokens: number
  total_tokens: number
  api_call_count: number
}

export interface AgentMeta {
  agent_type: string
  description: string
  spawn_depth: number
  usage: TokenUsage | null
  model: string | null
}

export interface Job {
  id: string
  name: string
  template: string
  state: string
  tokens: number
  model: string | null
  usage: TokenUsage | null
  cwd: string
  project: string
  created_at: string
  updated_at: string
  source: string
}

export interface JobDetail extends Job {
  agents: AgentMeta[]
}

export interface JobList {
  jobs: Job[]
  total: number
}

export interface LiveSnapshot {
  job_id: string
  state: string
  tokens: number
  updated_at: string
  usage: TokenUsage | null
}
