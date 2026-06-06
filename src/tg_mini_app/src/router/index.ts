import { createRouter, createWebHistory } from 'vue-router'
import GroupsView from '@/views/GroupsView.vue'
import AdminView from '@/views/AdminView.vue'
import GroupDetailsView from '@/views/GroupDetailsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'groups',
      component: GroupsView
    },
    {
      path: '/groups/:id',
      name: 'group-details',
      component: GroupDetailsView
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView
    }
  ]
})

export default router
