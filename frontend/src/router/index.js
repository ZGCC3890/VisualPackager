import { createRouter, createWebHashHistory } from 'vue-router'
import Login from '../components/login.vue'
import Packager from '../components/packager.vue'

const router = createRouter({
  history: createWebHashHistory('/zgcc/packager'),
  routes: [
    { path: '/:pathMatch(.*)*', redirect: '/login' }, // 重定向不匹配路由到登录页
    { path: '/login', name: 'login', component: Login },
    { path: '/packager', name: 'packager', component: Packager },
  ]
})

router.beforeEach((to, from, next) => {
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'
  if (to.name !== 'login' && !isLoggedIn) {
    next({ name: 'login' })
  } else if (to.name === 'login' && isLoggedIn) {
    next({ name: 'packager' })
  }
  else {
    next()
  }
})

export default router
