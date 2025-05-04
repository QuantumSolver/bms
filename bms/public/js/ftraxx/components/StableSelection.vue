<script setup>
defineProps({
  stables: Array
});

defineEmits(['selectStable']);
</script>

<template>
  <div class="section" v-animate:slide-up>
    <h4>Your Stables</h4>
    <div v-if="stables.length === 0" class="empty-state">
      No stables found for your account
    </div>
    <div class="stable-list">
      <div 
        v-for="stable in stables" 
        :key="stable.name"
        class="stable-card"
        @click="$emit('selectStable', stable)"
      >
        <div class="stable-name">{{ stable.stable_name }}</div>
        <div class="stable-horses">{{ stable.total_horses || 0 }} horses</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.section {
  margin-bottom: 30px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 5px;
}

.empty-state {
  padding: 20px;
  text-align: center;
  color: #6c757d;
  background: white;
  border-radius: 5px;
  margin-top: 15px;
}

.stable-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.stable-card {
  padding: 15px;
  background: white;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: all 0.2s;
}

.stable-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.stable-name {
  font-weight: bold;
  margin-bottom: 5px;
  color: #333;
}

.stable-horses {
  font-size: 0.8em;
  color: #5e64ff;
  margin-top: 5px;
}
</style>