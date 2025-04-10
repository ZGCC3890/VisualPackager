<template>
  <!-- 顶部工具栏，左侧是“添加货物”按钮 -->
  <div class="toolbar">
    <button class="add-freight-btn" @click="addItem">
      <img class="add-icon" src="/icons/addFreight.png" alt="添加货物" />
      添加货物
    </button>
    <!-- 发货地点选择器 -->
    <select v-model="selectedLocation" class="location-select">
      <option value="">请选择发货地点</option>
      <option value="澳洲">澳洲</option>
      <option value="美国">美国</option>
      <option value="英国">英国</option>
      <option value="德国">德国</option>
      <option value="日本">日本</option>
    </select>

    <!-- 标准件信息 -->
    <span class="std-label">标准件信息：</span>

    <!-- 按钮 / 卡片互斥渲染 -->
    <template v-if="!showStd">
      <button class="std-btn" @click="toggleStd">{{ stdButtonText }}</button>
    </template>

    <template v-else>
      <div class="std-card" @click="toggleStd">
        <!-- 左蓝块 -->
        <div class="std-header">
          {{ stdButtonText }}
        </div>
        <!-- 右白块 -->
        <div class="std-body">
          <p>长：{{ stdInfo.size.length }} cm</p>
          <p>宽：{{ stdInfo.size.width }} cm</p>
          <p>高：{{ stdInfo.size.height }} cm</p>
          <p>重量：{{ stdInfo.weight }} kg</p>
        </div>
      </div>
    </template>
  </div>

  <div class="freight-container">
    <!-- 显示约束条件 -->
    <div v-if="selectedLocation" class="constraint-box">
      <p>1. 外包箱尺寸限制：{{ constraints[selectedLocation].size }}</p>
      <p>2. 单箱重量限制：{{ constraints[selectedLocation].weight }}</p>
    </div>
    <!-- 货物列表 -->
    <div class="freight-list">
      <div v-for="(item, index) in freightList" :key="index" class="freight-item"
        :class="{ 'warning-item': freightWarnings[index]?.overweight || freightWarnings[index]?.oversize }">
        <div class="freight-field">
          <label>货物{{ index + 1 }}</label>
          <input type="text" v-model="item.productName" />
        </div>
        <div class="freight-field">
          <label>长</label>
          <input type="number" v-model="item.length" min="0"
            :class="{ 'warning-input': freightWarnings[index]?.oversize }" />
          <span>cm</span>
        </div>
        <div class="freight-field">
          <label>宽</label>
          <input type="number" v-model="item.width" min="0"
            :class="{ 'warning-input': freightWarnings[index]?.oversize }" />
          <span>cm</span>
        </div>
        <div class="freight-field">
          <label>高</label>
          <input type="number" v-model="item.height" min="0"
            :class="{ 'warning-input': freightWarnings[index]?.oversize }" />
          <span>cm</span>
        </div>
        <div class="freight-field">
          <label>重量</label>
          <input type="number" v-model="item.weight" min="0"
            :class="{ 'warning-input': freightWarnings[index]?.overweight }" />
          <span>kg</span>
        </div>

        <img v-if="freightWarnings[index]?.overweight" 
          class="warning-icon" 
          src="/icons/warning.png" 
          alt="警告" />

        <img class="delete-icon" 
          src="/icons/delFreight.png" 
          alt="删除" @click="deleteItem(index)" />
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
import { ref, onMounted, computed } from 'vue'

/* ----- 发货地点选择器 ----- */
const selectedLocation = ref('')           // 当前选中的地点

// 各地点对应的限制
const constraints = {
  澳洲: { size: '单边长 ≤ 63cm', weight: '≤ 22kg' },
  美国: { size: '单边长 ≤ 63cm', weight: '≤ 22kg' },
  英国: { size: '单边长 ≤ 63cm', weight: '≤ 15kg' },
  德国: { size: '单边长 ≤ 63cm', weight: '≤ 22.5kg' },
  日本: { size: '长 ≤ 60cm, 宽 ≤ 50cm, 高 ≤ 50cm', weight: '≤ 40kg' }
}

/* ----- 标准件信息显示 ----- */
const showStd = ref(false)           // 控制展开
const stdButtonText = computed(() =>
  selectedLocation.value
    ? `标准件\n (${stdMap[selectedLocation.value].code})`
    : '标准件'
)
const stdMap = {
  澳洲: { code: 'AUN11-ZY0009', size: { length: 30, width: 20, height: 8 }, weight: 0.68 },
  美国: { code: 'USY6-05-0314', size: { length: 49, width: 21, height: 8 }, weight: 6.999 },
  英国: { code: 'UKB8-ZY0009', size: { length: 30, width: 20, height: 8 }, weight: 0.68 },
  德国: { code: 'DEW1-ZB0004', size: { length: 45, width: 29, height: 17 }, weight: 1.5 },
  日本: { code: 'JPY5-GR049', size: { length: 25, width: 25, height: 10 }, weight: 0.82 }
}
const stdInfo = computed(() =>
  selectedLocation.value ? stdMap[selectedLocation.value] : {}
)

function toggleStd() {
  if (!selectedLocation.value) return
  showStd.value = !showStd.value
}

/* ----- 随机背景图片 ----- */
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

/* ----- 登录成功提示 ----- */
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

/* ----- 货物信息列表 ----- */
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
/* ----- 错误信息提示 ----- */
const freightWarnings = computed(() => {
  const location = selectedLocation.value
  const rule = constraints[location] || {}

  if (!rule || !rule.size || !rule.weight) {
    return freightList.value.map(() => ({
      overweight: false,
      oversize: false
    }))
  }

  const maxWeight = parseFloat(rule.weight?.replace(/[^\d.]/g, '')) || Infinity
  let sizeLimit = {
    length: Infinity,
    width: Infinity,
    height: Infinity
  }

  if (rule.size?.includes('单边长')) {
    // 通用单边长限制（如 澳洲等）
    const maxSide = parseFloat(rule.size.replace(/[^\d.]/g, '')) || Infinity
    sizeLimit = { length: maxSide, width: maxSide, height: maxSide }
  } else {
    // 明确给出了每个维度（如 日本）
    const match = rule.size.match(/长\s*≤\s*(\d+)cm.*?宽\s*≤\s*(\d+)cm.*?高\s*≤\s*(\d+)cm/)
    if (match) {
      sizeLimit = {
        length: parseFloat(match[1]),
        width: parseFloat(match[2]),
        height: parseFloat(match[3])
      }
    }
  }

  return freightList.value.map(item => {
    return {
      overweight: item.weight > maxWeight,
      oversize:
        item.length > sizeLimit.length ||
        item.width > sizeLimit.width ||
        item.height > sizeLimit.height
    }
  })
})

</script>