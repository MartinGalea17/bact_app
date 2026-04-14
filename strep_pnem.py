import json 
import streamlit as st
import os

#load resistance patterns from JSON files in the "resistance_patterns" folder and cache the results to improve performance
@st.cache_data
def load_resistance_patterns(folder_path="resistance_patterns"):
    patters = {}
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            filepath = os.path.join(folder_path, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                pattern_data = json.load(f)

                organism_names = pattern_data["name"].strip().lower()
                patters[organism_names] = pattern_data
    return patters

#strep pneumo logic
def pneumo_logic(ox, pen, sample_type, messages, pen_disc=None):
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
    
    # Benzylpenicillin disc required
    pen_disc = int(input("Enter benzylpenicillin disc zone: "))
    if pen_disc >= 14:
        pen_disc_result = messages["benzylpen_I"]
        print(f"DEBUG: penicillin disc input {pen_disc}")
    else:
        pen_disc_result = messages["benzylpen_R"]
    
    # STEP 3 — Other indications
    if 9 <= ox <= 19:
        other_ab_messages = messages["oxacillin_9_19"]

    if ox < 9:
        other_ab_messages = messages["oxacillin_less_9"]
    
    return resistance_detected + pen_disc_result + "\n" + other_ab_messages
    
#logic for Haeinf
with open("resistance_patterns/h_inf.json") as f:
    hinf_messages = json.load(f)

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


def haeinf_logic(cefinase_input, penicillin_input, hinf_messages,beta_lactam, Aug_input):

    if penicillin_input >= 12:
        return hinf_messages["hinf_no_mechanism_detected"]
    
    #below this line resistance exists 
    # showing the first resistance messages 
    print (f" cefinase_input {cefinase_input} and penicillin {penicillin_input}")
    hinf_resistance_detected = hinf_messages["hinf_mechanism_detected"]

    #beta lacamase testing 
    if beta_lactam == 1:
        beta_lactam_message_pos = hinf_messages["hinf_beta_lactam_pos"]

    if Aug_input >= 15:
        AUG_more = hinf_messages["hinf_Aug_>15"]
    else:
        AUG_less =  hinf_messages["hinf_Aug_<15"]
    
    if beta_lactam == 0:
        beta_lactam_message_neg = hinf_messages["hinf_beta_lactam_neg"]
    
    return hinf_resistance_detected + "\n" + beta_lactam_message_pos + "\n" + AUG_more + "\n" + beta_lactam_message_neg + "\n" + AUG_less



#esbl logic 

def esbl_logic():
    pass 
