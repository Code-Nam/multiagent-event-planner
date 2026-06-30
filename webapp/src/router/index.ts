import { createRouter, createWebHistory } from 'vue-router'
import SetupView from '../views/setup-view.vue'
import VenuesView from '../views/venues-view.vue'
import BudgetView from '../views/budget-view.vue'
import PlanView from '../views/plan-view.vue'
import EmailsView from '../views/emails-view.vue'
import ExportView from '../views/export-view.vue'
import PipelineView from '../views/pipeline-view.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/setup' },
    { path: '/setup', component: SetupView },
    { path: '/venues', component: VenuesView },
    { path: '/budget', component: BudgetView },
    { path: '/plan', component: PlanView },
    { path: '/emails', component: EmailsView },
    { path: '/export', component: ExportView },
    { path: '/pipeline', component: PipelineView }
  ]
})

export default router
