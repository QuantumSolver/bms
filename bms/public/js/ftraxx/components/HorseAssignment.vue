<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  selectedStable: Object,
  selectedRace: Object,
  availableHorses: Array,
  selectedHorses: Array,
  jockeys: Array
});

const emit = defineEmits(['saveAssignments', 'goBack']);

// Local state for temporary assignments before saving
const tempSelectedHorses = ref([]);

// Initialize with any existing selected horses
watch(() => props.selectedHorses, (newVal) => {
  tempSelectedHorses.value = newVal.map(horse => ({
    ...horse,
    // Ensure we have all required fields
    weight_carried: horse.weight_carried || 0,
    draw_number: horse.draw_number || 0,
    trump_card: horse.trump_card || "None",
    is_emergency: horse.is_emergency || false
  }));
}, { immediate: true });

const addHorseToSelection = (horse) => {
  if (!tempSelectedHorses.value.some(h => h.horse === horse.name)) {
    tempSelectedHorses.value.push({
      horse: horse.name,
      horse_name: horse.horse_name,
      jockey: null,
      trump_card: "None",
      is_emergency: false,
      weight_carried: 0,
      draw_number: 0,
      odds: 0,
      rating: 0,
      handicap: "",
      number: tempSelectedHorses.value.length + 1 // Auto-assign number
    });
  }
};

const removeHorseFromSelection = (horse) => {
  tempSelectedHorses.value = tempSelectedHorses.value.filter(h => h.horse !== horse.name);
  // Reassign numbers after removal
  tempSelectedHorses.value.forEach((h, index) => {
    h.number = index + 1;
  });
};

const saveAllAssignments = () => {
  // Validate required fields before saving
  const incompleteAssignments = tempSelectedHorses.value.filter(horse => 
    !horse.jockey || horse.weight_carried <= 0 || horse.draw_number <= 0
  );
  
  if (incompleteAssignments.length > 0) {
    frappe.msgprint({
      title: __('Incomplete Assignments'),
      indicator: 'red',
      message: __('Please complete all required fields (jockey, weight, draw number) for all horses before saving.')
    });
    return;
  }
  
  // Emit the save event with all data
  emit('saveAssignments', {
    race: props.selectedRace.name,
    competitors: tempSelectedHorses.value
  });
};
</script>
<template>
  <div class="section" v-animate:slide-up>
    <div class="section-header">
      <button class="btn btn-sm btn-back" @click="$emit('goBack')">
        ‹ Back to Races
      </button>
      <h4>Assign Horses to {{ selectedRace.race_name }}</h4>
      <div class="race-info">
        <span><strong>Stable:</strong> {{ selectedStable.stable_name }}</span>
        <span><strong>Distance:</strong> {{ selectedRace.distance }}m</span>
        <span><strong>Time:</strong> {{ selectedRace.race_time }}</span>
      </div>
    </div>
    
    <div class="assignment-container">
      <!-- Available Horses -->
      <div class="horse-list available-horses">
        <h5>Available Horses ({{ availableHorses.length }})</h5>
        <div v-if="availableHorses.length === 0" class="empty-state">
          No horses available in this stable
        </div>
        <div v-else class="horse-grid">
          <div 
            v-for="horse in availableHorses" 
            :key="horse.name"
            class="horse-card"
            :class="{ 'selected': tempSelectedHorses.some(h => h.horse === horse.name) }"
            @click="tempSelectedHorses.some(h => h.horse === horse.name) ? removeHorseFromSelection(horse) : addHorseToSelection(horse)"
          >
            <div class="horse-checkbox">
              <input 
                type="checkbox" 
                :checked="tempSelectedHorses.some(h => h.horse === horse.name)"
                @click.stop
                @change="e => e.target.checked ? addHorseToSelection(horse) : removeHorseFromSelection(horse)"
              >
            </div>
            <div class="horse-info">
              <h6>{{ horse.horse_name }}</h6>
              <div class="horse-details">
                <span>{{ horse.breed || '-' }}</span>
                <span>{{ horse.gender }}</span>
                <span :class="'status-' + horse.status.toLowerCase()">{{ horse.status }}</span>
              </div>
            </div>
            <div class="horse-action">
              <button 
                class="btn btn-sm"
                :class="tempSelectedHorses.some(h => h.horse === horse.name) ? 'btn-secondary' : 'btn-primary'"
                @click.stop="tempSelectedHorses.some(h => h.horse === horse.name) ? removeHorseFromSelection(horse) : addHorseToSelection(horse)"
              >
                {{ tempSelectedHorses.some(h => h.horse === horse.name) ? 'Remove' : 'Add' }}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Selected Horses -->
      <div class="horse-list selected-horses">
        <div class="selected-header">
          <h5>Selected Horses ({{ tempSelectedHorses.length }})</h5>
          <button 
            class="btn btn-primary btn-sm"
            @click="saveAllAssignments"
            :disabled="tempSelectedHorses.length === 0"
          >
            Save All
          </button>
        </div>
        <div v-if="tempSelectedHorses.length === 0" class="empty-state">
          No horses selected yet. Click on horses from the left panel to add them.
        </div>
        <div v-else class="selected-grid">
          <div 
            v-for="(horse, index) in tempSelectedHorses" 
            :key="index"
            class="competitor-card"
            :class="{ 'emergency': horse.is_emergency }"
          >
            <div class="competitor-number">
              #{{ horse.number }}
            </div>
            <div class="competitor-main">
              <div class="competitor-name">{{ horse.horse_name }}</div>
              
              <div class="form-group">
                <label>Jockey*</label>
                <select class="form-control" v-model="horse.jockey" required>
                  <option value="">Select Jockey</option>
                  <option 
                    v-for="jockey in jockeys" 
                    :key="jockey.name" 
                    :value="jockey.name"
                  >
                    {{ jockey.jockey_name }}
                  </option>
                </select>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Weight (kg)*</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model.number="horse.weight_carried"
                    min="0"
                    step="0.1"
                    required
                  >
                </div>
                
                <div class="form-group">
                  <label>Draw Number*</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model.number="horse.draw_number"
                    min="1"
                    required
                  >
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Trump Card</label>
                  <select class="form-control" v-model="horse.trump_card">
                    <option value="None">None</option>
                    <option value="Early Speed">Early Speed</option>
                    <option value="Strong Finish">Strong Finish</option>
                    <option value="Handles Wet Track">Handles Wet Track</option>
                    <option value="Good at Turns">Good at Turns</option>
                    <option value="Stamina">Stamina</option>
                    <option value="Consistent">Consistent</option>
                    <option value="Versatile">Versatile</option>
                  </select>
                </div>
                
                <div class="form-group emergency-toggle">
                  <label>Emergency</label>
                  <label class="switch">
                    <input type="checkbox" v-model="horse.is_emergency">
                    <span class="slider round"></span>
                  </label>
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Odds</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model.number="horse.odds"
                    min="0"
                    step="0.1"
                  >
                </div>
                
                <div class="form-group">
                  <label>Rating</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model.number="horse.rating"
                    min="0"
                    step="0.1"
                  >
                </div>
              </div>
              
              <div class="form-group">
                <label>Handicap</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="horse.handicap"
                >
              </div>
            </div>
            
            <div class="competitor-actions">
              <button 
                class="btn btn-sm btn-danger"
                @click="removeHorseFromSelection(horse)"
              >
                Remove
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="action-buttons">
      <button 
        class="btn btn-primary"
        @click="saveAllAssignments"
        :disabled="tempSelectedHorses.length === 0"
      >
        Save All Assignments
      </button>
      <button class="btn btn-secondary" @click="$emit('goBack')">
        Cancel
      </button>
    </div>
  </div>
</template>

<style scoped>
.assignment-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 20px;
}

.horse-list {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  height: calc(100vh - 250px);
  overflow-y: auto;
}

.horse-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.horse-card {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 12px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
}

.horse-card:hover {
  border-color: #b3d9ff;
  background-color: #f5f9ff;
}

.horse-card.selected {
  border-color: #4a90e2;
  background-color: #e6f0ff;
}

.horse-checkbox {
  margin-right: 10px;
}

.horse-info {
  flex-grow: 1;
}

.horse-info h6 {
  margin: 0 0 4px 0;
  font-size: 0.95em;
}

.horse-details {
  display: flex;
  gap: 8px;
  font-size: 0.8em;
  color: #666;
}

.horse-details span {
  display: inline-block;
}

.status-active {
  color: #28a745;
}

.status-injured {
  color: #dc3545;
}

.status-retired {
  color: #6c757d;
}

.selected-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.selected-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 15px;
}

.competitor-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  display: flex;
  transition: all 0.2s;
  position: relative;
}

.competitor-card.emergency {
  border-left: 4px solid #ffc107;
}

.competitor-number {
  font-size: 1.5em;
  font-weight: bold;
  color: #4a90e2;
  margin-right: 15px;
  width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.competitor-main {
  flex-grow: 1;
}

.competitor-name {
  font-weight: bold;
  margin-bottom: 10px;
}

.competitor-actions {
  display: flex;
  align-items: flex-start;
}

.form-group {
  margin-bottom: 10px;
}

.form-group label {
  display: block;
  font-size: 0.8em;
  margin-bottom: 4px;
  color: #555;
}

.form-control {
  width: 100%;
  padding: 6px 8px;
  font-size: 0.9em;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-row {
  display: flex;
  gap: 10px;
}

.form-row .form-group {
  flex: 1;
}

.emergency-toggle {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
  margin-top: 4px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
}

input:checked + .slider {
  background-color: #4a90e2;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.slider.round {
  border-radius: 24px;
}

.slider.round:before {
  border-radius: 50%;
}

.empty-state {
  padding: 20px;
  text-align: center;
  color: #666;
  font-style: italic;
  border: 1px dashed #ddd;
  border-radius: 6px;
  margin-top: 10px;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 0.85em;
}

@media (max-width: 992px) {
  .assignment-container {
    grid-template-columns: 1fr;
  }
  
  .horse-list {
    height: auto;
    max-height: 400px;
  }
}

.race-info {
  display: flex;
  gap: 15px;
  font-size: 0.9em;
  color: #666;
  margin-top: 5px;
}

@media (max-width: 768px) {
  .race-info {
    flex-direction: column;
    gap: 5px;
  }
  
  .horse-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    flex-direction: column;
    gap: 0;
  }
}
</style>