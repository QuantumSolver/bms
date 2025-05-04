<script setup>
defineProps({
  selectedStable: Object,
  selectedEvent: Object,
  selectedRace: Object
});

defineEmits(['goToStables', 'goToEvents', 'goToRaces']);
</script>

<template>
  <div class="breadcrumbs">
    <span 
      class="breadcrumb-item" 
      :class="{ active: !selectedStable }"
      @click="$emit('goToStables')"
    >
      Stables
    </span>
    
    <span class="separator" v-if="selectedStable">›</span>
    
    <span 
      class="breadcrumb-item" 
      :class="{ active: selectedStable && !selectedEvent }"
      @click="$emit('goToEvents')"
      v-if="selectedStable"
    >
      {{ selectedStable.stable_name }}
    </span>
    
    <span class="separator" v-if="selectedEvent">›</span>
    
    <span 
      class="breadcrumb-item" 
      :class="{ active: selectedEvent && !selectedRace }"
      @click="$emit('goToRaces')"
      v-if="selectedEvent"
    >
      {{ selectedEvent.venue }}
    </span>
    
    <span class="separator" v-if="selectedRace">›</span>
    
    <span 
      class="breadcrumb-item" 
      :class="{ active: selectedRace }"
      v-if="selectedRace"
    >
      {{ selectedRace.race_name }}
    </span>
  </div>
</template>

<style scoped>
.breadcrumbs {
  display: flex;
  align-items: center;
  padding: 10px 0;
  margin-bottom: 20px;
  font-size: 14px;
  color: #666;
  flex-wrap: wrap;
}

.breadcrumb-item {
  cursor: pointer;
  padding: 5px 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.breadcrumb-item:hover {
  background-color: #f0f2ff;
  color: #5e64ff;
}

.breadcrumb-item.active {
  font-weight: bold;
  color: #333;
  background-color: transparent;
  cursor: default;
}

.separator {
  margin: 0 5px;
  color: #999;
}
</style>