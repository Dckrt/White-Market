<template>
  <div class="rating-container" title="Seller Rating">
    <!-- Star Icons -->
    <div class="stars">
      <span 
        v-for="i in 5" 
        :key="i" 
        class="star" 
        :class="getStarClass(i)"
      >
        ★
      </span>
    </div>
    
    <!-- Numerical Label (Per your Paper's UI Plan) -->
    <span v-if="rating > 0" class="rating-text">
      {{ rating.toFixed(1) }} / 5.0
    </span>
    <span v-else class="rating-text empty">No ratings yet</span>
  </div>
</template>

<script setup>
const props = defineProps({
  rating: { type: Number, default: 0 }
})

// Logic to determine if a star is full, half, or empty
const getStarClass = (i) => {
  if (i <= Math.floor(props.rating)) return 'filled';
  if (i === Math.ceil(props.rating) && props.rating % 1 >= 0.5) return 'half';
  return 'empty';
}
</script>

<style scoped>
.rating-container {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.stars {
  color: #ddd; /* Base color for empty stars */
  display: flex;
  font-size: 1.1rem;
  line-height: 1;
}

.star {
  position: relative;
  transition: transform 0.2s;
}

.star.filled {
  color: #fbbf24; /* Ateneo Gold-ish Yellow */
}

/* Better Half-Star Overlay Technique */
.star.half {
  color: #ddd;
}
.star.half::before {
  content: '★';
  position: absolute;
  left: 0;
  top: 0;
  width: 50%;
  overflow: hidden;
  color: #fbbf24;
}

.rating-text {
  font-size: 0.85rem;
  font-weight: 600;
  color: #555;
}

.rating-text.empty {
  font-weight: normal;
  color: #999;
  font-style: italic;
}
</style>
