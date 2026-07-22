import os
import fastf1

# 1. Enable FastF1 Cache
if not os.path.exists('cache'):
    os.makedirs('cache')
fastf1.Cache.enable_cache('cache')

CIRCUIT_MAP = {
    "albert_park": "Australia",
    "monaco": "Monaco",
    "silverstone": "Great Britain",
    "spa": "Belgium"
}

def generate_sc_probabilities(circuits, years=list(range(2018, 2026))):
    sc_stats = {}
    
    for circuit_id in circuits:
        f1_gp_name = CIRCUIT_MAP.get(circuit_id, circuit_id)
        
        total_races = 0
        races_with_sc = 0
        
        print(f"\nProcessing {circuit_id} ({f1_gp_name})...")
        
        for year in years:
            try:
                session = fastf1.get_session(year, f1_gp_name, 'R')
                # laps=True is REQUIRED to load track_status (telemetry=False keeps it light)
                session.load(laps=True, telemetry=False, weather=False, messages=True)
                
                # Fetch track status codes ('4'=SC, '5'=Red Flag, '6'=VSC)
                statuses = session.track_status['Status'].astype(str).values
                
                # Check if code 4, 5, or 6 was flagged during the race
                sc_occurred = any(code in statuses for code in ['4', '5', '6'])
                
                total_races += 1
                if sc_occurred:
                    races_with_sc += 1
                    print(f"  -> {year} {f1_gp_name}: SC/VSC/Red Flag deployed")
                else:
                    print(f"  -> {year} {f1_gp_name}: Clean race (No SC)")
                
            except Exception as e:
                # Printed out so we can diagnose any failed years/sessions
                print(f"  -> {year} {f1_gp_name}: Skipped ({e})")
                continue

        if total_races > 0:
            prob = (races_with_sc / total_races) * 100
            sc_stats[circuit_id] = f"{round(prob, 1)}%"
        else:
            sc_stats[circuit_id] = "No Data"

    return sc_stats

if __name__ == "__main__":
    test_circuits = ["albert_park", "monaco", "silverstone"]
    results = generate_sc_probabilities(test_circuits)
    
    print("\nFinal Safety Car Probabilities:")
    print(results)