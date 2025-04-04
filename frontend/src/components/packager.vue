<template>
  <div v-if="showLoginToast" class="login-toast">
    登录成功，欢迎回来！
</div>
</template>

<script setup>
  import { ref, onMounted } from 'vue'

  // 随机背景图片
  const BASE_URL = import.meta.env.BASE_URL
  const backgroundImages = [
    `${BASE_URL}backgrounds/bg1.png`,
    `${BASE_URL}backgrounds/bg2.png`,
    `${BASE_URL}backgrounds/bg3.png`,
    `${BASE_URL}backgrounds/bg4.png`
  ]

  onMounted(() => {
    const randomIndex = Math.floor(Math.random() * backgroundImages.length)
    const selectedImage = backgroundImages[randomIndex]
    console.log("Selected background:", selectedImage)
    document.body.style.backgroundImage = `url(${selectedImage})`
    document.body.style.backgroundSize = 'cover'
    document.body.style.backgroundRepeat = 'no-repeat'
  })

  // 登录成功提示
  const showLoginToast = ref(false)
  onMounted(() => {
  if (localStorage.getItem('showLoginToast') === 'true') {
    showLoginToast.value = true
    localStorage.removeItem('showLoginToast')
    setTimeout(() => {
      showLoginToast.value = false
    }, 5000)
  }
  })


</script>

<style scoped>
.login-toast {
  position: fixed;
  top: 50px;
  left: 50%;
  transform: translateX(-50%);
  background: #4caf50;
  color: white;
  padding: 10px 20px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 999;
  font-size: 14px;
}
</style>