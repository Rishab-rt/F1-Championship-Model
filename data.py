races = ["Australian Grand Prix", "China Sprint", "Chinese Grand Prix", "Japanese Grand Prix", 
         "Miami Sprint", "Miami Grand Prix", "Canada Sprint", "Canadian Grand Prix", 
         "Monaco Grand Prix", "Spanish Grand Prix", "Austrian Grand Prix", "Silverstone Sprint",
         "British Grand Prix", "Belgian Grand Prix - SPA", "Hungarian Grand Prix", "Dutch Sprint", 
         "Dutch Grand Prix", "Italian Grand Prix", "Madrid Grand Prix", "Azerbaijan Grand Prix", 
         "Singapore Sprint", "Singapore Grand Prix", "Circuit of Americas Grand Prix", "Mexican Grand Prix", 
         "São Paulo Grand Prix", "Las Vegas Grand Prix", "Qatar Grand Prix", "Abu Dhabi Grand Prix"]

driver_to_team = {
    "Leclerc": "Ferrari", "Hamilton": "Ferrari",
    "Piastri": "McLaren", "Norris": "McLaren",
    "Russell": "Mercedes", "Antonelli": "Mercedes",
    "Verstappen": "Red Bull", "Hadjar": "Red Bull",
    "Sainz": "Williams", "Albon": "Williams",
    "Alonso": "Aston Martin", "Stroll": "Aston Martin",
    "Ocon": "Haas", "Bearman": "Haas",
    "Linblad": "Vcarb", "Lawson": "Vcarb",
    "Hulkenberg": "Audi", "Bortoleto": "Audi",
    "Gasly": "Alpine", "Colapinto": "Alpine",
    "Perez":"Cadillac","Bottas":"Cadillac"
}

driver_codes = {
    "Leclerc": "LEC", "Hamilton": "HAM", "Piastri": "PIA", "Norris": "NOR",
    "Russell": "RUS", "Antonelli": "ANT", "Verstappen": "VER", "Hadjar": "HAD",
    "Sainz": "SAI", "Albon": "ALB", "Alonso": "ALO", "Stroll": "STR",
    "Ocon": "OCO", "Bearman": "BEA", "Linblad": "LIN", "Lawson": "LAW",
    "Hulkenberg": "HUL", "Bortoleto": "BOR", "Gasly": "GAS", "Colapinto": "COL",
    "Perez": "PER", "Bottas": "BOT"
}

driver_number_to_name = {
    1: "Norris", 3: "Verstappen", 5: "Bortoleto", 6: "Hadjar",
    10: "Gasly", 12: "Antonelli", 16: "Leclerc", 23: "Albon",
    27: "Hulkenberg", 30: "Lawson", 31: "Ocon", 41: "Bearman",
    43: "Colapinto", 44: "Hamilton", 63: "Russell", 81: "Piastri",
    87: "Linblad", 14: "Alonso", 18: "Stroll", 11: "Perez",
    77: "Bottas", 55: "Sainz",
}

race_session_keys = {
    "Australian Grand Prix": 11234, "China Sprint": 11240, "Chinese Grand Prix": 11245,
    "Japanese Grand Prix": 11253, "Miami Sprint": 11275, "Miami Grand Prix": 11280,
    "Canada Sprint": 11286, "Canadian Grand Prix": 11291, "Monaco Grand Prix": 11299,
    "Spanish Grand Prix": 11307, "Austrian Grand Prix": 11315, "Silverstone Sprint": 11321,
    "British Grand Prix": 11326,
}

circuit_info = {
    "albert_park":  {"length": "5.278 km", "laps": 58,  "lap_record": "1:20.235", "lap_record_holder": "Leclerc (2022)",      "type": "Street"},
    "americas":     {"length": "5.513 km", "laps": 56,  "lap_record": "1:36.169", "lap_record_holder": "Leclerc (2019)",      "type": "Permanent"},
    "baku":         {"length": "6.003 km", "laps": 51,  "lap_record": "1:43.009", "lap_record_holder": "Leclerc (2019)",      "type": "Street"},
    "bahrain":      {"length": "5.412 km", "laps": 57,  "lap_record": "1:31.447", "lap_record_holder": "De la Rosa (2005)",   "type": "Permanent"},
    "catalunya":    {"length": "4.675 km", "laps": 66,  "lap_record": "1:16.330", "lap_record_holder": "Verstappen (2021)",   "type": "Permanent"},
    "hungaroring":  {"length": "4.381 km", "laps": 70,  "lap_record": "1:16.627", "lap_record_holder": "Hamilton (2020)",     "type": "Permanent"},
    "interlagos":   {"length": "4.309 km", "laps": 71,  "lap_record": "1:10.540", "lap_record_holder": "Verstappen (2023)",   "type": "Permanent"},
    "jeddah":       {"length": "6.174 km", "laps": 50,  "lap_record": "1:30.734", "lap_record_holder": "Leclerc (2022)",      "type": "Street"},
    "vegas":        {"length": "6.201 km", "laps": 50,  "lap_record": "1:35.490", "lap_record_holder": "Leclerc (2023)",      "type": "Street"},
    "losail":       {"length": "5.380 km", "laps": 57,  "lap_record": "1:24.319", "lap_record_holder": "Russell (2023)",      "type": "Permanent"},
    "miami":        {"length": "5.412 km", "laps": 57,  "lap_record": "1:29.708", "lap_record_holder": "Verstappen (2023)",   "type": "Street"},
    "monaco":       {"length": "3.337 km", "laps": 78,  "lap_record": "1:12.909", "lap_record_holder": "Leclerc (2024)",      "type": "Street"},
    "monza":        {"length": "5.793 km", "laps": 53,  "lap_record": "1:21.046", "lap_record_holder": "Barrichello (2004)",  "type": "Permanent"},
    "villeneuve":   {"length": "4.361 km", "laps": 70,  "lap_record": "1:13.078", "lap_record_holder": "Bottas (2019)",       "type": "Street"},
    "red_bull_ring":{"length": "4.318 km", "laps": 71,  "lap_record": "1:05.619", "lap_record_holder": "Leclerc (2020)",      "type": "Permanent"},
    "rodriguez":    {"length": "4.304 km", "laps": 71,  "lap_record": "1:17.774", "lap_record_holder": "Bottas (2021)",       "type": "Permanent"},
    "shanghai":     {"length": "5.451 km", "laps": 56,  "lap_record": "1:32.238", "lap_record_holder": "Verstappen (2024)",   "type": "Permanent"},
    "silverstone":  {"length": "5.891 km", "laps": 52,  "lap_record": "1:27.097", "lap_record_holder": "Hamilton (2020)",     "type": "Permanent"},
    "marina_bay":   {"length": "4.940 km", "laps": 62,  "lap_record": "1:35.867", "lap_record_holder": "Leclerc (2023)",      "type": "Street"},
    "spa":          {"length": "7.004 km", "laps": 44,  "lap_record": "1:46.286", "lap_record_holder": "Bottas (2018)",       "type": "Permanent"},
    "suzuka":       {"length": "5.807 km", "laps": 53,  "lap_record": "1:30.983", "lap_record_holder": "Verstappen (2023)",   "type": "Permanent"},
    "yas_marina":   {"length": "5.281 km", "laps": 58,  "lap_record": "1:26.103", "lap_record_holder": "Leclerc (2021)",      "type": "Permanent"},
    "zandvoort":    {"length": "4.259 km", "laps": 72,  "lap_record": "1:11.097", "lap_record_holder": "Verstappen (2021)",   "type": "Permanent"},
    "madring":      {"length": "5.059 km", "laps": 59,  "lap_record": "N/A",      "lap_record_holder": "New circuit",         "type": "Street"},
    "monte_carlo":  {"length": "3.337 km", "laps": 78,  "lap_record": "1:12.909", "lap_record_holder": "Leclerc (2024)",      "type": "Street"},
}

race_coords = {
    "Australian Grand Prix": ("-37.8497", "144.968"), "China Sprint": ("31.3389", "121.220"),
    "Chinese Grand Prix": ("31.3389", "121.220"), "Japanese Grand Prix": ("34.8431", "136.541"),
    "Miami Sprint": ("25.9581", "-80.2389"), "Miami Grand Prix": ("25.9581", "-80.2389"),
    "Canada Sprint": ("45.5000", "-73.5228"), "Canadian Grand Prix": ("45.5000", "-73.5228"),
    "Monaco Grand Prix": ("43.7347", "7.42056"), "Spanish Grand Prix": ("41.5700", "2.26111"),
    "Austrian Grand Prix": ("47.2197", "14.7647"), "Silverstone Sprint": ("52.0786", "-1.01694"),
    "British Grand Prix": ("52.0786", "-1.01694"), "Belgian Grand Prix - SPA": ("50.4372", "5.97139"),
    "Hungarian Grand Prix": ("47.5789", "19.2486"), "Dutch Sprint": ("52.3888", "4.54092"),
    "Dutch Grand Prix": ("52.3888", "4.54092"), "Italian Grand Prix": ("45.6156", "9.28111"),
    "Madrid Grand Prix": ("40.3831", "-3.71444"), "Azerbaijan Grand Prix": ("40.3725", "49.8533"),
    "Singapore Sprint": ("1.2914", "103.864"), "Singapore Grand Prix": ("1.2914", "103.864"),
    "Circuit of Americas Grand Prix": ("30.1328", "-97.6411"), "Mexican Grand Prix": ("19.4042", "-99.0907"),
    "São Paulo Grand Prix": ("-23.7036", "-46.6997"), "Las Vegas Grand Prix": ("36.1147", "-115.173"),
    "Qatar Grand Prix": ("25.4900", "51.4542"), "Abu Dhabi Grand Prix": ("24.4672", "54.6031"),
}

race_dates = {
    "Australian Grand Prix": "2026-03-15", "China Sprint": "2026-03-21", "Chinese Grand Prix": "2026-03-22",
    "Japanese Grand Prix": "2026-04-05", "Miami Sprint": "2026-05-02", "Miami Grand Prix": "2026-05-03",
    "Canada Sprint": "2026-06-13", "Canadian Grand Prix": "2026-06-14", "Monaco Grand Prix": "2026-05-24",
    "Spanish Grand Prix": "2026-06-28", "Austrian Grand Prix": "2026-07-05", "Silverstone Sprint": "2026-07-18",
    "British Grand Prix": "2026-07-19", "Belgian Grand Prix - SPA": "2026-08-02", "Hungarian Grand Prix": "2026-08-02",
    "Dutch Sprint": "2026-08-29", "Dutch Grand Prix": "2026-08-30", "Italian Grand Prix": "2026-09-06",
    "Madrid Grand Prix": "2026-09-13", "Azerbaijan Grand Prix": "2026-09-20", "Singapore Sprint": "2026-10-03",
    "Singapore Grand Prix": "2026-10-04", "Circuit of Americas Grand Prix": "2026-10-18", "Mexican Grand Prix": "2026-10-25",
    "São Paulo Grand Prix": "2026-11-08", "Las Vegas Grand Prix": "2026-11-21", "Qatar Grand Prix": "2026-11-28",
    "Abu Dhabi Grand Prix": "2026-12-06",
}

race_to_circuit_id = {
    "Australian Grand Prix": "albert_park", "Chinese Grand Prix": "shanghai", "China Sprint": "shanghai",
    "Japanese Grand Prix": "suzuka", "Miami Grand Prix": "miami", "Miami Sprint": "miami",
    "Canadian Grand Prix": "villeneuve", "Canada Sprint": "villeneuve", "Monaco Grand Prix": "monaco",
    "Spanish Grand Prix": "catalunya", "Austrian Grand Prix": "red_bull_ring", "Silverstone Sprint": "silverstone",
    "British Grand Prix": "silverstone", "Belgian Grand Prix - SPA": "spa", "Hungarian Grand Prix": "hungaroring",
    "Dutch Sprint": "zandvoort", "Dutch Grand Prix": "zandvoort", "Italian Grand Prix": "monza",
    "Madrid Grand Prix": "madring", "Azerbaijan Grand Prix": "baku", "Singapore Sprint": "marina_bay",
    "Singapore Grand Prix": "marina_bay", "Circuit of Americas Grand Prix": "americas",
    "Mexican Grand Prix": "rodriguez", "São Paulo Grand Prix": "interlagos", "Las Vegas Grand Prix": "vegas",
    "Qatar Grand Prix": "losail", "Abu Dhabi Grand Prix": "yas_marina",
}