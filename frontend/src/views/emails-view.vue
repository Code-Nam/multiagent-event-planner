<script setup lang="ts">
import { onMounted } from 'vue'
import { useDraftsStore } from '../stores/drafts'
import DraftCard from '../components/draft-card.vue'

const store = useDraftsStore()

onMounted(() => { store.fetchList() })

function handleExpand(name: string) {
  store.fetchDraft(name)
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-900 mb-1">Email Drafts</h1>
    <p class="text-sm text-gray-500 mb-6">Browse and preview all drafted emails.</p>

    <div v-if="store.loading" class="text-sm text-gray-400">Loading…</div>

    <div v-else-if="store.list.length" class="space-y-3">
      <DraftCard
        v-for="draft in store.list"
        :key="draft.name"
        :draft="draft"
        @expand="handleExpand"
      >
        <div
          v-if="store.active?.name === draft.name"
          class="border-t border-gray-100 bg-gray-50 px-4 py-3"
        >
          <p class="text-xs text-gray-500 mb-2 font-mono">{{ store.active.subject }}</p>
          <pre class="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed">{{ store.active.body }}</pre>
        </div>
      </DraftCard>
    </div>

    <p v-else class="text-sm text-gray-400 italic">
      No email drafts found. Run the email-drafter agent from the Pipeline view.
    </p>
  </div>
</template>
