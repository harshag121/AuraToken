"""
OPD Token Allocation Simulation
Simulates a full day at an OPD with 3 doctors, demonstrating:
- Token allocation from multiple sources
- Cancellations and no-shows
- Emergency insertions
- Dynamic reallocation
- Queue management
"""

import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Dict, List
import random

BASE_URL = "http://localhost:8000/api/v1"


class OPDSimulator:
    """Simulate OPD operations for testing."""
    
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.doctors: List[Dict] = []
        self.slots: List[Dict] = []
        self.tokens: List[Dict] = []
    
    async def setup_doctors(self):
        """Create 3 doctors with different specializations."""
        doctors_data = [
            {"name": "Dr. Sarah Johnson", "specialization": "General Medicine"},
            {"name": "Dr. Rajesh Kumar", "specialization": "Cardiology"},
            {"name": "Dr. Emily Chen", "specialization": "Pediatrics"}
        ]
        
        print("\n=== Setting Up Doctors ===")
        for doctor_data in doctors_data:
            response = await self.client.post(
                f"{BASE_URL}/doctors",
                json=doctor_data
            )
            doctor = response.json()
            self.doctors.append(doctor)
            print(f"✓ Created: {doctor['name']} ({doctor['specialization']})")
    
    async def setup_time_slots(self):
        """Create time slots for each doctor (9 AM - 5 PM)."""
        today = datetime.now().strftime("%Y-%m-%d")
        time_slots_config = [
            ("09:00", "10:00", 20),
            ("10:00", "11:00", 20),
            ("11:00", "12:00", 15),
            ("12:00", "13:00", 10),  # Reduced capacity during lunch
            ("13:00", "14:00", 20),
            ("14:00", "15:00", 20),
            ("15:00", "16:00", 15),
            ("16:00", "17:00", 10)
        ]
        
        print("\n=== Setting Up Time Slots ===")
        for doctor in self.doctors:
            print(f"\nDoctor: {doctor['name']}")
            for start, end, capacity in time_slots_config:
                slot_data = {
                    "doctor_id": doctor["id"],
                    "date": today,
                    "start_time": start,
                    "end_time": end,
                    "max_capacity": capacity
                }
                response = await self.client.post(
                    f"{BASE_URL}/slots",
                    json=slot_data
                )
                slot = response.json()
                self.slots.append(slot)
                print(f"  ✓ {start}-{end}: Capacity {capacity}")
    
    async def simulate_token_allocation(self):
        """Simulate token allocation throughout the day."""
        print("\n=== Simulating Token Allocation ===")
        
        # Patient data pool
        first_names = ["John", "Emma", "Michael", "Sophia", "William", "Olivia", 
                      "James", "Ava", "Robert", "Isabella", "David", "Mia"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
                     "Miller", "Davis", "Rodriguez", "Martinez"]
        
        sources = ["online", "walk_in", "priority", "follow_up"]
        source_weights = [0.4, 0.3, 0.15, 0.15]  # Distribution probabilities
        
        # Allocate tokens to different slots
        allocation_scenarios = [
            # Morning rush (9-11 AM) - High volume
            {"slot_range": (0, 2), "tokens_per_slot": 18},
            # Late morning (11-12) - Medium
            {"slot_range": (2, 3), "tokens_per_slot": 12},
            # Lunch (12-1) - Low
            {"slot_range": (3, 4), "tokens_per_slot": 8},
            # Afternoon (1-4) - Medium-High
            {"slot_range": (4, 6), "tokens_per_slot": 15},
            # Evening (4-5) - Medium
            {"slot_range": (6, 8), "tokens_per_slot": 10}
        ]
        
        token_count = 0
        
        for scenario in allocation_scenarios:
            for doctor in self.doctors:
                # Get doctor's slots for this time range
                doctor_slots = [
                    s for s in self.slots 
                    if s["doctor_id"] == doctor["id"]
                ]
                
                start_idx, end_idx = scenario["slot_range"]
                for slot_idx in range(start_idx, min(end_idx, len(doctor_slots))):
                    slot = doctor_slots[slot_idx]
                    num_tokens = min(
                        scenario["tokens_per_slot"],
                        slot["max_capacity"]
                    )
                    
                    # Allocate tokens
                    for i in range(num_tokens):
                        patient_name = f"{random.choice(first_names)} {random.choice(last_names)}"
                        patient_phone = f"+1{random.randint(2000000000, 9999999999)}"
                        source = random.choices(sources, weights=source_weights)[0]
                        
                        token_data = {
                            "patient_name": patient_name,
                            "patient_phone": patient_phone,
                            "doctor_id": doctor["id"],
                            "slot_id": slot["id"],
                            "source": source
                        }
                        
                        try:
                            response = await self.client.post(
                                f"{BASE_URL}/tokens",
                                json=token_data
                            )
                            if response.status_code == 201:
                                token = response.json()
                                self.tokens.append(token)
                                token_count += 1
                                if token_count % 20 == 0:
                                    print(f"  Allocated {token_count} tokens...")
                        except Exception as e:
                            print(f"  ⚠ Error allocating token: {e}")
        
        print(f"\n✓ Total tokens allocated: {token_count}")
    
    async def simulate_cancellations(self):
        """Simulate 10% cancellation rate."""
        print("\n=== Simulating Cancellations ===")
        
        num_cancellations = max(5, len(self.tokens) // 10)
        cancel_tokens = random.sample(self.tokens, num_cancellations)
        
        reasons = [
            "Patient unable to attend",
            "Rescheduled to different day",
            "Medical emergency elsewhere",
            "Patient recovered"
        ]
        
        cancelled_count = 0
        for token in cancel_tokens:
            try:
                response = await self.client.post(
                    f"{BASE_URL}/tokens/{token['id']}/cancel",
                    params={"reason": random.choice(reasons)}
                )
                if response.status_code == 200:
                    cancelled_count += 1
            except Exception as e:
                print(f"  ⚠ Error cancelling token: {e}")
        
        print(f"✓ Cancelled {cancelled_count} tokens")
    
    async def simulate_no_shows(self):
        """Simulate 5% no-show rate."""
        print("\n=== Simulating No-Shows ===")
        
        active_tokens = [
            t for t in self.tokens 
            if t.get("status") == "allocated"
        ]
        
        num_no_shows = max(3, len(active_tokens) // 20)
        no_show_tokens = random.sample(active_tokens, min(num_no_shows, len(active_tokens)))
        
        no_show_count = 0
        for token in no_show_tokens:
            try:
                response = await self.client.post(
                    f"{BASE_URL}/tokens/{token['id']}/no-show"
                )
                if response.status_code == 200:
                    no_show_count += 1
            except Exception as e:
                print(f"  ⚠ Error marking no-show: {e}")
        
        print(f"✓ Marked {no_show_count} patients as no-show")
    
    async def simulate_emergency_insertions(self):
        """Simulate emergency patient insertions."""
        print("\n=== Simulating Emergency Insertions ===")
        
        emergency_patients = [
            "Emergency Case - Chest Pain",
            "Emergency Case - Severe Allergic Reaction",
            "Emergency Case - Acute Asthma Attack"
        ]
        
        emergency_count = 0
        for patient_desc in emergency_patients:
            # Pick a random slot from first doctor
            doctor = self.doctors[0]
            available_slots = [
                s for s in self.slots 
                if s["doctor_id"] == doctor["id"] and s["available_capacity"] > 0
            ]
            
            if available_slots:
                slot = random.choice(available_slots)
                
                token_data = {
                    "patient_name": patient_desc,
                    "patient_phone": "+1-EMERGENCY",
                    "doctor_id": doctor["id"],
                    "slot_id": slot["id"],
                    "source": "priority",
                    "notes": "EMERGENCY CASE"
                }
                
                try:
                    response = await self.client.post(
                        f"{BASE_URL}/tokens",
                        json=token_data,
                        params={"emergency": True}
                    )
                    if response.status_code == 201:
                        token = response.json()
                        self.tokens.append(token)
                        emergency_count += 1
                        print(f"  ✓ Emergency insertion: {patient_desc}")
                except Exception as e:
                    print(f"  ⚠ Error inserting emergency: {e}")
        
        print(f"✓ Inserted {emergency_count} emergency patients")
    
    async def simulate_reallocation(self):
        """Simulate token reallocation due to delays."""
        print("\n=== Simulating Token Reallocation ===")
        
        # Get a doctor's slots
        doctor = self.doctors[1]
        doctor_slots = sorted(
            [s for s in self.slots if s["doctor_id"] == doctor["id"]],
            key=lambda x: x["start_time"]
        )
        
        if len(doctor_slots) < 2:
            print("  Not enough slots for reallocation demo")
            return
        
        # Get tokens from early slot
        source_slot = doctor_slots[0]
        target_slot = doctor_slots[1]
        
        response = await self.client.get(
            f"{BASE_URL}/tokens",
            params={"slot_id": source_slot["id"]}
        )
        
        if response.status_code == 200:
            slot_tokens = response.json()
            if slot_tokens:
                # Reallocate 2 tokens
                reallocated = 0
                for token in slot_tokens[:2]:
                    try:
                        realloc_response = await self.client.post(
                            f"{BASE_URL}/tokens/{token['id']}/reallocate",
                            json={
                                "new_slot_id": target_slot["id"],
                                "reason": "Doctor running behind schedule"
                            }
                        )
                        if realloc_response.status_code == 200:
                            reallocated += 1
                    except Exception as e:
                        print(f"  ⚠ Error reallocating: {e}")
                
                print(f"✓ Reallocated {reallocated} tokens due to delays")
    
    async def display_analytics(self):
        """Display comprehensive analytics."""
        print("\n" + "="*70)
        print("=== OPD DAY SIMULATION ANALYTICS ===")
        print("="*70)
        
        # System status
        response = await self.client.get(f"{BASE_URL}/analytics/system/status")
        if response.status_code == 200:
            status = response.json()
            print("\n📊 SYSTEM OVERVIEW")
            print(f"  Total Doctors: {status['total_doctors']}")
            print(f"  Active Doctors: {status['active_doctors']}")
            print(f"  Total Slots Today: {status['total_slots_today']}")
            print(f"  Total Tokens Today: {status['total_tokens_today']}")
            
            print(f"\n  Tokens by Status:")
            for status_name, count in status['tokens_by_status'].items():
                print(f"    - {status_name}: {count}")
            
            print(f"\n  Tokens by Source:")
            for source, count in status['tokens_by_source'].items():
                print(f"    - {source}: {count}")
        
        # Doctor-wise analytics
        today = datetime.now().strftime("%Y-%m-%d")
        print("\n" + "-"*70)
        print("📋 DOCTOR-WISE PERFORMANCE")
        print("-"*70)
        
        for doctor in self.doctors:
            response = await self.client.get(
                f"{BASE_URL}/analytics/doctors/{doctor['id']}/day/{today}"
            )
            if response.status_code == 200:
                analytics = response.json()
                print(f"\n🏥 {analytics['doctor_name']}")
                print(f"  Total Slots: {analytics['total_slots']}")
                print(f"  Total Capacity: {analytics['total_capacity']}")
                print(f"  Allocated Tokens: {analytics['total_allocated']}")
                print(f"  Completed: {analytics['total_completed']}")
                print(f"  Cancelled: {analytics['total_cancelled']}")
                print(f"  No-Shows: {analytics['total_no_shows']}")
                print(f"  Utilization: {analytics['average_utilization']:.1f}%")
        
        # Sample slot queue
        print("\n" + "-"*70)
        print("🎯 SAMPLE SLOT QUEUE (Priority Ordering)")
        print("-"*70)
        
        if self.slots:
            sample_slot = self.slots[4]  # Pick a mid-day slot
            response = await self.client.get(
                f"{BASE_URL}/slots/{sample_slot['id']}/queue"
            )
            if response.status_code == 200:
                queue = response.json()
                print(f"\nSlot: {sample_slot['start_time']}-{sample_slot['end_time']}")
                print(f"Doctor: {[d for d in self.doctors if d['id'] == sample_slot['doctor_id']][0]['name']}")
                print(f"\nQueue Order (Total: {len(queue)} patients):")
                
                for i, token in enumerate(queue[:10], 1):  # Show first 10
                    print(f"  {i}. Token {token['token_number']} - "
                          f"{token['patient_name']} [{token['source']}] "
                          f"(Priority: {token['priority_score']})")
                
                if len(queue) > 10:
                    print(f"  ... and {len(queue) - 10} more patients")
        
        print("\n" + "="*70)
    
    async def run(self):
        """Run the complete simulation."""
        print("\n" + "="*70)
        print("🏥 OPD TOKEN ALLOCATION ENGINE - DAY SIMULATION")
        print("="*70)
        print(f"Simulation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            await self.setup_doctors()
            await self.setup_time_slots()
            await self.simulate_token_allocation()
            await self.simulate_cancellations()
            await self.simulate_no_shows()
            await self.simulate_emergency_insertions()
            await self.simulate_reallocation()
            await self.display_analytics()
            
            print("\n✅ Simulation completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Simulation error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await self.client.aclose()


async def main():
    """Main entry point."""
    simulator = OPDSimulator()
    await simulator.run()


if __name__ == "__main__":
    print("\n⚠️  Make sure the API server is running on http://localhost:8000")
    print("Start it with: python -m app.main\n")
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        asyncio.run(main())
    else:
        print("To run simulation, use: python simulation.py --run")
