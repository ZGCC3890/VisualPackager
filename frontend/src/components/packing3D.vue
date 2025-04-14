<template>
    <div class="packing3d-container">
        <!-- 外包箱翻页 -->
        <div class="packing-controls">
            <button @click="prevBox" :disabled="currentIndex === 0">上一箱</button>
            <span>外包箱 {{ currentIndex + 1 }} / {{ totalBoxes }}</span>
            <button @click="nextBox" :disabled="currentIndex === totalBoxes - 1">下一箱</button>
        </div>

        <!-- 标准件选单 -->
        <div class="std-controls" v-if="stdList.length">
            <strong>标准件：</strong>
            <span v-for="(id, i) in stdList" :key="id" class="std-name" :class="{ active: id === selectedStd }"
                @click="toggleStd(id)">
                标准件{{ i + 1 }}
            </span>
            <span v-if="selectedStd" class="reset-btn" @click="resetStd">取消筛选</span>
        </div>

        <!-- 货物标签 -->
        <div class="packing-summary">
            <strong>货物列表：</strong>
            <span v-for="name in currentCargoList" :key="name" class="cargo-name"
                :class="{ disabled: isDisabled(name), active: persistentSet.has(name) }" @mouseenter="!isDisabled(name) && hoverCargo(name, true)"
                @mouseleave="!isDisabled(name) && hoverCargo(name, false)"
                @click="!isDisabled(name) && togglePersistentHighlight(name)">
                {{ name }}
            </span>
        </div>
        <div class="align-left label"></div>
        <canvas ref="canvasRef" class="packing-canvas" tabindex="0" style="outline: none"></canvas>
    </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'

/* ---------- props ---------- */
const props = defineProps({ plan: Object })

/* ---------- reactive refs ---------- */
const canvasRef = ref(null)
const currentIndex = ref(0)
const currentCargoList = ref([])
const persistentSet = ref(new Set())  // 黄色保持集合
const selectedStd = ref(null)       // 筛选的标准件 id
const stdList = ref([])         // 当前箱的所有标准件 id

/* ---------- three.js globals ---------- */
let scene, camera, renderer, controls
let meshMap = {}   // { cargoName: Mesh[] }
let stdMeshMap = {}   // { stdId: [stdMesh, ...cargoMeshes] }

/* ---------- computed ---------- */
const totalBoxes = computed(() => props.plan?.outer_boxes?.length || 0)

/* ---------- util ---------- */
const BASE_COLOR = 0x00cccc  // ★浅蓝
function drawBox(x, y, z, l, w, h, colorHex, opacity = 0.7, isCargo = false) {
    const geo = new THREE.BoxGeometry(l, h, w)
    const mat = new THREE.MeshLambertMaterial({
        color: colorHex,
        transparent: true,
        opacity
    })
    if (isCargo) {                           // ★ 只有货物才自带弱青光
        mat.emissive.setHex(0x00ccff)
        mat.emissiveIntensity = 0.25
    }
    const mesh = new THREE.Mesh(geo, mat)
    mesh.position.set(x + l / 2, z + h / 2, y + w / 2)
    scene.add(mesh)

    // 轮廓
    const edges = new THREE.EdgesGeometry(geo)
    const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x000000 }))
    line.position.copy(mesh.position)
    scene.add(line)
    return mesh
}

function addLabel(text) {
    // 若已存在就直接更新文字
    let dom = document.getElementById('scene-label')
    if (!dom) {
        dom = document.createElement('div')
        dom.id = 'scene-label'
        dom.className = 'scene-label'
        document.querySelector('.label')?.appendChild(dom)
    }
    dom.textContent = text
}

/* ---------- build scene ---------- */
function buildScene() {
    scene = new THREE.Scene()
    scene.background = new THREE.Color(0xfafafa)

    const w = canvasRef.value.clientWidth
    const h = canvasRef.value.clientHeight
    camera = new THREE.PerspectiveCamera(70, w / h, 1, 1000)
    camera.position.set(100, 80, 100)

    renderer = new THREE.WebGLRenderer({ canvas: canvasRef.value, antialias: true })
    renderer.setSize(w, h)

    controls = new OrbitControls(camera, renderer.domElement)
    controls.enablePan = true
    controls.listenToKeyEvents(canvasRef.value)
    // 设置平移速度和键位
    controls.keyPanSpeed = 50
    controls.keys = {
        LEFT: 'KeyA',   // A
        UP: 'KeyW',   // W
        RIGHT: 'KeyD',   // D
        BOTTOM: 'KeyS'    // S
    }

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.2)
    dirLight.position.set(100, 120, 80)
    scene.add(dirLight)

    const animate = () => { requestAnimationFrame(animate); controls.update(); renderer.render(scene, camera) }
    animate()
}

/* ---------- rendering helpers ---------- */
function clearScene() {
    meshMap = {}; stdMeshMap = {}
    while (scene.children.length) scene.remove(scene.children[0])
}

function renderCurrentBox() {
    clearScene()
    const box = props.plan?.outer_boxes?.[currentIndex.value]
    if (!box) return

    /* 外包箱极淡白 */
    const bd = box.dimensions
    const gross = box.gross_weight?.toFixed(2) || ''
    drawBox(0, 0, 0, bd.length, bd.width, bd.height, 0xffffff, 0.05, false)
    const volume = (bd.length * bd.width * bd.height / 1000000).toFixed(2)
    addLabel(`长: ${bd.length} cm   宽: ${bd.width} cm   高: ${bd.height} cm   重量: ${gross} kg   体积: ${volume} m³`)

    stdList.value = []
    const cargoNames = new Set()

    box.contents.forEach((std, idx) => {
        const stdId = `std-${idx}`; stdList.value.push(stdId)
        const p = std.position || { x: 0, y: 0, z: 0 }
        const d = std.dimensions
        const stdMesh = drawBox(p.x, p.y, p.z, d.length, d.width, d.height, 0x999999, 0.2, false)
        stdMeshMap[stdId] = [stdMesh]

        std.contents.forEach(cargo => {
            const pos = cargo.position
            const dim = cargo.dimensions
            const mesh = drawBox(
                p.x + pos.x, p.y + pos.y, p.z + pos.z,
                dim.length, dim.width, dim.height,
                BASE_COLOR, 0.7, true
            )
            if (!meshMap[cargo.item]) meshMap[cargo.item] = []
            meshMap[cargo.item].push(mesh)
            stdMeshMap[stdId].push(mesh)
            cargoNames.add(cargo.item)
        })
    })

    currentCargoList.value = Array.from(cargoNames)
    applyStdFilter()
    restorePersistentColors()
}

/* ---------- 标准件过滤 ---------- */
function toggleStd(id) { selectedStd.value = selectedStd.value === id ? null : id; applyStdFilter() }
function resetStd() { selectedStd.value = null; applyStdFilter() }
function applyStdFilter() {
    Object.entries(stdMeshMap).forEach(([id, meshes]) => {
        const show = !selectedStd.value || id === selectedStd.value
        meshes.forEach((m, idx) => {
            m.visible = show
            m.material.opacity = show ? (idx === 0 ? 0.2 : 0.7) : 0.05
        })
    })
}

/* ---------- 高亮逻辑 ---------- */
function setEmissive(meshes, hex) { meshes.forEach(m => m.material.emissive.setHex(hex)) }

function hoverCargo(name, enter) {
    const meshes = meshMap[name] || []
    if (enter) {
        meshes.forEach(m => m.material.emissive.setHex(0xff0000))   // 悬浮红
    } else {
        const keep = persistentSet.value.has(name)
        meshes.forEach(m => {
            m.material.emissive.setHex(keep ? 0xffff00 : 0x00ccff)   // ★ 货物本体颜色（弱青光）
            if (!keep) {
                // ★ 恢复本体颜色（浅蓝）
                m.material.color.setHex(BASE_COLOR)
            }
        })
    }
}

function togglePersistentHighlight(name) {
    if (persistentSet.value.has(name)) {
        persistentSet.value.delete(name)
        setEmissive(meshMap[name], 0x00cccc)
    } else {
        persistentSet.value.add(name)
        setEmissive(meshMap[name], 0xffff00)
    }
}

function restorePersistentColors() {
    // 重渲染后把持久高亮恢复为黄色
    persistentSet.value.forEach(name => setEmissive(meshMap[name] || [], 0xffff00))
}

function isDisabled(name) {
    if (!selectedStd.value) return false
    return !stdMeshMap[selectedStd.value].slice(1).some(m => meshMap[name]?.includes(m))
}

/* ---------- 翻页 ---------- */
function nextBox() { if (currentIndex.value < totalBoxes.value - 1) { currentIndex.value++; renderCurrentBox() } }
function prevBox() { if (currentIndex.value > 0) { currentIndex.value--; renderCurrentBox() } }

/* ---------- lifecycle ---------- */
onMounted(() => { buildScene(); renderCurrentBox() })
watch(() => props.plan, () => { currentIndex.value = 0; persistentSet.value.clear(); renderCurrentBox() })
</script>

<style scoped>
.packing3d-container {
    width: 100%;
    max-width: 1000px;
    margin: 24px auto 0;
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, .12);
    position: relative;
    padding: 16px;
    display: flex;
    flex-direction: column;
    /* 纵向堆叠子元素 */
    gap: 16px;
    /* 子元素之间垂直间距 */
    align-items: center;
    /* 默认让子元素水平居中 */
}

.packing-canvas {
    width: 100%;
    height: 500px;
    display: block;
}

.packing-controls,
.std-controls {
    margin: 10px 0;
    display: flex;
    gap: 12px;
    justify-content: center;
    align-items: center;
}

.std-name {
    cursor: pointer;
    padding: 2px 10px;
    border-radius: 4px;
    background: #e0e0e0;
}

.std-name.active {
    background: #2196f3;
    color: #fff;
}

.reset-btn {
    cursor: pointer;
    margin-left: 14px;
    padding: 2px 10px;
    border-radius: 4px;
    background: #e53935;
    color: #fff;
}

.packing-summary {
    margin-bottom: 10px;
    text-align: center;
}

.cargo-name {
    margin: 0 6px;
    padding: 2px 8px;
    border-radius: 4px;
    background: #e0e0e0;
    cursor: pointer;
}

.cargo-name.disabled {
    opacity: .25;
    pointer-events: none;
}
.cargo-name.active {
    background: #2196f3;   /* 和 .std-name.active 同色 */
    color: #fff;
}


.align-left {
    align-self: flex-start;
}

.scene-label {
    padding: 4px 10px;
    background: rgba(255, 255, 255, .85);
    border-radius: 4px;
    font-size: 14px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, .2);
    pointer-events: none;
    white-space: nowrap;
}
</style>