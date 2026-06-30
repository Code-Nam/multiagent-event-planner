import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import EventForm from './event-form.vue'
import type { EventContext } from '../types/api'

const sampleContext: EventContext = {
  name: 'Summer Gala',
  date: '2026-07-01',
  type: 'gala',
  expected_attendance: '200',
  fixed_budget: '15000',
  event_lead: 'Alice Durand',
  preferred_area: '11e arrondissement',
  constraints: 'No loud music after 22h',
}

describe('EventForm', () => {
  it('renders without initial prop without crashing', () => {
    const wrapper = mount(EventForm)
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('populates name input from initial prop', () => {
    const wrapper = mount(EventForm, { props: { initial: sampleContext } })
    const input = wrapper.find('input[type="text"]')
    expect((input.element as HTMLInputElement).value).toBe('Summer Gala')
  })

  it('populates date input from initial prop', () => {
    const wrapper = mount(EventForm, { props: { initial: sampleContext } })
    const input = wrapper.find('input[type="date"]')
    expect((input.element as HTMLInputElement).value).toBe('2026-07-01')
  })

  it('renders event type select', () => {
    const wrapper = mount(EventForm, { props: { initial: sampleContext } })
    const select = wrapper.find('select')
    expect(select.exists()).toBe(true)
  })

  it('populates type select from initial prop', () => {
    const wrapper = mount(EventForm, { props: { initial: sampleContext } })
    const select = wrapper.find('select')
    expect((select.element as HTMLSelectElement).value).toBe('gala')
  })

  it('renders textarea for constraints', () => {
    const wrapper = mount(EventForm, { props: { initial: sampleContext } })
    const textarea = wrapper.find('textarea')
    expect(textarea.exists()).toBe(true)
  })

  it('populates constraints textarea from initial prop', () => {
    const wrapper = mount(EventForm, { props: { initial: sampleContext } })
    const textarea = wrapper.find('textarea')
    expect((textarea.element as HTMLTextAreaElement).value).toBe(
      'No loud music after 22h'
    )
  })

  it('emits submit with correct EventContext data on form submit', async () => {
    const wrapper = mount(EventForm, { props: { initial: sampleContext } })
    await wrapper.find('form').trigger('submit')

    const emitted = wrapper.emitted('submit')
    expect(emitted).toBeTruthy()
    expect(emitted![0][0]).toEqual(sampleContext)
  })

  it('emits submit with empty strings when no initial prop provided', async () => {
    const wrapper = mount(EventForm)
    await wrapper.find('form').trigger('submit')

    const emitted = wrapper.emitted('submit')
    expect(emitted).toBeTruthy()
    const data = emitted![0][0] as EventContext
    expect(data.name).toBe('')
    expect(data.date).toBe('')
    expect(data.type).toBe('')
  })
})
