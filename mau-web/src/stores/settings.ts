import { defineStore } from 'pinia'
import { ref, type Ref } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  const topFilter: Ref<string, string> = ref('gems')

  return { topFilter }
})
