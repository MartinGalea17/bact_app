import json 

with open("resistance_patterns/strep_pneumoniae.json") as f:
    messages = json.load(f)

def pneumo_logic(ox, pen, sample_type):
    sample_type = sample_type.lower()
    

    # STEP 1 — Screen for resistance mechanism
    if ox >= 20 or pen <= 0.06:
        return messages["screen_susceptible"]
    
    # Everything below this line assumes resistance exists
    #step 2 — Resistance mechanism detected
    print(f"DEBUG: oxacillin input {ox}, penicillin input {pen}")
    resistance_detected = messages["mechanism_detected"] + "\n"

    # STEP 3 — Indication-specific reporting

    if sample_type in ["endocarditis", "meningitis"]:
        return resistance_detected + messages["meningitis_resistant"]

    # STEP 3 — Other indications
    if 9 <= ox <= 19:
        return resistance_detected + messages["oxacillin_9_19"]

    if ox < 9:
        return resistance_detected + messages["oxacillin_less_9"]
    # Benzylpenicillin disc required
    pen_disc = int(input("Enter benzylpenicillin disc zone: "))
    if pen_disc >= 14:
        return resistance_detected + messages["benzylpen_I"]
    else:
        return resistance_detected +messages["benzylpen_R"]

   

    
ox = int(input("Enter oxacillin test result: "))
pen = float(input("Enter penicillin test result: "))
sample_type = input("Enter sample type (e.g., endocarditis, meningitis, other): ")
print(pneumo_logic(ox, pen, sample_type))