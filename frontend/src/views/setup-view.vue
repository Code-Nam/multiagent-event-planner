<script setup lang="ts">
import { onMounted } from 'vue'
import { useEventStore } from '../stores/event'
import EventForm from '../components/event-form.vue'
import type { EventContext } from '../types/api'

const store = useEventStore()

onMounted(() => { store.fetch() })

async function handleSubmit(data: EventContext) {
  await store.save(data)
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-900 mb-1">Event Setup</h1>
    <p class="text-sm text-gray-500 mb-6">Configure the core details for your event.</p>

    <div v-if="store.loading" class="text-sm text-gray-400">Loading…</div>

    <div
      v-if="store.error"
      class="mb-4 rounded-md bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700"
    >
      {{ store.error }}
    </div>

    <div
      v-if="!store.loading && store.context && !store.error"
      class="mb-4 rounded-md bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-700"
    >
      Event saved successfully.
    </div>

    <div class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <EventForm :initial="store.context" @submit="handleSubmit" />
    </div>
  </div>
</template>
