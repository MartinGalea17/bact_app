import json 
import pandas as pd 
import os
import streamlit as st
import re
from difflib import get_close_matches


with open('eucast_gram_neg_preset.json', 'r', encoding='utf-8') as f:
    presets = json.load(f)  # loads the JSON content into a Python list of dicts
    
@st.cache_data
def clean_get_gram_neg(presets):
    names = []
    clinical_groups = []
    neg_site = []
    for entry in presets:
       raw_name = entry.get("name","").strip()
       raw_clinical_group = entry.get("clinical_group","").strip()
       raw_site = entry.get("site", "").strip()
       name = raw_name.lower()
       clinical_group = raw_clinical_group.lower()
       site = raw_site.lower()

       if name not in ["", "n/a"] or clinical_group not in ["", "n/a"]:
            
            names.append(raw_name)
            clinical_groups.append((entry["clinical_group"]).strip())
            neg_site.append(site)
    return names, clinical_groups, neg_site

# Get the cleaned lists
names, clinical_groups, neg_site = clean_get_gram_neg(presets)

# Print them separately
print("[DEBUG]List of valid gram negative names:")
print(names)

print("\n[DEBUG]List of valid gram negative clinical groups:")
print(clinical_groups)
       

with open('eucast_gram_pos_preset.json', 'r', encoding='utf-8') as f:
    pos_presets = json.load(f)  # loads the JSON content into a Python list of dicts
@st.cache_data
def clean_get_gram_pos(pos_presets):
   pos_names =[]
   pos_clinical_groups = []
   pos_site = []
   for entry in pos_presets:
      raw_name = entry.get("name","").strip()
      raw_clinical__group = entry.get("clinical_group","").strip()
      pos_raw_site = entry.get("site", "").strip()
      name = raw_name.lower()
      clinical_group = raw_clinical__group.lower()
      site = pos_raw_site.lower()

      if name not in ("","n/a") or clinical_group not in ("","n/a"):
        pos_names.append(raw_name)
        pos_clinical_groups.append(raw_clinical__group)
        pos_site.append(site)

   return pos_names, pos_clinical_groups, pos_site

pos_names, pos_clinical__groups, pos_site = clean_get_gram_pos(pos_presets)

print("[DEBUG]List of gram positive valid names: ")
print(pos_names)

print("[DEBUG]List of valid gram positive clinical groups")
print(pos_clinical__groups)


classified_data_file = 'bacteria_database_2.xlsx'

@st.cache_data
def get_data_in_classified_data(species_input=None):
    df = pd.read_excel('bacteria_database_2.xlsx')

    df['species'] = df['species'].astype(str).str.strip().str.lower()
    species = df['species'].dropna().unique().tolist()

    df['genus']= df["genus"].astype(str).str.strip().str.lower()
    genus = df["genus"].dropna().unique().tolist()

    df['family']= df["family"].astype(str).str.strip().str.lower()
    family = df["family"].dropna().unique().tolist()
   
    df['clinical_group']= df["clinical_group"].astype(str).str.strip().str.lower()
    clinical_group = df["clinical_group"].dropna().unique().tolist()

    df['gram stain']= df["gram stain"].astype(str).str.strip().str.lower()
    gram_stain = df["gram stain"].dropna().unique().tolist()

    df['cell shape']= df["cell shape"].astype(str).str.strip().str.lower()
    cell_shape = df["cell shape"].dropna().unique().tolist()

    return species,df,genus,family,clinical_group,gram_stain,cell_shape

def match_bacterium_name_to_clinical_group(bacterium_name, df, species):
    bacterium_name = bacterium_name.strip().lower()

    if bacterium_name in species:
        # Ensure both sides are cleaned
        matched_row = df[df['species'].str.strip().str.lower() == bacterium_name]

        # 🔍 Add this line to debug what was matched
        print("[DEBUG] Matched row:\n", matched_row[['species', 'clinical_group']])

        if not matched_row.empty:
            clinical_group = matched_row.iloc[0]['clinical_group']
            print(f"✅ Match found for bacterium: {bacterium_name}, clinical group: {clinical_group}")
            return bacterium_name, clinical_group
        else:
            print(f"⚠️ Found species in list, but no DataFrame row matched it.")
            return bacterium_name, None
    else:
        print(f"❌ No match found for bacterium: {bacterium_name}")
        return None, None


def get_relevant_preset(bacterium_name, clinical_group, sterility_check, mic_disc):
    combined_presets = pos_presets + presets

    # First try matching on species name
    for entry in combined_presets:
        try:
            if bacterium_name in entry["name"].lower() and entry["site"].lower() == sterility_check:
                if mic_disc == "mic" and "antibiotic_strips" in entry:
                    print(f"[DEBUG] Found MIC antibiotics for {bacterium_name}:")
                    return bacterium_name, entry["antibiotic_strips"], sterility_check
                elif mic_disc == "disc" and "antibiotic_discs" in entry:
                    print(f"[DEBUG] Found Disc antibiotics for {bacterium_name}")
                    return bacterium_name, entry["antibiotic_discs"], sterility_check             
                else:
                    print(f"❌ No MIC or disc antibiotics found for {bacterium_name} at {sterility_check}.")
                    return bacterium_name, None, sterility_check
        except KeyError as e:
            print(f"KeyError: {e} in entry: {entry}")

    # Fallback: match on clinical group
    for entry in combined_presets:
        try:
            if clinical_group and entry.get("clinical_group", "").lower() == clinical_group and entry["site"].lower() == sterility_check:
                if mic_disc == "mic" and "antibiotic_strips" in entry:
                    return clinical_group, entry["antibiotic_strips"], sterility_check
                elif mic_disc == "disc" and "antibiotic_discs" in entry:
                    return clinical_group, entry["antibiotic_discs"], sterility_check
                else:
                    print(f"❌ No MIC or disc antibiotics found for clinical group {clinical_group} at {sterility_check}")
        except KeyError as e:
            print(f"KeyError (fallback): {e} in entry: {entry}")

    #possibility to add a final fallback using gram stain and morphology to get a close match

    # Final fallback
    return clinical_group, None, None

#this is a function that will be used to get the brakpoints for the bacterium name or clinical group
@st.cache_data 
def load_all_breakpoints(json_folder='2024_breakpoint_folder'):
    all_data = []
    all_organisms = []
    all_clinical_groups = []
    all_antibiotic_groups = []
    all_names = []

    for filename in os.listdir(json_folder):
     if filename.endswith(".json"):
          file_path = os.path.join(json_folder, filename)

          # Open and load the JSON file
          with open(file_path, 'r', encoding='utf-8') as f:
               try:
                    data = json.load(f)
                    if isinstance(data, dict):
                         data = [data]

                    for entry in data:
                         if isinstance(entry, dict):
                            organisms = entry.get("organisms", [])
                            clinical_group = entry.get("clinical_group","")
                            antibiotic_groups = entry.get("class")
                            names = entry.get("names","")

                            all_organisms.append(organisms)
                            all_clinical_groups.append(clinical_group)
                            all_antibiotic_groups.append(antibiotic_groups)
                            all_names.append(names)


                            all_data.append(entry)
                            print(f"✅ Loaded {filename}")
                         else:
                              print(f"⚠️ Skipped non-dictionary entry in {filename}")

               except json.JSONDecodeError as e:
                    print(f"❌ Error decoding {filename}: {e}")
    return all_data

def get_breakpoints(bacterium_name, all_data, clinical_group=None):
    if not bacterium_name:
        print("[Error] ❌ Bacterium name is None. Skipping breakpoint search.")
        return []
    bacterium_name = bacterium_name.strip().lower()
    clinical_group = clinical_group.strip().lower() if clinical_group else ""

    print(f"[DEBUG] Looking for breakpoints for: {bacterium_name}")
    print(f"[DEBUG] Clinical group: {clinical_group}")

    # Try exact species match first
    for entry in all_data:
        organisms = entry.get("organisms")
        if isinstance(organisms, list):
            for org in organisms:
                if bacterium_name == org.strip().lower():
                    print(f"[DEBUG] ✅ Matched species in list: {org}")
                    return entry
        elif isinstance(organisms, str):
            if bacterium_name == organisms.strip().lower():
                print(f"[DEBUG] ✅ Matched species string: {organisms}")
                return entry

    # Fallback to clinical group if no species matched
    if clinical_group:
        for entry in all_data:
            entry_group = entry.get("clinical_group", "").strip().lower()
            if clinical_group == entry_group:
                print(f"[DEBUG] ✅ Matched by clinical group: {entry_group}")
                return entry

    print(f"[DEBUG] ❌ No breakpoint match found for bacterium: '{bacterium_name}' and clinical group: '{clinical_group}'.")
    return None

def matching_name_input(user_input, species, cutoff = 0.6):
    #function to attempt matchng any input mistakes 
    if not user_input:
        return None 
    user_input = user_input.strip().lower()
    species_str = [str(s) for s in species if isinstance(s, str) or isinstance(s, dict)]
    species_lower = [s.lower() for s in species_str]

    matches = get_close_matches(user_input, species_lower, n=1, cutoff=cutoff)
    if matches:
        #return the first match found
        index = species_lower.index(matches[0])
        return species[index]
    else:
        print(f"❌ No close match found for {user_input}.")
        return None    

def interpret_breakpoint(value, s_crit, r_crit):
    #Function for EUCAST interpretation that handles MIC and disk correctly

    def parse_value(val):
        if val in (None, "", "-", "IE", "NA"):
            return None, None
        if isinstance(val, str):
            match = re.match(r'(<=|>=|≤|≥|<|>|=)?\s*([\d.]+)', val)
            if match:
                op, num_str = match.groups()
                return op or "=", float(num_str)
        try:
            return "=", float(val)
        except (ValueError, TypeError):
            return None, None

    def compare(op, a, b):
        if op in ("≤", "<=", "<"): return a <= b
        if op in ("≥", ">=", ">"): return a >= b
        return a == b

    try:
        num_value = float(value)
    except (ValueError, TypeError):
        return "Invalid breakpoint"

    s_op, s_val = parse_value(s_crit)
    r_op, r_val = parse_value(r_crit)

    if None in (s_val, r_val):
        return "No breakpoint"

    # Disk diffusion if S cutoff is larger than R cutoff
    is_disk = s_val > r_val

    if is_disk:  
        if compare(s_op, num_value, s_val):
            return "Sensitive"
        elif compare(r_op, num_value, r_val):
            return "Resistant"
        else:
            return "Intermediate"
    else:  # MIC
        if compare(s_op, num_value, s_val):
            return "Sensitive"
        elif compare(r_op, num_value, r_val):
            return "Resistant"
        else:
            return "Intermediate"
        
with open('eucast_rules.json', 'r', encoding='utf-8') as f:
    rules = json.load(f)  # loads the JSON content into a Python list of dicts
    print("[DEBUG] ✅ Loaded rules" )
@st.cache_data
# Extract rules as dicts
def get_rules(rules):
    extracted = []
    for entry in rules:
        rule = entry.get("rule")
        organisms = entry.get("organisms", [])
        antibiotics = entry.get("antibiotics", [])
        notes = entry.get("notes", "")
        extracted.append({
            "rule": rule,
            "organisms": organisms,
            "antibiotics": antibiotics,
            "notes": notes
        })
    return extracted

extracted_rules = get_rules(rules)

# Find matching rules
def find_matching_rules(organism_input, extracted, antibiotic_input=None, extracted_rules=extracted_rules):
    organism_input = organism_input.lower()
    if antibiotic_input:
        antibiotic_input = antibiotic_input.lower()

    matches= []
    for entry in extracted:
        if any (organism_input == org.lower () for org in entry["organisms"]): 
            antibiotics_found = [] 
            for ab in entry["antibiotics"]:
                ab_name = ab.get("name","").lower()
                ab_res = str(ab.get("R","")).lower()
                if ab_res == "true":
                    if not antibiotic_input or ab_name == antibiotic_input:
                        antibiotics_found.append({"name": ab_name, "resistant": True})
                        
            if antibiotics_found:
                matches.append({
                    "rule": entry["rule"],
                    "organisms": entry["organisms"],
                    "antibiotics": antibiotics_found,
                    "notes": entry["notes"]
                })
    return matches
     
def process_user_results(result_entry, user_results, mic_or_disc, matches):
    """Process user results with antibiotic breakpoints"""
    interpretations = {}
    breakpoints = result_entry.get("breakpoints", [])
    
    for ab_name, user_val in user_results.items():
        if not str(user_val).strip():
            continue
            
        for bp in breakpoints:
            if bp["antibiotic"].strip().lower() == ab_name.strip().lower():
                try:
                    if mic_or_disc.lower() == "mic":
                        criteria = bp.get("MIC", {})
                        s = criteria.get("S")
                        r = criteria.get("R")
                    else:
                        criteria = bp.get("disk", {}).get("zone_mm", {})
                        s = criteria.get("S")
                        r = criteria.get("R")
                    
                    interpretation = interpret_breakpoint(user_val, s, r)
                    
                    interpretations[ab_name] = {
                        "value": user_val,
                        "S": str(s) if s is not None else "-",
                        "R": str(r) if r is not None else "-",
                        "interpretation": interpretation,
                        "site": bp.get("class", "N/A"),
                        "breakpoints": bp,
                        "warning": False,  # 🚩 default no warning
                        "notes": ""
                    }
                except Exception as e:
                    print(f"Error processing {ab_name}: {str(e)}")
                break
        for ab_name, interp in interpretations.items():         
            for match in matches:
                for ab_rule in match["antibiotics"]:
                    if ab_name.lower() == ab_rule["name"].lower():
                        #check if eucast expected resistance condluics with user result
                        if ab_rule["resistant"] and interp["interpretation"] == "Sensitive":
                            interp["interpretation"] = "R*"
                            interp["notes"] = f"🚩 Ecuast rule: {match["rule"]} → expected resistance"
                        else:
                            interp["notes"] = match.get("notes", "") 
    return interpretations 

def extract_numeric(val):
    """Extract numeric part from breakpoint strings like '≤0.25' or '≥20'."""
    if val in (None, "-", ""):
        return 0.0
    if isinstance(val, str):
        num_str = re.sub(r'[^0-9.]', '', val)
        return float(num_str) if num_str else 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0
