import json 
import pandas as pd 
import os
import streamlit as st
import re
from difflib import get_close_matches
import traceback

antibiotics_to_add = {
    "names": [
        "Benzylpenicillin", "Phenoxymethylpenicillin", "Ampicillin", "Amoxicillin",
        "Cloxacillin", "Flucloxacillin", "Piperacillin", "Ticarcillin",
        "Amoxicillin-clavulanic acid", "Ampicillin-sulbactam", "Piperacillin-tazobactam",
        "Ticarcillin-clavulanic acid", "Cefalexin", "Cefazolin", "Cefuroxime",
        "Cefotaxime", "Ceftriaxone", "Ceftazidime", "Cefepime", "Ceftaroline",
        "Imipenem", "Meropenem", "Ertapenem", "Doripenem", "Aztreonam",
        "Gentamicin", "Tobramycin", "Amikacin", "Netilmicin",
        "Erythromycin", "Clarithromycin", "Azithromycin", "Roxithromycin",
        "Clindamycin", "Tetracycline", "Doxycycline", "Minocycline", "Tigecycline",
        "Vancomycin", "Teicoplanin", "Linezolid", "Tedizolid",
        "Ciprofloxacin", "Levofloxacin", "Moxifloxacin", "Ofloxacin", "Norfloxacin",
        "Trimethoprim", "Sulfamethoxazole", "Trimethoprim-sulfamethoxazole",
        "Colistin", "Polymyxin B", "Rifampicin", "Metronidazole", "Tinidazole",
        "Chloramphenicol", "Fosfomycin", "Nitrofurantoin", "Daptomycin", "Mupirocin",
        "Ceftolozane-tazobactam", "Cefiderocol", "Dalbavancin", "Oritavancin",
        "Quinupristin-dalfopristin", "Spectinomycin", "Kanamycin", "Streptomycin",
        "Telithromycin", "Delafloxacin", "Plazomicin", "Cefotetan", "Cefmetazole","Pefloxacin"
    ]
}

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


classified_data_file = 'updated_database.csv'

@st.cache_data
def get_data_in_classified_data(species_input=None):
    file_path = os.path.join(os.path.dirname(__file__), classified_data_file)
    df = pd.read_csv(file_path)

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
 
def _to_list(val):
    """Normalize a field into a list of cleaned, lowercase strings."""
    if isinstance(val, list):
        return [str(v).strip().lower() for v in val if v is not None and str(v).strip() != ""]
    if isinstance(val, str):
        parts = re.split(r'\s*,\s*', val)
        return [p.strip().lower() for p in parts if p.strip() != ""]
    return []

@st.cache_data

def load_and_normalize_breakpoints(json_folder='2024_breakpoint_folder'):
    """
    Returns normalized_data: list of dicts where fields:
      - 'name','version','group','exclude_name','exclude_group','organism','clinical_group'
      are lists of lowercase strings (possibly empty).
    Each entry still keeps 'breakpoints' list (or may itself be a bp).
    """
    all_data = []
    for filename in sorted(os.listdir(json_folder)):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(json_folder, filename)
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
        except Exception as e:
            print(f"[LOAD ERROR] {filename}: {e}")
            continue
        if isinstance(data, dict):
            data = [data]
        for entry in data:
            if not isinstance(entry, dict):
                print(f"[WARNING] Skipping non-dict entry in {filename}: {repr(entry)[:120]}")
                continue
            # Normalize the scope fields
            for field in ["organism","version","clinical_group","name","group","exclude_name","exclude_group"]:
                entry[field] = _to_list(entry.get(field, ""))
            # keep as-is; breakpoints may be under entry['breakpoints'] or entry may itself be a bp
            all_data.append(entry)
        print(f"✅ Loaded {filename}")
    return all_data

def get_relevant_preset_entry(bacterium_name, clinical_group, sterility_check, mic_or_disc):
    """
    Search combined presets (pos_presets + presets) for:
      1) species-specific entry (entry['name'] contains bacterium_name)
      2) clinical_group match (entry['clinical_group'] == clinical_group)
    Returns the matched entry (the whole preset dict) or None.
    """
    combined = (pos_presets or []) + (presets or [])
    bn = (bacterium_name or "").strip().lower()
    cg = (clinical_group or "").strip().lower()
    sc = (sterility_check or "").strip().lower()
    for entry in combined:
        try:
            entry_site = (entry.get("site","") or "").strip().lower()
        except Exception:
            entry_site = ""
        # check site match if provided (if your presets use site)
        if sc and entry_site and entry_site != sc:
            continue
        # species-name match (entry['name'] might be empty or comma-list)
        names = _to_list(entry.get("name",""))
        if names and bn and bn in names:
            return entry
    # fallback to clinical_group
    for entry in combined:
        try:
            entry_site = (entry.get("site","") or "").strip().lower()
        except Exception:
            entry_site = ""
        if sc and entry_site and entry_site != sc:
            continue
        if (entry.get("clinical_group","") or "").strip().lower() == cg:
            return entry
    return None

select_relevant_entries(normalized_data, bacterium_name, clinical_group):

bn = (bacterium or "").strip().lower()
cg - (clinical_group or "").strip().lower()

organism_entries = []
group_entries = []

for entry in normalized_data:
    if not isininstance(entry,dict):
        continue

#normalize fields 
entry_organisms = _to_list(entry.get("organism",""))
entry_cg = _to_list(entry.get("clinical_group",""))

if entry_organisms:
    if bn in entry_organisms:
        organism_rntries.append(entry)
        continue 
if entry_cg:
    if cg in entry_cg:
        group_entries.append(entry)

#priority decision 
if organism_entries:
    print(f"[SELECT] Using organism-specific entries for '{BN}' ({len(organism_entries)} found")
    return organism_entries,"organism"

if group_entries:
    print(f"[SELECT] Using organism-specific entries for '{cg}' ({len(group_entries)} found")
    return group_entries,"clinical_group"

print (f"[WARNING] No organism or clinical group match found for '{bn}' / '{cg}'")
return [], None 


def get_refined_breakpoints(bacterium_name, preset_antibiotics, normalized_data, clinical_group=None):
    """
    Return dict keyed by lowercase antibiotic name -> breakpoint dict + 'source'.
    Includes:
      ✅ Exact species matches
      ✅ Group/clinical group matches
      ✅ Universal fallbacks (no name/group specified)
    """
    normalized_data = select_relevant_entries(normalized_data,bacterium_name, clinical_group)
    if not bacterium_name or not preset_antibiotics:
        print("[DEBUG] Missing bacterium name or preset_antibiotics")
        return {}

    bn = bacterium_name.strip().lower()
    cg = (clinical_group or "").strip().lower()

    # Normalize preset antibiotic names safely
    preset_lower = []
    for p in preset_antibiotics:
        if isinstance(p, str):
            preset_lower.append(p.strip().lower())
        elif isinstance(p, dict) and "name" in p:
            names = _to_list(p["name"])
            preset_lower.extend(names)

    preset_lower = list(dict.fromkeys(preset_lower))  # preserve order, unique
    print(f"[DEBUG] Query bn='{bn}' cg='{cg}' presets={preset_lower}")

    refined = {}

    # Iterate through normalized EUCAST entries
    for i, entry in enumerate(normalized_data):
        if not isinstance(entry, dict):
            continue

        # Handle entries that contain a list of breakpoints
        bps = entry.get("breakpoints")
        if isinstance(bps, list) and bps:
            parent_scope = entry
        elif "antibiotic" in entry:
            bps = [entry]
            parent_scope = entry
        else:
            continue  # skip malformed entries

        # Pull parent-level fields (used as fallback if bp doesn’t override)
        parent_names = _to_list(entry.get("name", []))
        parent_groups = _to_list(entry.get("group", []))
        parent_clinical = _to_list(entry.get("clinical_group", []))
        parent_ex_names = _to_list(entry.get("exclude_name", []))
        parent_ex_groups = _to_list(entry.get("exclude_group", []))

        # Iterate over breakpoints within the entry
        for bp in bps:
            if not isinstance(bp, dict):
                continue

            ab_raw = bp.get("antibiotic", "")
            ab = str(ab_raw).strip().lower() if ab_raw else ""
            if not ab or ab not in preset_lower:
                continue  # not relevant to the preset

            # Get bp-level or fallback scopes
            bp_names = _to_list(bp.get("name", [])) or parent_names
            bp_groups = _to_list(bp.get("group", [])) or parent_groups
            bp_clinical = _to_list(bp.get("clinical_group", [])) or parent_clinical
            bp_ex_names = _to_list(bp.get("exclude_name", [])) or parent_ex_names
            bp_ex_groups = _to_list(bp.get("exclude_group", [])) or parent_ex_groups

            # Debug output
            print(f"[TRACE] Entry#{i} antibiotic='{ab}' | names={bp_names} | groups={bp_groups} | clinical={bp_clinical}")

            # 1️⃣ Exact species name match
            if bp_names and bn in bp_names and bn not in bp_ex_names:
                refined[ab] = {**bp, "source": f"specific ({', '.join(bp_names)})"}
                print(f"[MATCH] exact name -> {ab} from {bp_names}")
                continue

            # 2️⃣ Group match
            matched_group = False
            if bp_groups:
                if cg and cg in bp_groups:
                    matched_group = True
                else:
                    # Heuristic: genus substring match (e.g., "staph" in "staphylococcus aureus")
                    for g in bp_groups:
                        if g and (g in bn or bn.startswith(g.split()[0])):
                            matched_group = True
                            break

            if matched_group and bn not in bp_ex_names and cg not in bp_ex_groups:
                if ab not in refined:
                    refined[ab] = {**bp, "source": f"group ({', '.join(bp_groups)})"}
                    print(f"[MATCH] group -> {ab} from {bp_groups}")
                continue

            # 3️⃣ Clinical group fallback
            if bp_clinical and cg and cg in bp_clinical:
                if bn not in bp_ex_names and cg not in bp_ex_groups:
                    if ab not in refined:
                        refined[ab] = {**bp, "source": f"clinical_group ({', '.join(bp_clinical)})"}
                        print(f"[MATCH] clinical_group -> {ab} from clinical {bp_clinical}")
                continue

            # 4️⃣ Universal fallback (no restrictions)
            if (not bp_names and not bp_groups and not bp_clinical) and (ab in preset_lower):
                if ab not in refined:
                    refined[ab] = {**bp, "source": "universal (applies to all)"}
                    print(f"[MATCH] universal -> {ab} applies to all")
                continue

    print(f"[DEBUG] Refined results: {list(refined.keys())}")
    return refined


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
     
def process_user_results(user_results, mic_or_disc, matches, refined):
    """Process user results with antibiotic breakpoints (works with dict or list)"""
    interpretations = {}

    for ab_name, user_val in user_results.items():
        if not str(user_val).strip():
            continue

        # Normalize name
        ab_key = ab_name.strip().lower()

        # Handle refined as dict OR list
        bp = None
        if isinstance(refined, dict):
            bp = refined.get(ab_key)
        elif isinstance(refined, list):
            bp = next(
                (entry for entry in refined if str(entry.get("antibiotic", "")).lower() == ab_key),
                None
            )

        if not bp:
            interpretations[ab_name] = {
                "value": user_val,
                "S": "-",
                "R": "-",
                "interpretation": "No breakpoint",
                "site": "N/A",
                "breakpoints": None,
                "warning": True,
                "notes": "No breakpoint found"
            }
            continue

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
                "warning": False,
                "notes": ""
            }
        except Exception as e:
            print(f"[ERROR] proccessing{ab_name} with value {user_val}: {e}")
            traceback.print_exc() #full stack trace in console 
            interpretations[ab_name] = {
                "value": user_val,
                "S": str(s) if 's' in locals() and s is not None else "-",
                "R": str(r) if 'r' in locals() and r is not None else "-",
                "interpretation": "Error",
                "site": bp.get("class", "N/A") if bp else "N/A",
                "breakpoints": bp,
                "warning": True,
                "notes": str(e)
            }

    # Apply EUCAST expected resistance rules
    for ab_name, interp in interpretations.items():
        for match in matches:
            for ab_rule in match.get("antibiotics", []):
                if ab_name.lower() == ab_rule.get("name", "").lower():
                    if ab_rule.get("resistant") and interp["interpretation"] == "Sensitive":
                        interp["interpretation"] = "R*"
                        interp["notes"] = f"🚩 EUCAST rule: {match.get('rule')} → expected resistance"
                    else:
                        interp["notes"] = interp.get("notes", "") or match.get("notes", "")

    return interpretations

def add_additional_antibiotics(bacterium_name, clinical_group, all_data):
#function to add additional antibioptics to the existing presets if possible after checking if they are present in the eucast data sheet
    additional_antibiotics = []
    for entry in all_data:
        if (bacterium_name in entry.get("organisms","").lower() or clinical_group in entry.get("clinical_group","")):
                
            for bp in entry.get("breakpoints", []):
                antibiotic = bp.get("antibiotic")
                if antibiotic and antibiotic not in additional_antibiotics:
                    additional_antibiotics.append(antibiotic)

    return additional_antibiotics

def update_antibiotic_panel(selected, current_panel, organism_name=None, all_data=None):
    """
    Merge selected antibiotics into the current panel.
    Returns updated panel.
    """
    added = []
    skipped = []

    for ab in selected:
        if ab not in current_panel:
            current_panel.append(ab)
            added.append(ab)
        else:
            skipped.append(ab)

    return current_panel, added, skipped

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
