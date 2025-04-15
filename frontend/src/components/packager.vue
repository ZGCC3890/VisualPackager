<template>

  <!-- 提示 -->
  <div v-if="showPlanToast" class="plan-toast">{{ planToastMsg }}</div>
  <div v-if="showLoginToast" class="login-toast">{{ loginToastMsg }}</div>
  <div v-if="showFreightToast" class="freight-toast">{{ freightToastMsg }}</div>
  <!-- 侧边栏 -->
  <PlanSidebar @planLoaded="handlePlanLoaded" @sidebarVisible="sidebarVisible = $event" />
  <div :class="['main-wrapper', { 'with-sidebar': sidebarVisible }]">
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
        <p>2. 单箱重量限制：{{ constraints[selectedLocation].weightText }}</p>
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

          <img v-if="freightWarnings[index]?.overweight" class="warning-icon" src="/icons/warning.png" alt="警告" />

          <img class="delete-icon" src="/icons/delFreight.png" alt="删除" @click="deleteItem(index)" />
        </div>
      </div>

      <!-- 生成装箱方案按钮 -->
      <button class="plan-button" @click="handleGeneratePlan">
        生成装箱方案
      </button>
      <!-- 保存按钮，与列表右侧对齐 -->
      <button class="save-button" @click="handleSaveFreight">
        保存货物信息
      </button>
    </div>
    <Packing3D v-if="packingPlan" :plan="packingPlan" />
  </div>
</template>

<script setup>
import { saveFreight } from '../api/packager'
import { generatePackingPlan } from '../api/packager'
import { ref, onMounted, computed } from 'vue'
import Packing3D from './packing3D.vue'
import PlanSidebar from './sidebar.vue'

/* 侧栏可见状态 */
const sidebarVisible = ref(true)
/* ----- 侧边栏 ----- */
async function handlePlanLoaded(payload) {
  if (!payload.success) return
  selectedLocation.value = payload.destination
  freightList.value = payload.freight_data.map((f, i) => ({
    productName: `货物${i + 1}`,
    length: f.length, width: f.width, height: f.height, weight: f.weight
  }))
  packingPlan.value = payload.plan           // 可能为 null
}

/* ----- 发货地点选择器 ----- */
const selectedLocation = ref('')           // 当前选中的地点

// 各地点对应的限制
const constraints = {
  澳洲: { size: '单边长 ≤ 63cm', weightText: '≤ 22kg', length: 63, width: 63, height: 63, weight: 22 },
  美国: { size: '单边长 ≤ 63cm', weightText: '≤ 22kg', length: 63, width: 63, height: 63, weight: 22 },
  英国: { size: '单边长 ≤ 63cm', weightText: '≤ 15kg', length: 63, width: 63, height: 63, weight: 15 },
  德国: { size: '单边长 ≤ 63cm', weightText: '≤ 22.5kg', length: 63, width: 63, height: 63, weight: 22.5 },
  日本: { size: '长 ≤ 60cm, 宽 ≤ 50cm, 高 ≤ 50cm', weightText: '≤ 40kg', length: 60, width: 50, height: 50, weight: 40 }
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
  const wrapper = document.querySelector('.main-wrapper')
  console.log("Selected background:", selectedImage)
  if (wrapper) {
    wrapper.style.backgroundImage = `url(${selectedImage})`
    wrapper.style.backgroundSize = 'cover'
    wrapper.style.backgroundRepeat = 'no-repeat'
    wrapper.style.backgroundPosition = 'center'
  }
})

/* ----- 登录成功提示 ----- */
const showLoginToast = ref(false)
const loginToastMsg = ref('登录成功，欢迎回来！')
onMounted(() => {
  if (localStorage.getItem('showLoginToast') === 'true') {
    showLoginToast.value = true
    localStorage.removeItem('showLoginToast')
    setTimeout(() => {
      showLoginToast.value = false
    }, 3000)
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
const showFreightToast = ref(false)
const freightToastMsg = ref('')
async function handleSaveFreight() {
  try {
    const storedUsername = localStorage.getItem('username') || ''
    const destination = selectedLocation.value            // ★ 当前发货地
    const payload = {
      username: storedUsername,
      destination: destination,
      freight_data: freightList.value,
      plan: packingPlan.value || null    // ★ 追加方案（若已生成）
    }
    const resp = await saveFreight(payload)

    // 例如后端返回 { success: true, message: '货物信息已保存' }
    if (resp.success) {
      freightToastMsg.value = '货物信息已保存'
      showFreightToast.value = true
      setTimeout(() => (showFreightToast.value = false), 3000)
    } else {
      alert(resp.message || '保存失败，请稍后重试。')
    }
  } catch (error) {
    console.error('保存货物信息出错:', error)
    alert('保存失败，请稍后重试。')
  }
}

/* ----- 错误信息提示 ----- */
const freightWarnings = computed(() => {
  const location = selectedLocation.value
  const std = stdMap[location] || {}
  const rule = constraints[location] || {}

  const stdSize = std.size || {}
  const maxGrossWeight = rule.weight || Infinity  // 外包箱最大承重

  // 计算最小外包箱重量（基于标准件尺寸）
  const WALL_THICKNESS = 0.6 // cm
  const MATERIAL_DENSITY = 0.54 // kg/m²
  const calcShellWeight = (L, W, H) => {
    const area = 2 * (L * W + L * H + W * H) / 10000 // cm²转m²
    return area * MATERIAL_DENSITY
  }

  // 最小外包箱尺寸（标准件尺寸+两侧壁厚）
  const minOuterLength = (stdSize.length || 0) + 2 * WALL_THICKNESS
  const minOuterWidth = (stdSize.width || 0) + 2 * WALL_THICKNESS
  const minOuterHeight = (stdSize.height || 0) + 2 * WALL_THICKNESS

  // 最小外包箱重量
  const minShellWeight = calcShellWeight(minOuterLength, minOuterWidth, minOuterHeight)

  // 标准件自重（如果有）
  const stdWeight = std.weight || 0

  // 实际允许的最大货物重量 = 最大总承重 - 标准件自重 - 最小外包箱重量
  const maxItemWeight = maxGrossWeight - stdWeight - minShellWeight

  // 如果缺失标准件或限制，则不报警告
  if (!stdSize.length || !stdSize.width || !stdSize.height || !maxItemWeight) {
    return freightList.value.map(() => ({
      overweight: false,
      oversize: false
    }))
  }

  return freightList.value.map(item => {
    const oversize =
      item.length > stdSize.length ||
      item.width > stdSize.width ||
      item.height > stdSize.height

    const overweight = item.weight > maxItemWeight

    return {
      overweight,
      oversize
    }
  })
})

const packingPlan = ref(null)
const showPlanToast = ref(false)
const planToastMsg = ref('')
/* 装箱方案生成 */
async function handleGeneratePlan() {
  try {
    const hasWarnings = freightWarnings.value.some(w => w.oversize || w.overweight)
    if (hasWarnings) {
      alert('存在超重或超尺寸的货物条目，请检查并修改后再生成装箱方案。')
      return
    }
    if (!selectedLocation.value) {
      alert('请选择发货地点')
      return
    }

    const { code, size, weight } = stdMap[selectedLocation.value]
    const std = { code, ...size, weight }
    const outerLimit = {
      maxLength: constraints[selectedLocation.value].length,
      maxWidth: constraints[selectedLocation.value].width,
      maxHeight: constraints[selectedLocation.value].height,
      maxWeight: constraints[selectedLocation.value].weight
    }

    const resp = await generatePackingPlan(freightList.value, std, outerLimit)

    if (resp.success) {
      console.log('装箱成功：', resp.plan)
      packingPlan.value = resp.plan
      planToastMsg.value = '装箱方案已生成，请查看3D视图'
      showPlanToast.value = true
      setTimeout(() => (showPlanToast.value = false), 3000)
    } else {
      alert(resp.message || '装箱失败')
    }
  } catch (err) {
    console.error('装箱异常', err)
    alert('网络异常或服务器错误')
  }
}

</script>