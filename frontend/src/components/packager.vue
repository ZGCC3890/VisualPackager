<template>
    <!-- 顶部工具栏，左侧是“添加货物”按钮 -->
    <div class="toolbar">
      <button class="add-freight-btn" @click="addItem">
        <img class="add-icon" src="/icons/addFreight.png" alt="添加货物" />
        添加货物
      </button>
    </div>
    <div class="freight-container">

    <!-- 货物列表 -->
    <div class="freight-list">
      <div
        v-for="(item, index) in freightList"
        :key="index"
        class="freight-item"
      >
        <div class="freight-field">
          <label>货物{{ index + 1 }}</label>
          <input type="text" v-model="item.productName" />
        </div>
        <div class="freight-field">
          <label>长</label>
          <input type="number" v-model="item.length" min="1" />
          <span>cm</span>
        </div>
        <div class="freight-field">
          <label>宽</label>
          <input type="number" v-model="item.width" min="1" />
          <span>cm</span>
        </div>
        <div class="freight-field">
          <label>高</label>
          <input type="number" v-model="item.height" min="1" />
          <span>cm</span>
        </div>
        <div class="freight-field">
          <label>重量</label>
          <input type="number" v-model="item.weight" min="1" />
          <span>kg</span>
        </div>

        <img
          class="delete-icon"
          src="/icons/delFreight.png"
          alt="删除"
          @click="deleteItem(index)"
        />
      </div>
    </div>

    <!-- 容器底部右下角的保存按钮，与列表右侧对齐 -->
    <button class="save-button" @click="handleSaveFreight">
      保存货物信息
    </button>
  </div>
</template>

<script setup>
  import { saveFreight } from '../api/packager'
  import { ref, onMounted } from 'vue'

  // 随机背景图片
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
  // 新增的货物信息列表
  const freightList = ref([])

  // 点击空白处的“+”图标，添加一条新的货物信息
  function addItem() {
    const nextIndex = freightList.value.length + 1
    freightList.value.push({
      productName: `货物${nextIndex}`,
      length: 0,
      width: 0,
      height: 0,
      weight: 0
    })
  }

  // 删除条目信息
  function deleteItem(index) {
    freightList.value.splice(index, 1)
  }

  // 保存货物信息到后端
  async function handleSaveFreight() {
  try {
    const storedUsername = localStorage.getItem('username') || ''
    const resp = await saveFreight(storedUsername, freightList.value)

    // 例如后端返回 { success: true, message: '货物信息已保存' }
    alert(resp.message || '货物信息已成功保存！')
  } catch (error) {
    console.error('保存货物信息出错:', error)
    alert('保存失败，请稍后重试。')
  }
}
</script>

<style scoped>
.toolbar {
  width: 900px;
  margin: 50px auto 0; /* 居中并留出上方空间 */
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  padding: 20px;
  position: relative;
  display: flex;
  justify-content: flex-start;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* 添加货物按钮 */
.add-freight-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  background-color: rgba(255, 255, 255, 0.5);
  color: black;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.add-freight-btn:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
}

.add-icon {
  width: 24px;
  height: 24px;
  margin-right: 8px;
}

.freight-container {
  width: 900px; 
  min-height: 300px;
  margin: 50px auto 0;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  position: relative;
  padding: 20px;
  padding-bottom: 80px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.freight-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 200px;
}

/* 货物条目 */
.freight-item {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 30px;
  background-color: transparent;
  border-radius: 6px;
  padding: 10px;
  font-size: 18px;
}

/* 货物字段 */
.freight-field {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 输入框 */
.freight-field input {
  width: 60px;
  height: 30px;
  text-align: center;
  padding: 2px 4px;
  font-size: 16px;
}

/* 删除图标 */
.delete-icon {
  width: 24px;
  height: 24px;
  cursor: pointer;
  margin-left: auto;
  margin-right: 10px;
}

/* 保存按钮 */
.save-button {
  position: absolute;
  bottom: 20px;
  right: 20px;
  padding: 10px 20px;
  background-color: black;
  color: #fff;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 16px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
}
.save-button:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
}

/* 去掉数字输入框右侧箭头 */
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>
