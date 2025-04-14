<template>
    <!-- 侧栏主体：使用 .sidebar-slide 动画控制展开 / 收起 -->
    <transition name="sidebar-slide">
        <aside v-show="visible" class="sidebar">
            <!-- 折叠按钮：左上角图标 -->
            <img src="/icons/sidebar.png" class="toggle-btn" @click="visible = false" />

            <!-- 用户名 -->
            <div class="user-box">{{ username }}</div>

            <!-- 新建方案按钮 -->
            <button class="side-btn" @click="createPlan">
                <img src="/icons/addFreight.png" class="icon" />
                新建方案
            </button>

            <!-- 历史方案列表 -->
            <ul class="plan-list">
                <li v-for="p in plans" :key="p.id" class="side-btn" @click="loadPlan(p.id)">
                    <!-- 标题或编辑框 -->
                    <template v-if="editingId !== p.id">
                        <span @click="loadPlan(p.id)">{{ p.title }}</span>
                    </template>
                    <template v-else>
                        <input v-model="editText" @keyup.enter="saveRename(p)" @blur="saveRename(p)"
                            class="edit-input" />
                    </template>

                    <!-- 三点菜单 -->
                    <span class="dots" @mouseenter="hoverDots = p.id" @mouseleave="hoverDots = null"
                        @click.stop="openMenu(p.id, $event)">
                        {{ hoverDots === p.id ? '•••' : '···' }}
                    </span>
                </li>
            </ul>
            <ul v-if="menuVisible" class="pop-menu" :style="menuStyle">
                <li @click="startRename">重命名</li>
                <li @click="deleteFunction">删除</li>
            </ul>
        </aside>
    </transition>

    <!-- 展开按钮（侧栏隐藏时显示） -->
    <transition name="sidebar-slide">
        <img v-if="!visible" src="/icons/sidebar.png" class="expand-btn" @click="visible = true" />
    </transition>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchPlans, fetchPlanById, renamePlan, deletePlan } from '../api/packager'

const emit = defineEmits(['planLoaded'])
const username = localStorage.getItem('username') || '未登录'
const visible = ref(true)
const plans = ref([])

/** 加载历史方案列表 */
async function refresh() {
    plans.value = await fetchPlans(username)
}

/** 点击方案标题，加载该方案 */
async function loadPlan(id) {
    const data = await fetchPlanById(id)
    emit('planLoaded', data) // 抛给父组件
}

/* ★ 新建空白方案：向父组件发出空数据 */
function createPlan() {
    emit('planLoaded', {
        success      : true,
        destination: '',      // 发货地清空
        freight_data: [],      // 货物列表为空
        plan: null     // 无装箱方案
    })
}
onMounted(refresh)

const editingId = ref(null)   // 正在重命名的 id
const editText = ref('')
const hoverDots = ref(null)   // 悬浮高亮
const menuVisible = ref(false)
const menuStyle = ref({})     // 弹出菜单定位
let currentId = null        // 当前操作的方案 id

function openMenu(id, evt) {
    menuVisible.value = false
    currentId = id
    menuVisible.value = true
    menuStyle.value = { left: `${evt.clientX}px`, top: `${evt.clientY}px` }
}

function startRename() {
    menuVisible.value = false
    editingId.value = currentId
    const plan = plans.value.find(p => p.id === currentId)
    editText.value = plan.title
}

async function saveRename(plan) {
    const txt = editText.value.trim()
    const newTitle = txt || (new Date().toLocaleString() + ' · 新方案')
    const res = await renamePlan(plan.id, newTitle)
    if (res.success) plan.title = res.title
    editingId.value = null
}

async function deleteFunction() {
    const ok = await deletePlan(currentId)
    if (ok.success) plans.value = plans.value.filter(p => p.id !== currentId)
    menuVisible.value = false
}

/* 点击空白关闭菜单 */
window.addEventListener('click', () => { menuVisible.value = false })

</script>

<style scoped>
/* ========== 动画 ========== */
.sidebar-slide-enter-active,
.sidebar-slide-leave-active {
    transition: transform 0.3s;
}

.sidebar-slide-enter-from,
.sidebar-slide-leave-to {
    transform: translateX(-100%);
}

/* ========== 侧栏主体 ========== */
.sidebar {
    width: 260px;
    height: 100vh;
    background: #f5f5f5;
    /* 灰色与按钮一致 */
    border-right: 1px solid #ddd;
    position: fixed;
    left: 0;
    top: 0;
    z-index: 50;
    display: flex;
    flex-direction: column;
    padding-top: 46px;
    /* 预留给 toggle-btn */
}

/* ========== 折叠/展开图标 ========== */
.toggle-btn,
.expand-btn {
    position: fixed;
    top: 12px;
    /* 两者都 12px，保证同一高度 */
    left: 12px;
    width: 28px;
    height: 28px;
    cursor: pointer;
    z-index: 60;
}

.toggle-btn:hover,
.expand-btn:hover {
    background: #e0e0e0;
    border-radius: 4px;
}

/* ========== 用户名 ========== */
.user-box {
    font-weight: 700;
    padding: 12px 16px;
    margin-bottom: 6px;
    text-align: left;
}

/* ========== 通用按钮 (含新建方案 & 历史方案) ========== */
.side-btn {
    margin: 6px 12px;
    padding: 10px 14px;
    background: #f5f5f5;
    /* 与sidebar颜色相同 */
    border: none;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    text-align: left;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.side-btn:hover {
    background: #e0e0e0;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

/* ========== 图标 ========== */
.icon {
    width: 18px;
    height: 18px;
}

/* ========== 历史方案列表 ========== */
.plan-list {
    flex: 1;
    overflow: auto;
    list-style: none;
    padding: 0;
    margin: 0;
}

.plan-list li {
    font-size: 14px;
}

/* 滚动条可选自定义 */
.plan-list::-webkit-scrollbar {
    width: 6px;
}

.plan-list::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 3px;
}

/* 三点图标 */
.dots {
    margin-left: auto;
    cursor: pointer;
    font-weight: 600;
    user-select: none;
}

.dots:hover {
    font-weight: 900;
}

/* 编辑框 */
.edit-input {
    flex: 1;
    border: 1px solid #bbb;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 14px;
}

/* 弹出菜单 */
.pop-menu {
    position: fixed;
    background: #ffffff;
    border: 1px solid #ccc;
    border-radius: 6px;
    list-style: none;
    padding: 4px 0;
    margin: 0;
    z-index: 999;
    width: 100px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, .15);
}

.pop-menu li {
    padding: 6px 12px;
    cursor: pointer;
}

.pop-menu li:hover {
    background: #e0e0e0;
}
</style>