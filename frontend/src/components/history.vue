<template>

</template>

<script setup>
import { ref, onMounted } from 'vue'

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
</script>