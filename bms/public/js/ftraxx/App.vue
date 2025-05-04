<script setup>
import { ref, onMounted } from "vue";
import { createToast } from "./utils";
import StableSelection from "./components/StableSelection.vue";
import EventSelection from "./components/EventSelection.vue";
import RaceSelection from "./components/RaceSelection.vue";
import HorseAssignment from "./components/HorseAssignment.vue";
import Breadcrumbs from "./components/Breadcrumbs.vue";
import { fadeIn, slideUp } from "./components/animations";

// Main reactive state
const upcomingEvents = ref([]);
const stables = ref([]);
const selectedStable = ref(null);
const selectedEvent = ref(null);
const selectedRace = ref(null);
const availableHorses = ref([]);
const selectedHorses = ref([]);
const jockeys = ref([]);
const showAssignmentModal = ref(false);
const currentAssignment = ref({
  horse: null,
  horse_name: "",
  jockey: null,
  trump_card: "None",
  is_emergency: false,
  weight_carried: 0,
  draw_number: 0
});

// Navigation functions
const goToStables = () => {
  selectedStable.value = null;
  selectedEvent.value = null;
  selectedRace.value = null;
};

const goToEvents = () => {
  selectedEvent.value = null;
  selectedRace.value = null;
};

const goToRaces = () => {
  selectedRace.value = null;
};

// Data fetching functions
const fetchUpcomingEvents = async () => {
  try {
    const { message } = await frappe.call({
      method: "bms.api.get_upcoming_events"
    });
    upcomingEvents.value = message;
  } catch (error) {
    createToast("Error loading events: " + error.message, "error");
  }
};

const fetchUserStables = async () => {
  try {
    const { message } = await frappe.call({
      method: "bms.api.get_user_stables"
    });
    stables.value = message;
    
    if (stables.value.length === 1) {
      selectStable(stables.value[0]);
    }
  } catch (error) {
    createToast("Error loading stables: " + error.message, "error");
  }
};

const fetchStableHorses = async () => {
  if (!selectedStable.value) {
    availableHorses.value = [];
    return;
  }
  
  try {
    const { message } = await frappe.call({
      method: "bms.api.get_stable_horses",
      args: { stable: selectedStable.value.name }
    });
    availableHorses.value = message;
  } catch (error) {
    createToast("Error loading horses: " + error.message, "error");
  }
};

const fetchJockeys = async () => {
  try {
    const { message } = await frappe.call({
      method: "bms.api.get_jockeys"
    });
    jockeys.value = message;
  } catch (error) {
    createToast("Error loading jockeys: " + error.message, "error");
  }
};

const loadSelectedHorses = async () => {
  if (!selectedRace.value) return;
  
  try {
    const { message } = await frappe.call({
      method: "bms.api.get_race_competitors",
      args: { race: selectedRace.value.name }
    });
    selectedHorses.value = message;
  } catch (error) {
    createToast("Error loading competitors: " + error.message, "error");
  }
};

// User interaction handlers
const selectStable = (stable) => {
  selectedStable.value = {
    name: stable.name,
    stable_name: stable.stable_name,
    total_horses: stable.total_horses || 0
  };
  fetchStableHorses();
};

const selectEvent = (event) => {
  selectedEvent.value = event;
  goToRaces();
};

const selectRace = (race) => {
  selectedRace.value = race;
  loadSelectedHorses();
};

const addHorseToRace = (horse) => {
  currentAssignment.value = {
    horse: horse.name,
    horse_name: horse.horse_name,
    jockey: null,
    trump_card: "None",
    is_emergency: false,
    weight_carried: 0,
    draw_number: 0
  };
  showAssignmentModal.value = true;
};

const saveAssignments = async ({ race, competitors }) => {
  try {
    // First remove existing competitors
    const existing = await frappe.call({
      method: "bms.api.get_race_competitors",
      args: { race }
    });
    
    if (existing.message.length > 0) {
      await frappe.call({
        method: "bms.api.remove_all_competitors",
        args: { race }
      });
    }
    
    // Add all new competitors - ensure we're passing proper objects
    const results = await Promise.all(
      competitors.map(competitor => 
        frappe.call({
          method: "bms.api.add_competitor_to_race",
          args: {
            race: race,
            competitor: JSON.parse(JSON.stringify(competitor)) // Ensure plain object
          },
          freeze: true,
          freeze_message: __("Saving competitors...")
        })
      )
    );
    
    createToast(`Successfully saved ${results.length} competitors!`);
    loadSelectedHorses(); // Refresh the list
  } catch (error) {
    createToast("Error saving assignments: " + error.message, "error");
    console.error(error);
  }
};

const removeHorseFromRace = async (competitor) => {
  try {
    await frappe.call({
      method: "bms.api.remove_competitor_from_race",
      args: { competitor_name: competitor.name }
    });
    createToast("Horse removed from race!");
    loadSelectedHorses();
  } catch (error) {
    createToast("Error removing horse: " + error.message, "error");
  }
};

// Initialize component
onMounted(() => {
  fetchUpcomingEvents();
  fetchUserStables();
  fetchJockeys();
});
</script>

<template>
  <div class="bms-container">
    <Breadcrumbs 
      :selectedStable="selectedStable"
      :selectedEvent="selectedEvent"
      :selectedRace="selectedRace"
      @goToStables="goToStables"
      @goToEvents="goToEvents"
      @goToRaces="goToRaces"
    />
    
    <Transition name="fade" mode="out-in">
      <StableSelection
        v-if="!selectedStable"
        :stables="stables"
        @selectStable="selectStable"
      />
      
      <EventSelection
        v-else-if="selectedStable && !selectedEvent"
        :upcomingEvents="upcomingEvents"
        @selectEvent="selectEvent"
        @goBack="goToStables"
      />
      
      <RaceSelection
        v-else-if="selectedEvent && !selectedRace"
        :selectedEvent="selectedEvent"
        @selectRace="selectRace"
        @goBack="goToEvents"
      />
      
      <HorseAssignment
    v-else-if="selectedRace"
    :selectedStable="selectedStable"
    :selectedRace="selectedRace"
    :availableHorses="availableHorses"
    :selectedHorses="selectedHorses"
    :jockeys="jockeys" 
    @saveAssignments="saveAssignments"
    @goBack="goToRaces"
  />
    </Transition>
<!--     
    <AssignmentModal
      v-if="showAssignmentModal"
      :currentAssignment="currentAssignment"
      :jockeys="jockeys"
      @save="saveAssignment"
      @close="showAssignmentModal = false"
    /> -->
  </div>
</template>

<style scoped>
.bms-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Animation styles */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease-out;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>