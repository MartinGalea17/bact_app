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

#logic for Haeinf
cefinase_input = int(input("Enter cefinase test result (1 for positive, 0 for negative): "))
penicillin_input = int(input("Enter penicillin test result: "))

def cefinase_test(cefinase_input):
    if cefinase_input == 1:
        print("DEBUG: cefinase_input is 1, Beta-lactamase detected")
        return "BLPR"
    elif cefinase_input == 0:
        print("DEBUG: cefinase_input is 0, No Beta-lactamase detected")
        return "No enzyme"
    else:
        print("DEBUG: Invalid input for cefinase test")
        return "Invalid input for cefinase test. Please enter 1 for positive or 0 for negative."
    
def penicillin_test(penicillin_input):
    if penicillin_input >=12:
        print("DEBUG: penicillin_input is greater than or equal to 12 indicating no resistance mechanism")
        return "Screen negative"
    elif penicillin_input <12:
        print("DEBUG: penicillin_input is less than 12 indicating a resistance mechanism")
        return "Screen positive"
    else:
        print("DEBUG: Invalid input for penicillin test")
        return "Invalid input for penicillin test. Please enter a valid number."

def haeinf_logic(cefinase_input, penicillin_input):

    if penicillin_input ≥ 12:
        return hinf_messages # no mechansim detected. no furthur testing 
    
    #below this line resistance exists 
    # showing the first resistance messages 
    print (f" cefinase_input {cefinase_input} and penicillin {penicillin_input}")
    hinf_resistance_detected = hinf_messages["hinf_mechanism_detected"]

    
    

    cef_result = cefinase_test(cefinase_input)
    pen_result = penicillin_test(penicillin_input)



###    
ox = int(input("Enter oxacillin test result: "))
pen = float(input("Enter penicillin test result: "))
sample_type = input("Enter sample type (e.g., endocarditis, meningitis, other): ")

print(pneumo_logic(ox, pen, sample_type))
###

