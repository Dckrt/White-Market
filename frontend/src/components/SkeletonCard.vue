<template>
  <div class="skeleton-wrapper">
    <!-- Category & Status Header -->
    <div class="skeleton-header">
      <div class="skeleton-box small-tag"></div>
      <div class="skeleton-box status-tag"></div>
    </div>

    <!-- Title & Description -->
    <div class="skeleton-box title"></div>
    <div class="skeleton-box description"></div>
    <div class="skeleton-box description short"></div>

    <!-- Footer with Price and Button -->
    <div class="skeleton-footer">
      <div class="skeleton-box price"></div>
      <div class="skeleton-box button"></div>
    </div>
  </div>
</template>

<style scoped>
.skeleton-wrapper {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 1.2rem;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Shimmer Animation Effect */
.skeleton-box {
  background: #eee;
  background: linear-gradient(110deg, #ececec 8%, #f5f5f5 18%, #ececec 33%);
  border-radius: 4px;
  background-size: 200% 100%;
  animation: shimmer 1.5s linear infinite;
}

@keyframes shimmer {
  to { background-position-x: -200%; }
}

.skeleton-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.small-tag { width: 60px; height: 20px; }
.status-tag { width: 80px; height: 20px; border-radius: 12px; }

.title { height: 24px; width: 80%; margin-bottom: 1rem; }

.description { height: 14px; width: 100%; margin-bottom: 8px; }
.description.short { width: 60%; margin-bottom: 2rem; }

.skeleton-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid #f0f0f0;
}

.price { width: 70px; height: 22px; }
.button { width: 100px; height: 32px; border-radius: 6px; }
</style>
