
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
const bets = ref([]);
const bookmakerOdds = ref([]);
const activeTab = ref('place-bet');
const selectedTicket = ref(null);
const betAmount = ref(0);
const selectedCompetitor = ref(null);
const isLoading = ref(false);

// Formatting functions
const formatCurrency = (value) => {
  return parseFloat(value).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
};

const formatDateTime = (value) => {
  return frappe.datetime.str_to_user(value);
};

// Data loading functions
const loadMeetings = async () => {
  try {
    isLoading.value = true;
    const response = await frappe.call('bms.api.get_upcoming_race_events');
    meetings.value = response.message || [];
  } catch (error) {
    console.error("Error loading meetings:", error);
    frappe.msgprint("Failed to load meetings");
  } finally {
    isLoading.value = false;
  }
};

const loadBookmakers = async () => {
  try {
    isLoading.value = true;
    bookmakers.value = await frappe.db.get_list("Bookmaker", {
      fields: ["name", "bookmaker_name"],
      filters: { status: "Active" }
    });
  } catch (error) {
    console.error("Error loading bookmakers:", error);
    frappe.msgprint("Failed to load bookmakers");
  } finally {
    isLoading.value = false;
  }
};

const loadRaceCompetitors = async () => {
  if (!selectedRace.value || !selectedBookmaker.value) return;
  
  try {
    isLoading.value = true;
    const response = await frappe.call('bms.api.get_race_competitors_with_odds', {
      race: selectedRace.value.name,
      bookmaker: selectedBookmaker.value
    });
    
    competitors.value = (response.message || []).map(comp => ({
      ...comp,
      total_bets: 0,
      total_amount: 0
    }));
    
    calculateTotals();
  } catch (error) {
    console.error("Error loading competitors:", error);
    frappe.msgprint("Failed to load competitors");
  } finally {
    isLoading.value = false;
  }
};

const loadBookmakerBets = async () => {
  if (!selectedRace.value || !selectedBookmaker.value) return;
  
  try {
    isLoading.value = true;
    const response = await frappe.call('bms.api.get_bookmaker_bet_tickets', {
      bookmaker: selectedBookmaker.value,
      race: selectedRace.value.name
    });
    
    bets.value = response.message || [];
    calculateTotals();
  } catch (error) {
    console.error("Error loading bets:", error);
    frappe.msgprint("Failed to load bets");
  } finally {
    isLoading.value = false;
  }
};

const loadBookmakerOdds = async () => {
  if (!selectedRace.value || !selectedBookmaker.value) return;
  
  try {
    isLoading.value = true;
    const response = await frappe.call('bms.api.get_bookmaker_odds_data', {
      bookmaker: selectedBookmaker.value,
      race: selectedRace.value.name
    });
    
    bookmakerOdds.value = response.message?.odds_table || [];
    
    // Initialize if empty
    if (bookmakerOdds.value.length === 0 && competitors.value.length > 0) {
      bookmakerOdds.value = competitors.value.map(comp => ({
        competitor: comp.name,
        number: comp.number,
        horse: comp.horse,
        horse_name: comp.horse_name || comp.horse,
        odds_f100: comp.odds || 0,
        inventory: 0
      }));
    }
  } catch (error) {
    console.error("Error loading odds:", error);
  } finally {
    isLoading.value = false;
  }
};

// Business logic functions
const calculateTotals = () => {
  competitors.value.forEach(comp => {
    comp.total_bets = 0;
    comp.total_amount = 0;
  });
  
  bets.value.forEach(bet => {
    const competitor = competitors.value.find(c => c.name === bet.competitor);
    if (competitor) {
      competitor.total_bets++;
      competitor.total_amount += bet.amount;
    }
  });
};

const selectCompetitor = (competitor) => {
  selectedCompetitor.value = competitor;
  betAmount.value = 0;
};

const placeBet = async () => {
  if (!selectedCompetitor.value || !betAmount.value || betAmount.value <= 0) {
    frappe.msgprint("Please select a competitor and enter a valid bet amount");
    return;
  }

  try {
    isLoading.value = true;
    await frappe.call('bms.api.create_bet_ticket', {
      bookmaker: selectedBookmaker.value,
      race: selectedRace.value.name,
      competitor: selectedCompetitor.value.name,
      amount: betAmount.value,
      race_event: selectedMeeting.value.name
    });
    
    frappe.show_alert({ message: "Bet placed successfully!", indicator: "green" });
    await loadBookmakerBets();
    betAmount.value = 0;
    selectedCompetitor.value = null;
  } catch (error) {
    console.error("Error placing bet:", error);
    frappe.msgprint("Failed to place bet");
  } finally {
    isLoading.value = false;
  }
};

const viewTicket = (ticket) => {
  selectedTicket.value = ticket;
  activeTab.value = 'ticket-view';
};

const backToBets = () => {
  selectedTicket.value = null;
  activeTab.value = 'tickets';
};

const updateBookmakerOdds = async () => {
  try {
    isLoading.value = true;
    await frappe.call('bms.api.save_bookmaker_odds_data', {
      bookmaker: selectedBookmaker.value,
      race: selectedRace.value.name,
      race_event: selectedMeeting.value.name,
      odds_data: bookmakerOdds.value
    });
    
    frappe.show_alert({ message: "Odds updated successfully!", indicator: "green" });
    await loadRaceCompetitors();
  } catch (error) {
    console.error("Error updating odds:", error);
    frappe.msgprint("Failed to update odds");
  } finally {
    isLoading.value = false;
  }
};

// Watchers
watch(selectedMeeting, (newMeeting) => {
  if (newMeeting) {
    races.value = newMeeting.races || [];
    selectedRace.value = null;
    competitors.value = [];
    bets.value = [];
    bookmakerOdds.value = [];
  }
});

watch(selectedRace, (newRace) => {
  if (newRace && selectedBookmaker.value) {
    loadRaceCompetitors();
    loadBookmakerBets();
    loadBookmakerOdds();
  }
});

watch(selectedBookmaker, (newBookmaker) => {
  if (newBookmaker && selectedRace.value) {
    loadRaceCompetitors();
    loadBookmakerBets();
    loadBookmakerOdds();
  }
});

// Initial load
onMounted(() => {
  loadMeetings();
  loadBookmakers();
});
</script>



<template>
  <div class="frappe-card">
    <div class="frappe-card-head">
      <h5 class="mb-0">Bookmaker Betting Interface</h5>
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
      
      <div v-if="selectedRace && selectedBookmaker">
        <ul class="nav nav-tabs mb-3">
          <li class="nav-item">
            <button 
              class="nav-link" 
              :class="{ 'active': activeTab === 'place-bet' }"
              @click="activeTab = 'place-bet'"
            >
              Place Bet
            </button>
          </li>
          <li class="nav-item">
            <button 
              class="nav-link" 
              :class="{ 'active': activeTab === 'tickets' }"
              @click="activeTab = 'tickets'"
            >
              Bet Tickets
            </button>
          </li>
          <li class="nav-item">
            <button 
              class="nav-link" 
              :class="{ 'active': activeTab === 'manage-odds' }"
              @click="activeTab = 'manage-odds'"
            >
              Manage Odds
            </button>
          </li>
        </ul>
        
        <div v-if="activeTab === 'place-bet'">
          <div v-if="competitors.length > 0" class="table-responsive">
            <table class="table table-bordered align-middle">
              <thead class="table-light">
                <tr>
                  <th>Number</th>
                  <th>Horse</th>
                  <th>Odds (F100)</th>
                  <th>Odds (F500)</th>
                  <th>Total Bets</th>
                  <th>Total Amount</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(comp, index) in competitors" :key="index">
                  <td>{{ comp.number }}</td>
                  <td>{{ comp.horse_name || comp.horse }}</td>
                  <td>{{ comp.odds || 'N/A' }}</td>
                  <td>{{ (comp.odds * 0.05).toFixed(2) }}</td>
                  <td>{{ comp.total_bets }}</td>
                  <td>{{ comp.total_amount }}</td>
                  <td>
                    <button 
                      class="btn btn-sm btn-outline-primary"
                      @click="selectCompetitor(comp)"
                    >
                      Select
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            
            <div v-if="selectedCompetitor" class="card mt-3">
              <div class="card-body">
                <h5 class="card-title">Place Bet</h5>
                <div class="row g-3">
                  <div class="col-md-6">
                    <label class="form-label">Selected Competitor</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      :value="selectedCompetitor.horse_name || selectedCompetitor.horse"
                      readonly
                    />
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Odds (F100)</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      :value="selectedCompetitor.odds || 'N/A'"
                      readonly
                    />
                  </div>
                  <div class="col-md-12">
                    <label class="form-label">Bet Amount</label>
                    <input 
                      type="number" 
                      class="form-control" 
                      v-model.number="betAmount"
                      placeholder="Enter bet amount"
                      min="1"
                    />
                  </div>
                  <div class="col-md-12">
                    <button 
                      class="btn btn-primary"
                      @click="placeBet"
                      :disabled="isLoading || !betAmount"
                    >
                      <span v-if="isLoading">Processing...</span>
                      <span v-else>Place Bet</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-muted text-center py-4">
            No competitors available for this race
          </div>
        </div>
        
        <div v-if="activeTab === 'tickets'">
          <div v-if="bets.length > 0" class="table-responsive">
            <table class="table table-bordered align-middle">
              <thead class="table-light">
                <tr>
                  <th>Ticket #</th>
                  <th>Horse</th>
                  <th>Odds</th>
                  <th>Amount</th>
                  <th>Potential Win</th>
                  <th>Time</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(bet, index) in bets" :key="index">
                  <td>{{ bet.name }}</td>
                  <td>{{ bet.horse_name || bet.horse }}</td>
                  <td>{{ bet.odds }}</td>
                  <td>{{ formatCurrency(bet.amount) }}</td>
                  <td>{{ formatCurrency(bet.amount * bet.odds) }}</td>
                  <td>{{ formatDateTime(bet.creation) }}</td>
                  <td>
                    <button 
                      class="btn btn-sm btn-outline-primary"
                      @click="viewTicket(bet)"
                    >
                      View
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="text-muted text-center py-4">
            No bets placed yet
          </div>
        </div>
        
        <div v-if="activeTab === 'manage-odds'">
          <div v-if="bookmakerOdds.length > 0" class="table-responsive">
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
                <tr v-for="(item, index) in bookmakerOdds" :key="index">
                  <td>{{ item.number }}</td>
                  <td>{{ item.horse_name }}</td>
                  <td>
                    <input
                      type="number"
                      class="form-control form-control-sm"
                      v-model.number="item.odds_f100"
                      min="0"
                      step="0.1"
                    />
                  </td>
                  <td>{{ (item.odds_f100 * 0.05).toFixed(2) }}</td>
                  <td>
                    <input
                      type="number"
                      class="form-control form-control-sm"
                      v-model.number="item.inventory"
                      min="0"
                    />
                  </td>
                </tr>
              </tbody>
            </table>
            
            <button 
              class="btn btn-primary mt-3"
              @click="updateBookmakerOdds"
              :disabled="isLoading"
            >
              <span v-if="isLoading">Saving...</span>
              <span v-else>Update Odds</span>
            </button>
          </div>
          <div v-else class="text-muted text-center py-4">
            No odds data available for this race and bookmaker
          </div>
        </div>
        
        <div v-if="activeTab === 'ticket-view' && selectedTicket" class="card">
          <div class="card-body text-center">
            <h4 class="card-title">Bet Ticket</h4>
            <div class="mb-4">
              <div class="qr-code-placeholder bg-light p-3 d-inline-block">
                <div class="text-center">
                  <i class="fa fa-qrcode fa-5x"></i>
                  <p class="mt-2">Ticket #{{ selectedTicket.name }}</p>
                </div>
              </div>
            </div>
            
            <div class="text-start mx-auto" style="max-width: 300px;">
              <div class="mb-2">
                <strong>Race:</strong> {{ selectedRace.race_name }}
              </div>
              <div class="mb-2">
                <strong>Horse:</strong> {{ selectedTicket.horse_name || selectedTicket.horse }}
              </div>
              <div class="mb-2">
                <strong>Odds:</strong> {{ selectedTicket.odds }}
              </div>
              <div class="mb-2">
                <strong>Amount:</strong> {{ formatCurrency(selectedTicket.amount) }}
              </div>
              <div class="mb-2">
                <strong>Potential Win:</strong> {{ formatCurrency(selectedTicket.amount * selectedTicket.odds) }}
              </div>
              <div class="mb-2">
                <strong>Bookmaker:</strong> {{ bookmakers.find(b => b.name === selectedBookmaker)?.bookmaker_name }}
              </div>
              <div class="mb-2">
                <strong>Time:</strong> {{ formatDateTime(selectedTicket.creation) }}
              </div>
            </div>
            
            <button 
              class="btn btn-primary mt-4"
              @click="backToBets"
            >
              Back to Tickets
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<style scoped>
.frappe-card {
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

.nav-tabs .nav-link {
  color: var(--text-light);
}

.nav-tabs .nav-link.active {
  color: var(--primary);
  font-weight: 500;
}

.qr-code-placeholder {
  border: 1px dashed var(--gray-400);
  border-radius: var(--border-radius);
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}
</style>