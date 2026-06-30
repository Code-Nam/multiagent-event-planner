<script setup lang="ts">
import { onMounted } from 'vue'
import { useOutputStore } from '../stores/output'
import { usePipelineStore } from '../stores/pipeline'
import RunAgentButton from '../components/run-agent-button.vue'
import FileDownload from '../components/file-download.vue'
import PipelineProgress from '../components/pipeline-progress.vue'

const outputStore = useOutputStore()
const pipelineStore = usePipelineStore()

onMounted(() => { outputStore.fetch() })

const docTypes = [
  { key: 'xlsx', label: 'Generate XLSX', agent: 'py-dev', message: 'generate xlsx from doc-content specs' },
  { key: 'docx', label: 'Generate DOCX', agent: 'py-dev', message: 'generate docx from doc-content specs' },
  { key: 'ppt',  label: 'Generate PPT',  agent: 'py-dev', message: 'generate pptx from doc-content specs' }
]
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-900 mb-1">Export Documents</h1>
    <p class="text-sm text-gray-500 mb-6">Generate XLSX, DOCX, and PPT files from prepared content specs.</p>

    <div class="flex flex-wrap gap-3 mb-6">
      <RunAgentButton
        v-for="dt in docTypes"
        :key="dt.key"
        :agent="dt.agent"
        :label="dt.label"
        :message="dt.message"
      />
    </div>

    <PipelineProgress :log="pipelineStore.log" :running="pipelineStore.running" />

    <div class="mt-8">
      <h2 class="text-lg font-semibold text-gray-800 mb-3">Output files</h2>
      <div v-if="outputStore.loading" class="text-sm text-gray-400">Loading…</div>
      <div v-else-if="outputStore.files.length" class="space-y-2">
        <FileDownload
          v-for="file in outputStore.files"
          :key="file.path"
          :file="file"
        />
      </div>
      <p v-else class="text-sm text-gray-400 italic">No output files yet. Generate a document above.</p>
    </div>
  </div>
</template>
