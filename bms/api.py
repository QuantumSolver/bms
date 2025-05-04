# bms/api.py
import frappe
from frappe import _
from frappe.utils import flt,cint

@frappe.whitelist()
def get_upcoming_events():
    """Get upcoming race events"""
    events = frappe.get_all("Race Events",
        filters={"status": ["in", ["Draft", "Scheduled"]], "meet_date": [">=", frappe.utils.nowdate()]},
        fields=["name", "meet_date", "venue", "organizer", "status"],
        order_by="meet_date"
    )
    
    # Get races for each event
    for event in events:
        event.races = frappe.get_all("Races",
            filters={"parent": event.name},
            fields=["name", "race_name", "race_time", "distance", "status"]
        )
    
    return events


@frappe.whitelist()
def get_jockeys():
    """Get all active jockeys"""
    jockeys = frappe.get_all("Jockey",
        filters={"status": "Active"},
        fields=["name", "jockey_name"]
    )
    return jockeys

@frappe.whitelist()
def get_race_competitors(race):
    """Get competitors for a specific race"""
    competitors = frappe.get_all("Race Competitor",
        filters={"parent": race},
        fields=["name", "horse", "jockey", "trump_card", "is_emergency"]
    )
    return competitors

# @frappe.whitelist()
# def add_competitor_to_race(race, competitor):
#     """Add a horse to a race with assignment details"""
#     race_doc = frappe.get_doc("Races", race)
    
#     # Create new competitor
#     competitor_doc = frappe.get_doc({
#         "doctype": "Race Competitor",
#         "parent": race,
#         "parenttype": "Races",
#         "parentfield": "nomination",
#         "horse": competitor.horse,
#         "jockey": competitor.jockey,
#         "trump_card": competitor.trump_card,
#         "is_emergency": competitor.is_emergency,
#         "weight_carried": competitor.weight_carried,
#         "draw_number": competitor.draw_number
#     })
    
#     competitor_doc.insert()
#     return competitor_doc.name

# @frappe.whitelist()
# def remove_competitor_from_race(competitor_name):
#     """Remove a horse from a race"""
#     frappe.delete_doc("Race Competitor", competitor_name)
#     return True

@frappe.whitelist()
def remove_all_competitors(race):
    """Remove all competitors from a race"""
    competitors = frappe.get_all("Race Competitor", 
        filters={"parent": race},
        pluck="name"
    )
    
    for competitor in competitors:
        frappe.delete_doc("Race Competitor", competitor)
    
    return len(competitors)
@frappe.whitelist()
def add_competitor_to_race(race, competitor):
    """Add a horse to a race with assignment details"""
    # Handle case where competitor comes as stringified JSON
    if isinstance(competitor, str):
        try:
            competitor = frappe.parse_json(competitor)
        except:
            frappe.throw("Invalid competitor data format")
    
    # Validate required fields
    required_fields = ['horse', 'jockey']
    for field in required_fields:
        if not competitor.get(field):
            frappe.throw(f"Missing required field: {field}")
    
    # Create new competitor
    competitor_doc = frappe.get_doc({
        "doctype": "Race Competitor",
        "parent": race,
        "parenttype": "Races",
        "parentfield": "nomination",
        "horse": competitor.get("horse"),
        "horse_name": competitor.get("horse_name"),
        "jockey": competitor.get("jockey"),
        "trump_card": competitor.get("trump_card", "None"),
        "is_emergency": competitor.get("is_emergency", False),
        "weight_carried": competitor.get("weight_carried", 0),
        "draw_number": competitor.get("draw_number", 0),
        "odds": competitor.get("odds", 0),
        "rating": competitor.get("rating", 0),
        "handicap": competitor.get("handicap", ""),
        "number": competitor.get("number", 0)
    })
    
    competitor_doc.insert()
    return competitor_doc.name


@frappe.whitelist()
def get_user_stables():
    """Get all stables (not filtered by owner)"""
    stables = frappe.get_all("Stable",  
        fields=["name", "stable_name"]  
    )
    
    # Add horse count for each stable
    for stable in stables:
        stable.total_horses = frappe.db.count("Horses", {"parent": stable.name})
    
    return stables

@frappe.whitelist()
def get_stable_horses(stable):
    """Get all horses belonging to a stable"""
    if not stable:
        return []
    
    return frappe.get_all("Horses",
        filters={"parent": stable},
        fields=["name", "horse_name", "date_of_birth", "gender", "status", "breed"],
        order_by="horse_name"
    )


@frappe.whitelist()
def get_race_competitors(race):
    """Get competitors for a specific race with all required fields"""
    competitors = frappe.get_all("Race Competitor",
        filters={"parent": race},
        fields=["name", "horse",  "number", "odds"]
    )
    return competitors

@frappe.whitelist()
def get_bookmaker_odds(bookmaker, race):
    """Get existing odds for a bookmaker and race"""
    odds = frappe.get_all("Bookmaker Odds",
        filters={"bookmaker": bookmaker, "race": race},
        fields=["name", "race_event"]
    )
    
    if odds:
        odds_doc = frappe.get_doc("Bookmaker Odds", odds[0].name)
        return {
            "name": odds_doc.name,
            "odds_table": [
                {
                    "competitor": item.competitor,
                    "number": item.number,
                    "horse": item.horse,
                    "odds_f100": item.odds_f100,
                    "inventory": item.inventory
                } for item in odds_doc.odds_table
            ]
        }
    return None

@frappe.whitelist()
def save_bookmaker_odds(bookmaker, race, race_event, odds_data):
    """Save or update bookmaker odds"""
    # Check if odds already exist
    existing = frappe.get_all("Bookmaker Odds",
        filters={"bookmaker": bookmaker, "race": race},
        fields=["name"]
    )
    
    if existing:
        doc = frappe.get_doc("Bookmaker Odds", existing[0].name)
        doc.odds_table = []
    else:
        doc = frappe.new_doc("Bookmaker Odds")
        doc.bookmaker = bookmaker
        doc.race = race
        doc.race_event = race_event
    
    # Parse and validate odds data
    try:
        odds_items = frappe.parse_json(odds_data)
    except:
        frappe.throw("Invalid odds data format")
    
    # Add odds items
    for item in odds_items:
        doc.append("odds_table", {
            "competitor": item.get("competitor"),
            "number": item.get("number", 0),
            "horse": item.get("horse"),
            "horse_name": item.get("horse_name"),
            "odds_f100": flt(item.get("odds_f100", 0)),
            "inventory": cint(item.get("inventory", 0))
        })
    
    doc.save()
    frappe.db.commit()
    return doc.name





    # bets

@frappe.whitelist()
def get_upcoming_race_events():
    """Get upcoming race events with races"""
    events = frappe.get_all("Race Events",
        filters={"status": ["in", ["Draft", "Scheduled"]], "meet_date": [">=", frappe.utils.nowdate()]},
        fields=["name", "meet_date", "venue", "organizer", "status"],
        order_by="meet_date"
    )
    
    for event in events:
        event.races = frappe.get_all("Races",
            filters={"parent": event.name},
            fields=["name", "race_name", "race_time", "distance", "status"]
        )
    
    return events

@frappe.whitelist()
def get_race_competitors_with_odds(race, bookmaker=None):
    """Get competitors with bookmaker-specific odds if available"""
    competitors = frappe.get_all("Race Competitor",
        filters={"parent": race},
        fields=["name", "horse",  "number", "odds", "jockey"]
    )
    
    if bookmaker:
        bookmaker_odds = frappe.get_all("Bookmaker Odds",
            filters={"bookmaker": bookmaker, "race": race},
            fields=["name"]
        )
        
        if bookmaker_odds:
            odds_doc = frappe.get_doc("Bookmaker Odds", bookmaker_odds[0].name)
            for competitor in competitors:
                odds_item = next((item for item in odds_doc.odds_table 
                               if item.competitor == competitor.name), None)
                if odds_item:
                    competitor.odds = odds_item.odds_f100
    
    return competitors

@frappe.whitelist()
def get_bookmaker_bet_tickets(bookmaker, race):
    """Get all bets placed by a bookmaker for a specific race"""
    return frappe.get_all("Bet Ticket",
        filters={"bookmaker": bookmaker, "race": race},
        fields=["name", "horse", "horse_name", "odds", "amount", "creation", "competitor"],
        order_by="creation desc"
    )

@frappe.whitelist()
def get_bookmaker_odds_data(bookmaker, race):
    """Get existing odds for a bookmaker and race"""
    odds = frappe.get_all("Bookmaker Odds",
        filters={"bookmaker": bookmaker, "race": race},
        fields=["name", "race_event"]
    )
    
    if odds:
        odds_doc = frappe.get_doc("Bookmaker Odds", odds[0].name)
        return {
            "name": odds_doc.name,
            "odds_table": [
                {
                    "competitor": item.competitor,
                    "number": item.number,
                    "horse": item.horse,
                    "horse_name": item.horse,
                    "odds_f100": item.odds_f100,
                    "inventory": item.inventory
                } for item in odds_doc.odds_table
            ]
        }
    return None

@frappe.whitelist()
def save_bookmaker_odds_data(bookmaker, race, race_event, odds_data):
    """Save or update bookmaker odds"""
    existing = frappe.get_all("Bookmaker Odds",
        filters={"bookmaker": bookmaker, "race": race},
        fields=["name"]
    )
    
    if existing:
        doc = frappe.get_doc("Bookmaker Odds", existing[0].name)
        doc.odds_table = []
    else:
        doc = frappe.new_doc("Bookmaker Odds")
        doc.bookmaker = bookmaker
        doc.race = race
        doc.race_event = race_event
    
    try:
        odds_items = frappe.parse_json(odds_data)
    except:
        frappe.throw("Invalid odds data format")
    
    for item in odds_items:
        doc.append("odds_table", {
            "competitor": item.get("competitor"),
            "number": item.get("number", 0),
            "horse": item.get("horse"),
            "horse_name": item.get("horse"),
            "odds_f100": flt(item.get("odds_f100", 0)),
            "inventory": cint(item.get("inventory", 0))
        })
    
    doc.save()
    frappe.db.commit()
    return doc.name

@frappe.whitelist()
def create_bet_ticket(bookmaker, race, competitor, amount, race_event):
    """Create a new bet ticket using bookmaker-specific odds"""
    competitor_doc = frappe.get_doc("Race Competitor", competitor)
    
    # Get bookmaker-specific odds
    odds = competitor_doc.odds
    bookmaker_odds = frappe.get_all("Bookmaker Odds",
        filters={"bookmaker": bookmaker, "race": race},
        fields=["name"]
    )
    
    if bookmaker_odds:
        odds_doc = frappe.get_doc("Bookmaker Odds", bookmaker_odds[0].name)
        for item in odds_doc.odds_table:
            if item.competitor == competitor:
                odds = item.odds_f100
                break
    
    bet_doc = frappe.get_doc({
        "doctype": "Bet Ticket",
        "bookmaker": bookmaker,
        "race": race,
        "race_event": race_event,
        "competitor": competitor,
        "horse": competitor_doc.horse,
        "horse_name": competitor_doc.horse,
        "odds": odds,
        "amount": flt(amount),
        "status": "Active"
    })
    
    bet_doc.insert()
    frappe.db.commit()
    return bet_doc.name