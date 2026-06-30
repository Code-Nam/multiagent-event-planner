import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PipelineProgress from './pipeline-progress.vue'

describe('PipelineProgress', () => {
  it('renders each log entry', () => {
    const wrapper = mount(PipelineProgress, {
      props: {
        log: ['Starting venue-scout…', 'Searching venues…', 'Done.'],
        running: false,
      },
    })
    expect(wrapper.text()).toContain('Starting venue-scout…')
    expect(wrapper.text()).toContain('Searching venues…')
    expect(wrapper.text()).toContain('Done.')
  })

  it('renders all log entries as individual elements', () => {
    const log = ['line one', 'line two', 'line three']
    const wrapper = mount(PipelineProgress, {
      props: { log, running: false },
    })
    // Each log line should appear separately in the rendered text
    for (const line of log) {
      expect(wrapper.text()).toContain(line)
    }
  })

  it('shows spinner/loading indicator when running prop is true', () => {
    const wrapper = mount(PipelineProgress, {
      props: { log: [], running: true },
    })
    // The spinner SVG or loading element should be present
    const spinner = wrapper.find('[data-testid="spinner"], .animate-spin, [aria-label="loading"]')
    expect(spinner.exists()).toBe(true)
  })

  it('hides spinner/loading indicator when running prop is false', () => {
    const wrapper = mount(PipelineProgress, {
      props: { log: ['Done'], running: false },
    })
    const spinner = wrapper.find('[data-testid="spinner"], .animate-spin, [aria-label="loading"]')
    expect(spinner.exists()).toBe(false)
  })

  it('renders empty log without error', () => {
    const wrapper = mount(PipelineProgress, {
      props: { log: [], running: false },
    })
    expect(wrapper.exists()).toBe(true)
  })
})
