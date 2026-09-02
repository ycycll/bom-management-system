import {createRouter, createWebHashHistory} from 'vue-router'
import login from '../views/login.vue'
import sample from '../views/sample.vue'
import home from '../views/home.vue'
import copilot from '../views/copilot.vue'
import hub from '../views/hub.vue'
import defog from '../views/defog.vue'
import agreement from '../views/agreement.vue'
import draw from '../views/draw.vue'
import component from '../views/component.vue'
import archiveQuery from '../views/archiveQuery.vue'
import tool from '../views/tool.vue'
import toolDetail from '../views/tool_detail.vue'

const routes = [
    {
        path: '/',
        name: 'login',
        component: login
    },
    {
        path: '/home',
        name: 'home',
        component: home
    },
    {
        path: '/sample',
        name: 'sample',
        component: sample
    },
    {
        path: '/copilot',
        name: 'copilot',
        component: copilot
    },
    {
        path: '/hub',
        name: 'hub',
        component: hub
    },
    {
        path: '/defog',
        name: 'defog',
        component: defog
    },
    {
        path: '/agreement',
        name: 'agreement',
        component: agreement
    },
    {
        path: '/draw',
        name: 'draw',
        component: draw
    },
    {
        path: '/component',
        name: 'component',
        component: component
    },
    { 
        path: '/archive-query',
        name: 'archiveQuery', 
        component: archiveQuery 
    },
    {
        path: '/tool',
        name: 'tool',
        component: tool
    },
    { 
        path: '/tool/:toolId',
        name: 'toolDetail', 
        component: toolDetail 
    },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})

export default router