import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DraftCard from './draft-card.vue'
import type { DraftSummary } from '../types/api'

const sampleDraft: DraftSummary = {
  name: 'venue-inquiry-2026-07-01.md',
  purpose: 'venue',
  to: 'contact@salledesartes.fr',
  subject: 'Demande de disponibilité — Juillet 2026',
  status: 'draft',
}

describe('DraftCard', () => {
  it('renders purpose badge', () => {
    const wrapper = mount(DraftCard, { props: { draft: sampleDraft } })
    expect(wrapper.text()).toContain('venue')
  })

  it('renders subject', () => {
    const wrapper = mount(DraftCard, { props: { draft: sampleDraft } })
    expect(wrapper.text()).toContain('Demande de disponibilité — Juillet 2026')
  })

  it('renders recipient (to field)', () => {
    const wrapper = mount(DraftCard, { props: { draft: sampleDraft } })
    expect(wrapper.text()).toContain('contact@salledesartes.fr')
  })

  it('renders draft name', () => {
    const wrapper = mount(DraftCard, { props: { draft: sampleDraft } })
    expect(wrapper.text()).toContain('venue-inquiry-2026-07-01.md')
  })

  it('shows Expand button initially', () => {
    const wrapper = mount(DraftCard, { props: { draft: sampleDraft } })
    const button = wrapper.find('button')
    expect(button.text()).toBe('Expand')
  })

  it('emits expand with draft name when Expand button is clicked', async () => {
    const wrapper = mount(DraftCard, { props: { draft: sampleDraft } })
    await wrapper.find('button').trigger('click')

    const emitted = wrapper.emitted('expand')
    expect(emitted).toBeTruthy()
    expect(emitted![0][0]).toBe('venue-inquiry-2026-07-01.md')
  })

  it('toggles button text to Collapse after first click', async () => {
    const wrapper = mount(DraftCard, { props: { draft: sampleDraft } })
    await wrapper.find('button').trigger('click')
    expect(wrapper.find('button').text()).toBe('Collapse')
  })

  it('does not emit expand on second click (collapse)', async () => {
    const wrapper = mount(DraftCard, { props: { draft: sampleDraft } })
    await wrapper.find('button').trigger('click')
    await wrapper.find('button').trigger('click')

    const emitted = wrapper.emitted('expand')
    expect(emitted).toHaveLength(1)
  })
})
