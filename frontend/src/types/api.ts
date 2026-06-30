export interface EventContext {
  name: string
  date: string
  type: string
  expected_attendance: string
  fixed_budget: string
  event_lead: string
  preferred_area: string
  constraints: string
}

export interface DraftSummary {
  name: string
  purpose: string
  to: string
  subject: string
  status: string
}

export interface Draft extends DraftSummary {
  body: string
}

export interface OutputFile {
  name: string
  type: string
  path: string
}

export interface PipelineStatus {
  event_configured: boolean
  drafts_count: number
  doc_content_count: number
  output_count: number
  draft_names: string[]
}

export interface GenerateResult {
  ok: boolean
  path?: string
  error?: string
}
