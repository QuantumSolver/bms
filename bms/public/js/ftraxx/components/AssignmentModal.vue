<script setup>
defineProps({
  currentAssignment: Object,
  jockeys: Array
});

defineEmits(['save', 'close']);
</script>

<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal" v-animate:slide-up>
      <h5>Assign Horse to Race</h5>
      <div class="modal-body">
        <div class="form-group">
          <label>Horse</label>
          <input type="text" class="form-control" v-model="currentAssignment.horse_name" disabled>
        </div>
        
        <div class="form-group">
          <label>Jockey</label>
          <select class="form-control" v-model="currentAssignment.jockey" required>
            <option value="">Select Jockey</option>
            <option v-for="jockey in jockeys" :key="jockey.name" :value="jockey.name">
              {{ jockey.jockey_name }}
            </option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Trump Card</label>
          <select class="form-control" v-model="currentAssignment.trump_card">
            <option v-for="card in [
              'None', 'Early Speed', 'Strong Finish', 'Handles Wet Track', 
              'Good at Turns', 'Stamina', 'Consistent', 'Versatile'
            ]" :key="card" :value="card">
              {{ card }}
            </option>
          </select>
        </div>
        
        <div class="form-row">
          <div class="form-group col-md-6">
            <label>Weight Carried (kg)</label>
            <input 
              type="number" 
              class="form-control" 
              v-model.number="currentAssignment.weight_carried"
              min="0"
              step="0.1"
              required
            >
          </div>
          <div class="form-group col-md-6">
            <label>Draw Number</label>
            <input 
              type="number" 
              class="form-control" 
              v-model.number="currentAssignment.draw_number"
              min="1"
              required
            >
          </div>
        </div>
        
        <div class="form-group form-check">
          <input 
            type="checkbox" 
            class="form-check-input" 
            id="emergencyCheck" 
            v-model="currentAssignment.is_emergency"
          >
          <label class="form-check-label" for="emergencyCheck">Emergency Replacement</label>
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="$emit('close')">Cancel</button>
        <button 
          class="btn btn-primary" 
          @click="$emit('save')"
          :disabled="!currentAssignment.jockey || !currentAssignment.weight_carried || !currentAssignment.draw_number"
        >
          Save Assignment
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* .modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white !important;
  border: 3px solid blue !important;
  border-radius: 5px;
  width: 500px;
  max-width: 90%;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
} */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050; /* Higher than most content */
}

.modal {
  background: white;
  border-radius: 5px;
  width: 500px;
  max-width: 90%;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  position: relative;
  z-index: 1051; /* Higher than backdrop */
  /* Add these to ensure visibility: */
  opacity: 1 !important;
  transform: none !important;
}
.modal h5 {
  margin-top: 0;
  color: #333;
}

.modal-body {
  margin: 20px 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.form-group {
  margin-bottom: 15px;
}

.form-check {
  margin-top: 20px;
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-row .form-group {
  flex: 1;
}
</style>