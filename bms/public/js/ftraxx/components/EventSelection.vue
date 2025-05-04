<script setup>
defineProps({
  upcomingEvents: Array
});

defineEmits(['selectEvent', 'goBack']);
</script>

<template>
    
  <div class="section" v-animate:slide-up>
<div class="section-header">
      <!-- <button class="btn btn-sm btn-back" @click="$emit('goBack')">
        ‹ Back to Events
      </button> -->
      <h4>Upcoming Events</h4>
    </div>
    
    <div v-if="upcomingEvents.length === 0" class="empty-state">
      No upcoming events found
    </div>
    
    <div class="event-list">
      <div 
        v-for="event in upcomingEvents" 
        :key="event.name"
        class="event-card"
        @click="$emit('selectEvent', event)"
      >
        <div class="event-date">{{ event.meet_date }}</div>
        <div class="event-name">{{ event.venue }}</div>
        <div class="event-organizer">{{ event.organizer }}</div>
        <div class="event-status" :class="event.status.toLowerCase()">{{ event.status }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* .section-header {
  position: relative;
} */
/* 
.btn-back {
  position: absolute;
  left: 0;
  top: 0;
  background: none;
  border: none;
  color: #5e64ff;
  cursor: pointer;
}

.btn-back:hover {
  text-decoration: underline;
} */

.event-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.event-card {
  padding: 15px;
  background: white;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: all 0.2s;
}

.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.event-date {
  font-weight: bold;
  color: #5e64ff;
  margin-bottom: 5px;
}

.event-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.event-organizer {
  font-size: 0.9em;
  color: #666;
}

.event-status {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin-top: 5px;
}

.event-status.scheduled {
  background: #e3f2fd;
  color: #1976d2;
}

.event-status.completed {
  background: #e8f5e9;
  color: #388e3c;
}

.event-status.cancelled {
  background: #ffebee;
  color: #d32f2f;
}
</style>