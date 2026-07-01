import { createRouter, createWebHistory } from 'vue-router'
import SessionsView from '../views/sessions-view.vue'
import SessionDetailView from '../views/session-detail-view.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/sessions' },
    { path: '/sessions', component: SessionsView },
    { path: '/sessions/:sessionId', component: SessionDetailView, props: true }
  ]
})

export default router
