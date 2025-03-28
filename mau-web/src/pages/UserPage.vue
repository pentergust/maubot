<script setup lang="ts">
import type { User } from '@/share/api/types'
import type { Ref } from 'vue'
import HomeButton from '@/components/buttons/HomeButton.vue'
import ErrorLoadingCard from '@/components/ErrorLoadingCard.vue'
import GetGems from '@/components/user/GetGems.vue'
import UserProfileCard from '@/components/user/UserProfileCard.vue'
import UserSettings from '@/components/user/UserSettings.vue'
import UserStats from '@/components/user/UserStats.vue'
import { getRatingIndex, getUser } from '@/share/api'
import { useNotifyStore } from '@/share/stores/notify'
import { useUserStore } from '@/share/stores/user'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const userStore = useUserStore()
const notifyState = useNotifyStore()

let user: Ref<User | null> = ref(null)
const userTop = ref(0)

if (!route.params.id) {
  user = ref(userStore.getMe())
  if (user.value === null) {
    notifyState.addNotify('Оффлайн', 'Mau сервер не отвечает', 'error')
  }
}

onMounted(async () => {
  if (route.params.id) {
    user.value = await getUser(route.params.id as string)
  }

  if (user.value !== null) {
    userTop.value = await getRatingIndex(user.value.username, 'gems')
  }
})
</script>

<template>
  <div v-if="user">
    <UserProfileCard :user="user" :top-index="userTop" />
    <div class="md:flex md:gap-2">
      <div class="md:flex-1">
        <UserStats :user="user" />
        <UserSettings :user="user" />
      </div>

      <GetGems />
    </div>
  </div>

  <!-- Пока пользователь не успел загрузиться -->
  <section v-else>
    <div class="text-center justify-between bg-linear-160 from-violet-400/40 rounded-xl p-2 mb-4">
      <h2 class="text-xl mb-2 font-bold">Профиль пользователя</h2>
      <div class="text-stone-300">Здесь вы можете просмотреть свою статистику.</div>
    </div>
    <ErrorLoadingCard :block="true" />
  </section>

  <section class="p-2 m-2 absolute bottom-0 right-0 flex gap-2">
    <HomeButton :show-name="true" />
  </section>
</template>
