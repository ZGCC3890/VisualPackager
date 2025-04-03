<template>
  
</template>

<script setup>
  import { ref, onMounted } from 'vue'

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
</script>