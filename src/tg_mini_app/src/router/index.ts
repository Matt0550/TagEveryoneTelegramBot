import { createRouter, createWebHistory } from 'vue-router'
import GroupsView from '@/views/GroupsView.vue'
import AdminView from '@/views/AdminView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'groups',
      component: GroupsView
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView
    }
  ]
})

export default router
