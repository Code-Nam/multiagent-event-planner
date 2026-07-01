<template>
  <div class="flex items-center gap-2 text-sm text-yellow-700">
    <span class="inline-block h-2 w-2 animate-ping rounded-full bg-yellow-400" />
    <span>Live — {{ tokens.toLocaleString() }} tokens</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{ tokens: number }>()
</script>
