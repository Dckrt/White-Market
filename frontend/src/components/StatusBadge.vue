<template>
  <div class="badge-wrapper">
    <span :class="['badge', status.toLowerCase()]">
      <span class="dot"></span>
      {{ status }}
    </span>
  </div>
</template>

<script setup>
defineProps(['status']);
</script>

<style scoped>
.badge-wrapper {
  display: inline-block;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border: 1px solid transparent;
}

/* Status: Available (Success) */
.available {
  background-color: #e6fffa;
  color: #234e52;
  border-color: #b2f5ea;
}
.available .dot { background-color: #38a169; }

/* Status: Reserved (Warning) */
.reserved {
  background-color: #fffaf0;
  color: #744210;
  border-color: #fbd38d;
}
.reserved .dot { background-color: #dd6b20; }

/* Status: Sold (Danger) */
.sold {
  background-color: #fff5f5;
  color: #742a2a;
  border-color: #feb2b2;
}
.sold .dot { background-color: #e53e3e; }

/* The small status indicator dot */
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}
</style>
