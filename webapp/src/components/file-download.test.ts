import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FileDownload from './file-download.vue'
import type { OutputFile } from '../types/api'

const sampleFile: OutputFile = {
  name: 'recap.xlsx',
  type: 'xlsx',
  path: 'output/recap.xlsx',
}

describe('FileDownload', () => {
  it('renders filename', () => {
    const wrapper = mount(FileDownload, { props: { file: sampleFile } })
    expect(wrapper.text()).toContain('recap.xlsx')
  })

  it('renders file type', () => {
    const wrapper = mount(FileDownload, { props: { file: sampleFile } })
    expect(wrapper.text()).toContain('xlsx')
  })

  it('renders an anchor element with download attribute', () => {
    const wrapper = mount(FileDownload, { props: { file: sampleFile } })
    const anchor = wrapper.find('a')
    expect(anchor.exists()).toBe(true)
    expect(anchor.attributes('download')).toBeDefined()
  })

  it('anchor href contains the filename', () => {
    const wrapper = mount(FileDownload, { props: { file: sampleFile } })
    const href = wrapper.find('a').attributes('href') ?? ''
    expect(href).toContain('recap.xlsx')
  })

  it('anchor href contains /api/output/ path', () => {
    const wrapper = mount(FileDownload, { props: { file: sampleFile } })
    const href = wrapper.find('a').attributes('href') ?? ''
    expect(href).toContain('/api/output/')
  })

  it('URL-encodes filename with spaces in href', () => {
    const fileWithSpaces: OutputFile = {
      name: 'my report.docx',
      type: 'docx',
      path: 'output/my report.docx',
    }
    const wrapper = mount(FileDownload, { props: { file: fileWithSpaces } })
    const href = wrapper.find('a').attributes('href') ?? ''
    expect(href).toContain('my%20report.docx')
  })

  it('renders Download link text', () => {
    const wrapper = mount(FileDownload, { props: { file: sampleFile } })
    expect(wrapper.find('a').text()).toBe('Download')
  })
})
