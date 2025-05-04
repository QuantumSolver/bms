<script setup>
defineProps({
  selectedEvent: Object
});

defineEmits(['selectRace', 'goBack']);
</script>

<template>
  <div class="section" v-animate:slide-up>
    <div class="section-header">
      <button class="btn btn-sm btn-back" @click="$emit('goBack')">
        ‹ Back to Events
      </button>
      <h4>Races in {{ selectedEvent.venue }}</h4>
      <div class="event-meta">
        <span>{{ selectedEvent.meet_date }}</span>
        <span>•</span>
        <span>{{ selectedEvent.organizer }}</span>
      </div>
    </div>
    
    <div v-if="!selectedEvent.races || selectedEvent.races.length === 0" class="empty-state">
      No races scheduled for this event
    </div>
    
    <div class="race-list">
      <div 
        v-for="race in selectedEvent.races" 
        :key="race.name"
        class="race-card"
        @click="$emit('selectRace', race)"
      >
        <div class="race-time">{{ race.race_time }}</div>
        <div class="race-name">{{ race.race_name }}</div>
        <div class="race-distance">{{ race.distance }}m</div>
        <div class="race-status" :class="race.status.toLowerCase()">{{ race.status }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.event-meta {
  display: flex;
  gap: 10px;
  font-size: 0.9em;
  color: #666;
  margin-top: 5px;
}

.race-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.race-card {
  padding: 15px;
  background: white;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: all 0.2s;
}

.race-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.race-time {
  font-weight: bold;
  color: #5e64ff;
  margin-bottom: 5px;
}

.race-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.race-distance {
  font-size: 0.9em;
  color: #666;
}

.race-status {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin-top: 5px;
}

.race-status.scheduled {
  background: #e3f2fd;
  color: #1976d2;
}

.race-status.completed {
  background: #e8f5e9;
  color: #388e3c;
}

.race-status.cancelled {
  background: #ffebee;
  color: #d32f2f;
}
</style>