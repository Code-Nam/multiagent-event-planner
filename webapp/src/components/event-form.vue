<script setup lang="ts">
import { reactive } from 'vue'
import type { EventContext } from '../types/api'

const props = defineProps<{ initial?: EventContext | null }>()
const emit = defineEmits<{ (e: 'submit', data: EventContext): void }>()

const form = reactive<EventContext>({
  name: props.initial?.name ?? '',
  date: props.initial?.date ?? '',
  type: props.initial?.type ?? '',
  expected_attendance: props.initial?.expected_attendance ?? '',
  fixed_budget: props.initial?.fixed_budget ?? '',
  event_lead: props.initial?.event_lead ?? '',
  preferred_area: props.initial?.preferred_area ?? '',
  constraints: props.initial?.constraints ?? ''
})

function handleSubmit() {
  emit('submit', { ...form })
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="handleSubmit">
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Event name</label>
        <input
          v-model="form.name"
          type="text"
          required
          placeholder="e.g. Summer Gala 2026"
          class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Date</label>
        <input
          v-model="form.date"
          type="date"
          required
          class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Event type</label>
        <select
          v-model="form.type"
          required
          class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="">Select type…</option>
          <option>festival</option>
          <option>sports</option>
          <option>cultural</option>
          <option>workshop</option>
          <option>gala</option>
          <option>other</option>
        </select>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Expected attendance</label>
        <input
          v-model="form.expected_attendance"
          type="text"
          required
          placeholder="e.g. 200"
          class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Fixed budget (€)</label>
        <input
          v-model="form.fixed_budget"
          type="text"
          required
          placeholder="e.g. 15000"
          class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Event lead</label>
        <input
          v-model="form.event_lead"
          type="text"
          required
          placeholder="Full name"
          class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Preferred area (Paris)</label>
        <input
          v-model="form.preferred_area"
          type="text"
          placeholder="e.g. 11e arrondissement"
          class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>
    </div>
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">Constraints / notes</label>
      <textarea
        v-model="form.constraints"
        rows="3"
        placeholder="Accessibility, catering requirements, AV needs…"
        class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />
    </div>
    <div class="flex justify-end">
      <button
        type="submit"
        class="rounded-md bg-indigo-600 px-5 py-2 text-sm font-semibold text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors"
      >
        Save event
      </button>
    </div>
  </form>
</template>
