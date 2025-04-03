import { createRouter, createWebHashHistory } from 'vue-router'
import Login from '../components/login.vue'
import Packager from '../components/packager.vue'

const router = createRouter({
  history: createWebHashHistory('/zgcc/packager'),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/packager',
      name: 'packager',
      component: Packager
    }
  ]
})

export default router
