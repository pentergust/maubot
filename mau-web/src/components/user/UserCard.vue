<script setup lang="ts">
import type { User } from '@/share/api/types'
import { Gem, Sparkle, User2 } from 'lucide-vue-next'

const { user, topIndex } = defineProps<{ user: User; topIndex: number }>()
</script>

<template>
  <RouterLink
    to="/me"
    class="p-2 flex justify-between gap-2 my-4 bg-linear-160 from-pink-400/50 rounded-xl transition border-2 border-stone-800 hover:border-stone-600"
  >
    <div class="text-middle my-auto">
      <h2 class="color-stone-800 font-bold text-lg">
        {{ user.name }}
      </h2>
      <div class="flex gap-2">
        <div class="flex text-stone-400 gap-1">{{ user.gems }} <Gem /></div>
        <div class="flex text-stone-400 gap-1">{{ topIndex }} место <Sparkle /></div>
      </div>
    </div>
    <img v-if="user.avatar_url" :src="user.avatar_url" class="w-[64px] h-[64px] rounded-full" />
    <User2 v-else class="w-[64px] h-[64px] rounded-full text-stone-300" />
  </RouterLink>
</template>
