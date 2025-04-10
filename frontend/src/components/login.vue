<template>
  <div class="login-container">
    <div class="login-title">装箱助手登录系统</div>

    <div class="login-card">
      <div class="login-image">
        <img src="/packager.png" alt="login" />
      </div>

      <div class="login-form">
        <input v-model="username" placeholder="用户名" class="login-input" />
        <input v-model="password" type="password" placeholder="密码" class="login-input" />
        <button @click="handleLogin" class="login-button">登录</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { userLogin } from '../api/packager'  // 视项目目录结构而定
import { useRouter } from 'vue-router'

const backgroundImages = [
  `/backgrounds/bg1.png`,
  `/backgrounds/bg2.png`,
  `/backgrounds/bg3.png`,
  `/backgrounds/bg4.png`
]

onMounted(() => {
  const randomIndex = Math.floor(Math.random() * backgroundImages.length)
  const selectedImage = backgroundImages[randomIndex]
  console.log("Selected background:", selectedImage)
  document.body.style.backgroundImage = `url(${selectedImage})`
  document.body.style.backgroundSize = 'cover'
  document.body.style.backgroundRepeat = 'no-repeat'
})

const username = ref('')
const password = ref('')
const router = useRouter()

const handleLogin = async () => {
  try {
    const res = await userLogin(username.value, password.value)
    if (res.success) {
      localStorage.setItem('showLoginToast', 'true')
      localStorage.setItem('isLoggedIn', 'true')
      localStorage.setItem('username', res.username)
      router.push({ name: 'packager' })
    } else {
      alert('用户名或密码错误')
    }
  } catch (err) {
    alert('网络错误')
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 圆角主卡片（白底+边框+阴影） */
.login-card {
  display: flex;
  flex-direction: row;
  background: white;
  border: 1px solid #ddd;
  border-radius: 16px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  /* 关键：让子元素右角不超出边框 */
}

/* 图片左侧 */
.login-image {
  width: 300px;
  height: 220px;
  border-top-left-radius: 16px;
  border-bottom-left-radius: 16px;
  overflow: hidden;
}

.login-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-top-right-radius: 0;
  /* 保证右角是直角 */
  border-bottom-right-radius: 0;
}

/* 表单右侧 */
.login-form {
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 300px;
}

.login-input {
  padding: 10px 12px;
  margin-bottom: 16px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
}

.login-button {
  padding: 10px;
  background-color: #000;
  /* ✅ 改为黑色 */
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  cursor: pointer;
  transition: 0.2s;
}

.login-button:hover {
  opacity: 0.9;
}

.login-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #333;
}
</style>