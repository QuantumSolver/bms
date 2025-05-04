<script setup>
import { ref, onMounted, watch } from 'vue';

// Reactive state
const meetings = ref([]);
const selectedMeeting = ref(null);
const races = ref([]);
const selectedRace = ref(null);
const bookmakers = ref([]);
const selectedBookmaker = ref(null);
const competitors = ref([]);
const oddsData = ref([]);
const isLoading = ref(false);

// Load initial data
onMounted(() => {
  loadMeetings();
  loadBookmakers();
});

// Watch for meeting selection changes
watch(selectedMeeting, (newMeeting) => {
  if (newMeeting) {
    races.value = newMeeting.races || [];
    selectedRace.value = null;
    competitors.value = [];
    oddsData.value = [];
  }
});

// Watch for race selection changes
watch(selectedRace, (newRace) => {
  if (newRace) {
    loadCompetitors(newRace.name);
  }
});

// Watch for bookmaker selection changes
watch(selectedBookmaker, (newBookmaker) => {
  if (newBookmaker && selectedRace.value) {
    loadExistingOdds(newBookmaker, selectedRace.value.name);
  }
});

// Data fetching functions
const loadMeetings = () => {
  isLoading.value = true;
  frappe.call({
    method: "bms.api.get_upcoming_events",
    callback: (response) => {
      isLoading.value = false;
      meetings.value = response.message || [];
    },
    error: () => {
      isLoading.value = false;
      frappe.msgprint("Failed to load meetings");
    }
  });
};

const loadBookmakers = async () => {
  try {
    const bookmakersList = await frappe.db.get_list("Bookmaker", {
      fields: ["name", "bookmaker_name"],
      filters: { status: "Active" }
    });
    bookmakers.value = bookmakersList;
  } catch (error) {
    console.error("Error loading bookmakers:", error);
    frappe.msgprint("Failed to load bookmakers");
  }
};

const loadCompetitors = (race) => {
  frappe.call({
    method: "bms.api.get_race_competitors",
    args: { race: race },
    callback: (response) => {
      competitors.value = response.message || [];
      
      // Initialize odds data with default values
      oddsData.value = competitors.value.map(comp => ({
        competitor: comp.name,
        number: comp.number,
        horse: comp.horse,
        horse_name: comp.horse_name || comp.horse, // Fixed: Use horse_name if available
        odds_f100: comp.odds || 0,
        inventory: 0
      }));
    }
  });
};

const loadExistingOdds = (bookmaker, race) => {
  frappe.call({
    method: "bms.api.get_bookmaker_odds",
    args: { bookmaker: bookmaker, race: race },
    callback: (response) => {
      if (response.message) {
        oddsData.value = response.message.odds_table.map(item => ({
          competitor: item.competitor,
          number: item.number,
          horse: item.horse,
          horse_name: item.horse_name || item.horse,
          odds_f100: item.odds_f100,
          inventory: item.inventory
        }));
      } else {
        // If no existing odds, initialize with competitors data
        oddsData.value = competitors.value.map(comp => ({
          competitor: comp.name,
          number: comp.number,
          horse: comp.horse,
          horse_name: comp.horse_name || comp.horse,
          odds_f100: 0,
          inventory: 0
        }));
      }
    }
  });
};

const handleOddsChange = (index, field, value) => {
  const updatedOdds = [...oddsData.value];
  updatedOdds[index][field] = value;
  oddsData.value = updatedOdds;
};

const saveOdds = () => {
  if (!selectedBookmaker.value || !selectedRace.value || !selectedMeeting.value) return;
  
  isLoading.value = true;
  frappe.call({
    method: "bms.api.save_bookmaker_odds",
    args: {
      bookmaker: selectedBookmaker.value,
      race: selectedRace.value.name,
      race_event: selectedMeeting.value.name,
      odds_data: oddsData.value
    },
    callback: () => {
      isLoading.value = false;
      frappe.show_alert({
        message: __("Odds saved successfully"),
        indicator: "green"
      });
    },
    error: (error) => {
      isLoading.value = false;
      console.error("Error saving odds:", error);
      frappe.msgprint("Failed to save odds");
    }
  });
};
</script>

<template>
  <div class="frappe-card">
    <div class="frappe-card-head">
      <h5 class="mb-0">Bookmaker Odds Management</h5>
    </div>
    
    <div class="frappe-card-body">
      <div class="row g-3 mb-4">
        <div class="col-md-4">
          <label class="control-label">Meeting</label>
          <select 
            class="input-with-feedback form-control ellipsis bold"
            v-model="selectedMeeting"
          >
            <option :value="null">Select Meeting</option>
            <option 
              v-for="meeting in meetings" 
              :key="meeting.name" 
              :value="meeting"
            >
              {{ meeting.meet_date }} - {{ meeting.venue }}
            </option>
          </select>
        </div>
        
        <div class="col-md-4">
          <label class="control-label">Race</label>
          <select 
            class="input-with-feedback form-control ellipsis bold"
            v-model="selectedRace"
            :disabled="!selectedMeeting"
          >
            <option :value="null">Select Race</option>
            <option 
              v-for="race in races" 
              :key="race.name" 
              :value="race"
            >
              {{ race.race_name }} ({{ race.race_time }})
            </option>
          </select>
        </div>
        
        <div class="col-md-4">
          <label class="control-label">Bookmaker</label>
          <select 
            class="input-with-feedback form-control ellipsis bold"
            v-model="selectedBookmaker"
            :disabled="bookmakers.length === 0"
          >
            <option :value="null">Select Bookmaker</option>
            <option 
              v-for="bm in bookmakers" 
              :key="bm.name" 
              :value="bm.name"
            >
              {{ bm.bookmaker_name }}
            </option>
          </select>
        </div>
      </div>
      
      <div v-if="oddsData.length > 0" class="table-responsive">
        <table class="table table-bordered align-middle">
          <thead class="table-light">
            <tr>
              <th>Number</th>
              <th>Horse</th>
              <th>Odds (F100)</th>
              <th>Odds (F500)</th>
              <th>Inventory</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in oddsData" :key="index">
              <td>{{ item.number }}</td>
              <td>{{ item.horse_name }}</td>
              <td>
                <input
                  type="number"
                  class="form-control form-control-sm"
                  v-model.number="item.odds_f100"
                  @change="handleOddsChange(index, 'odds_f100', $event.target.value)"
                />
              </td>
              <td>{{ (item.odds_f100 * 0.05).toFixed(2) }}</td>
              <td>
                <input
                  type="number"
                  class="form-control form-control-sm"
                  v-model.number="item.inventory"
                  @change="handleOddsChange(index, 'inventory', $event.target.value)"
                />
              </td>
            </tr>
          </tbody>
        </table>
        
        <button 
          class="btn btn-primary btn-sm mt-3"
          @click="saveOdds"
          :disabled="isLoading || !selectedBookmaker || !selectedRace"
        >
          <span v-if="isLoading">Saving...</span>
          <span v-else>Save Odds</span>
        </button>
      </div>
      
      <div v-else-if="selectedRace && selectedBookmaker" class="text-muted text-center py-4">
        No odds data available for this race and bookmaker
      </div>
      <div v-else-if="bookmakers.length === 0" class="text-muted text-center py-4">
        Loading bookmakers...
      </div>
    </div>
  </div>
</template>
<style scoped>.frappe-card {
  background-color: #fff;
  border: 1px solid var(--gray-300);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  margin-bottom: 1.5rem;
}

.frappe-card-head {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--gray-300);
  background-color: #f9fafb;
}

.frappe-card-body {
  padding: 1.25rem;
}

.table th,
.table td {
  vertical-align: middle;
}

.form-label {
  font-weight: 500;
  margin-bottom: 0.5rem;
}

</style>