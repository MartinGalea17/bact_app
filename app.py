
import streamlit as st
import re
import json
import pandas as pd
import bcrypt
import plotly
from graph_testing import complete_graph,create_circular_zones
import time
from streamlit_lottie import st_lottie
from test import (
    clean_get_gram_neg,
    clean_get_gram_pos,
    get_data_in_classified_data,
    get_relevant_preset,
    match_bacterium_name_to_clinical_group,
    load_and_normalize_breakpoints, 
    get_refined_breakpoints,
    process_user_results,
    matching_name_input,
    extract_numeric,
    find_matching_rules,
    get_rules,
    get_relevant_preset_entry
    )
from notifications import load_notifications, add_notifications, get_notifications_by_level, delete_notification
logo_image = r"C:\Users\marti\Desktop\code\logo.png" # Path to your logo image

# --- Authentication function ---
def check_login(username, password):
    users = st.secrets["users"]
    if username not in users:
        return False
    stored_hash = users[username]["password"]
    if bcrypt.checkpw(password.encode(), stored_hash.encode()):
        st.session_state["role"] = users[username]["role"]
        return True
    else:
        return False
    
#logout dialog confirmation
@st.dialog("Confirm Logout")
def confirm_logout():
    st.warning("Are you sure you want to logout?👋")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes logout"):
            print("[INFO] User logged out")
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.success("🔒 You have been logged out.")
            st.rerun()
    with col2:
        if st.button("❌ Cancel"):
            st.info("Logout cancelled.")

#confirm delete notification dialog
@st.dialog("Confirm Delete Noification")
def confirm_delete(note):
    st.warning("Are you sure you want to delete this notification?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, delete"):
            if delete_notification(note["id"]):
                st.success(f"Deleted notification: {note['title']}")
                st.rerun()  # only rerun after deletion
    with col2:
        if st.button("❌ Cancel", key=f"cancel_{note['id']}"):
            st.info("Deletion cancelled.")
        

# --- Show App Logic ---
def show_app():
    print("[INFO] Running show_app()")

    # --- Load normalized breakpoint data ---
    json_folder = "2024_breakpoint_folder"  # adjust path if needed
    all_data = load_and_normalize_breakpoints(json_folder=json_folder)
    print(f"[DEBUG] Loaded {len(all_data)} normalized breakpoint entries from {json_folder}")

    # --- Load classified bacterial data ---
    species, df, genus, family, clinical_group, gram_stain, cell_shape = get_data_in_classified_data()
    print("[DEBUG] Loaded classified bacterial data")

    # --- Load Gram-negative presets ---
    with open('eucast_gram_neg_preset.json', 'r', encoding='utf-8') as f:
        presets = json.load(f)
        print("[DEBUG] Loaded Gram-negative presets")

    names, clinical_groups, neg_site = clean_get_gram_neg(presets)
    unique_names = sorted(set(names))
    unique_groups = sorted(set(clinical_groups))
    unique_neg_site = sorted(set(neg_site))
    print(f"[DEBUG] Gram-negative sites: {unique_neg_site}")

    # --- Load Gram-positive presets ---
    with open('eucast_gram_pos_preset.json', 'r', encoding='utf-8') as f:
        pos_presets = json.load(f)
        print("[DEBUG] Loaded Gram-positive presets")

    pos_names, pos_clinical_groups, pos_site = clean_get_gram_pos(pos_presets)
    unique_pos_names = sorted(set(pos_names))
    unique_pos_groups = sorted(set(pos_clinical_groups))
    unique_pos_site = sorted(set(pos_site))
    print(f"[DEBUG] Gram-positive sites: {unique_pos_site}")

    # --- Load rules ---
    with open('eucast_rules.json', 'r', encoding='utf-8') as f:
        rules = json.load(f)
        print("[DEBUG] ✅ Loaded EUCAST rules")
    extracted_rules = get_rules(rules)

    container = st.container(border=True)
    container.title('🧫 Bacteriology helper APP')
    container.markdown(
        "Welcome to the Bacterial Antibiotic Susceptibility App! "
        "This app helps you find the relevant antibiotic susceptibility data for various bacteria. "
        "Please select a section from the dropdown list below to get started.")

    # --- Sidebar for navigation ---
    with st.sidebar:
        st.sidebar.image(logo_image,width=150)
        st.sidebar.title(" ☰  MENU")
        st.sidebar.write("Use the menu below to navigate:")
        user_menu = st.sidebar.selectbox("Select a section", ["-- Select --","🥼Account", "🔐logout"])
        print(f"[DEBUG] User menu selection: {user_menu}")
        
    if st.session_state.get("role") == "admin" and user_menu == "🥼Account":
        st.subheader("👨‍💻 Admin section")
        print("[DEBUG] Admin section accessed")

        user_info_container = st.container(border=True)
        with user_info_container:
            if st.session_state.get("logged_in", False):
                st.success(f"🔓 Logged in as {st.session_state.username}")
                tab1,tab2,tab3 = st.tabs(["🔔Manage Notifications", "⚙️Settings", "👥Users"])
            
                with tab1:
                    st.subheader("Manage Notifications")
                    with st.form("add_notification_form"):
                        with st.container(border = False): 
                            col1, col2 = st.columns(2)
                        with col1:
                            title = st.text_input("Enter Title")
                        with col2:
                            level = ["🚨High","⚠️Medium","📢Low"]
                            notification_level = st.selectbox("Notification level", level)
                        main_info = st.text_area("Input notification")
                        notification = st.form_submit_button("Submit notification")

                    if notification and notification_level: 
                        if title and main_info:
                            add_notifications(title, main_info, notification_level, author="Admin")
                            st.success("✅ Notification added successfully")
                            st.rerun()  # only rerun after adding notification
                        else: 
                            st.error("⚠️ Please fill all fields")

                            # Display existing notifications
                    st.divider()
                    st.subheader("📜 Existing Notifications")

                    notifications = load_notifications()

                    if notifications:  # only loop if there are notifications
                        for note in notifications:
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.write(f"{note['title']} - {note['level']}")
                                st.write(note["message"])
                            with col2:
                                if st.button("🗑 Delete", key=f"delete_{note['id']}"):
                                    confirm_delete(note)
                    else:
                        st.info("No notifications available.")
                with tab2:
                    st.subheader("Settings")
                    st.info("Admin settings will go here")

                with tab3: 
                    st.subheader("Users")
                    st.info("User mangement will go here ")
            else:
                st.warning("You are not logged in.")

    
    elif st.session_state.get("role") == "user" and user_menu == "🥼Account":
        st.subheader("👤 User Section")
        if st.session_state.get("logged_in", False):
            st.success(f" 👤 Logged in as {st.session_state.get('username')}")
        else:
            st.warning("You are not logged in.")
    
    elif user_menu == "🔐logout":
        if st.button("Logout"):
            confirm_logout()
        
    # --- Main application sections ---
    option = st.sidebar.selectbox("Select a section", ["-- Select --", "🧪 Antibiotic lookup/ Sensitivites", "🦠 Bacteria Lookup", "🔔Notifications"])
    print(f"[DEBUG] Selected option: {option}")

    if option == "🧪 Antibiotic lookup/ Sensitivites":
        container1 = st.container(border=True)
        container1.header("Antibiotic Preset & Sensitivity Section")
        container1.markdown(
            "This section provides antibiotic preset information for various bacteria and automatic antibiotic results. "
            "Please select from the following tabs.")
        tab1, tab2,tab3= container1.tabs(["🔍 AST preset lookup", "💊Antibiotic Sensitivities","🧐 Panel verification"])

        with tab1:
            container2 = st.container(border=True)
            container2.header("📋 Antibiotic Presets lookup module")
            left, middle, right, last = st.columns(4, vertical_alignment="center")

            with middle:
                gram_type = st.radio("Filter by Gram", ["Gram Positive 🟣", "Gram Negative 🔴"])
                print(f"[DEBUG tab1] Filter choosen is {gram_type}")
            with right:
                search_type = st.radio("Search by", ["Species Name", "Clinical Group"])
                print(f"[DEBUG tab1] Filter choosen is {search_type}")
            with last:
                sterility_check = st.radio("Filter by", ["Sterile", "Urine", "❔ Other", "Eye-swab"])
                print(f"[DEBUG tab1] Filter choosen is {sterility_check}")

            with left:
                with left:
                    species_clinical_dynamic_input = ""

                # Map sterility check to lowercase site key
                    site_map = {"Sterile": "sterile", "Urine": "urines", "❔ Other": "other", "Eye-swab":"eye swab"}
                    input_site = site_map.get(sterility_check, "").lower()
                    print(f"[DEBUG] input_site = '{input_site}'")

                    if gram_type == "Gram Positive 🟣" and search_type == "Species Name":
                        filtered_names = sorted({
                            e.get("name", "").strip()
                            for e in pos_presets
                            if e.get("site", "").strip().lower() == input_site and e.get("name", "").strip()})
                        species_clinical_dynamic_input = st.selectbox("Enter Species Name", filtered_names)

                    elif gram_type == "Gram Positive 🟣" and search_type == "Clinical Group":
                        filtered_groups = sorted({
                            e.get("clinical_group", "").strip()
                            for e in pos_presets
                            if e.get("clinical_group", "").strip().lower() not in ("", "n/a") and (not input_site or e.get("site","").strip().lower() == input_site)
                        })
                        species_clinical_dynamic_input = st.selectbox("Enter Clinical Group", filtered_groups)

                    elif gram_type == "Gram Negative 🔴" and search_type == "Species Name":
                        filtered_names = sorted({
                            e.get("name", "").strip()
                            for e in presets
                            if e.get("site", "").strip().lower() == input_site and e.get("name", "").strip()})
                        species_clinical_dynamic_input = st.selectbox("Enter Species Name", filtered_names)

                    elif gram_type == "Gram Negative 🔴" and search_type == "Clinical Group":
                        filtered_groups = sorted({
                            e.get("clinical_group", "").strip()
                            for e in presets
                            if e.get("site", "").strip().lower() == input_site and e.get("clinical_group", "").strip().lower() not in ("", "n/a")})
                        species_clinical_dynamic_input = st.selectbox("Enter Clinical Group", filtered_groups)

            print(f"[DEBUG tab1] Input selected: {species_clinical_dynamic_input}")
            main_antibiotic_presets_container = st.container(border=False)
            main_antibiotic_presets_container.subheader("This section provides antibiotic presets for various bacteria. Please select from the options below.")

            with main_antibiotic_presets_container:
                site_map = {"Sterile":"sterile",
                            "Urine":"urines",
                            "❔ Other":"other",
                            "Eye-swab":"eye swab"}
                input_site = site_map.get(sterility_check,"").lower()

                target_presets = pos_presets if gram_type == "Gram Positive 🟣" else presets
                selected_preset = get_relevant_preset_entry(
                bacterium_name=species_clinical_dynamic_input.strip().lower() if search_type == "Species Name" else "",
                clinical_group=species_clinical_dynamic_input.strip().lower() if search_type == "Clinical Group" else "",
                sterility_check=input_site,
                mic_or_disc=st.session_state.get("mic_disc_filter", "MIC").lower())

                if selected_preset:
                    st.success(f"✅ Found preset for {species_clinical_dynamic_input}")
                    st.json(selected_preset)
                else:
                    st.warning(f"❌ No preset found for {species_clinical_dynamic_input} and {sterility_check}. Please check your input or try a different search type.")

        with tab2:
            # Top filters
            with st.form("global_filters", clear_on_submit=False):
                st.header("🎛️ Shared filters")

                col1, col2, col3, col4 = st.columns(4, vertical_alignment="center")
                with col1:
                     mic_disc = st.radio("Select MIC or Disc", ["MIC", "Disc"],key="mic_disc_filter",horizontal=False)
                     print(f"[DEBUG tab 2] Filter choosen is {mic_disc}")
                with col2:
                    sterility = st.radio("Filter by", ["Sterile", "Urine", "Other"],key="sterility_type")
                    print(f"[DEBUG tab 2] Filter choosen {sterility}")
                with col3:
                    site = st.selectbox("Select a section", ["-- Select --", "Normal", "❤️ Endocarditis", "🧠CSF"],key="infection_site_filter")
                with col4:
                    date = st.selectbox("Select Eucast date", ["-- Select --", "2021", "2024", "2025"],key="eucast_date_filter")

                submitted_filters = st.form_submit_button("Apply Filters")

                if submitted_filters:
                    st.success(f"✅ Applied filters → "
                    f"MIC/Disc: {st.session_state.mic_disc_filter}, "
                    f"Sterility: {st.session_state.sterility_type}, "
                    f"Site: {st.session_state.infection_site_filter}, "
                    f"Date: {st.session_state.eucast_date_filter}")


                    #defaullts for organism states only 
            default_session_states = {
                "left_name_input":"",
                "right_name_input":"",
                "bact_name_left": "",
                "bact_name_right":"",
                "clinical_group_left":"",
                "clinical_group_right":"",
                "antibiotics_left": [],
                "antibiotics_right": [],
                "left_user_result": {},
                "right_user_result": {},
                "left_submitted": False,
                "right_submitted": False,
                "sterility_type": "",
                "mic_disc_filter": "",}

            for key, val in default_session_states.items():
                if key not in st.session_state:
                    st.session_state[key] = val 


            input_results_container = st.container(border=True)
            with input_results_container:     
                left, right = st.columns(2, vertical_alignment="top")
                # --- Organism A input section ---
                with left:
                    with st.form(key='left_organism_form'):
                        st.subheader("🦠 Organism A")

                        # Input for organism name
                        left_name_input = st.text_input("Enter Organism Name:", key="left_name_input")

                        if st.form_submit_button("📤Submit"):
                            matched_left_input = None
                            clinical_group_left = None

                            with st.status("Matching organism A...") as status:
                                st.write("Relax dude, this will not take long")
                                time.sleep(1)

                            if left_name_input.strip():
                                print(f"[DEBUG] Processing left organism: {left_name_input}")

                                # Load species and df
                                species, df, *_ = get_data_in_classified_data()

                                # Match partial input
                                matched_left_input = matching_name_input(left_name_input, species) or left_name_input

                                # Match to clinical group
                                bact_name_left, clinical_group_left = match_bacterium_name_to_clinical_group(
                                    matched_left_input, df, species)

                                # Get relevant preset panel (new logic fully integrated)
                                _, antibiotics_left, _ = get_relevant_preset(
                                    bacterium_name=bact_name_left if bact_name_left else matched_left_input.strip().lower(),
                                    clinical_group=clinical_group_left.strip().lower() if clinical_group_left else "",
                                    sterility_check=st.session_state["sterility_type"].strip().lower(),
                                    mic_disc=st.session_state["mic_disc_filter"].strip().lower())

                                # Save to session state before rerun
                                st.session_state["bact_name_left"] = bact_name_left
                                st.session_state["clinical_group_left"] = clinical_group_left
                                st.session_state["antibiotics_left"] = antibiotics_left or []
                                st.session_state["matched_left_input"] = left_name_input

                                status.update(label="Done matching organism A")
                                st.rerun()

                                # Show matched info
                                st.success(f"✅ Matched species: {bact_name_left} with {clinical_group_left} clinical group")
                                print(f"[DEBUG] Matched left input: {matched_left_input} with clinical group {clinical_group_left}")

                            else:
                                st.warning("❌ Please enter a valid organism name before submitting.")
                                print(f"[DEBUG] Matched left input: {matched_left_input} with clinical group {clinical_group_left}")

                     # --- Antibiotic input container ---
                    if "antibiotics_left" in st.session_state:
                        with st.container(border=True):
                            if st.session_state.antibiotics_left:
                                st.success(f"✅ Found preset for {st.session_state.bact_name_left} ({st.session_state.mic_disc_filter.upper()}):")

                                if "left_user_result" not in st.session_state:
                                    st.session_state.left_user_result = {}

                                temp_results = {}
                                # Create input fields for each antibiotic
                                for antibiotic in st.session_state.antibiotics_left:
                                    left_raw_value = st.session_state.left_user_result.get(antibiotic, "")
                                    result = st.text_input(f"Enter result for {antibiotic}:", value=str(left_raw_value), key=f"left_res_{antibiotic}")
                                    temp_results[antibiotic] = result

                                if st.button("📤 Submit Left Results"):
                                    st.session_state.left_user_result = temp_results
                                    st.session_state.left_submitted = True
                                    st.rerun()
                            else:
                                st.warning(f"❌ No preset found for {st.session_state.bact_name_left} (clinical group: {st.session_state.clinical_group_left})")
                    else:
                        st.info("ℹ️ Please enter a bacterial species to begin.")

                # --- Results Interpretation Section ---
                with right:
                        header_left = st.container(border=True)
                        with header_left:
                            st.header("📄Results")

                        interpretation_container_left = st.container()
                    
                        if st.session_state.left_submitted:
                            with interpretation_container_left:
                                final_results = {k.replace("left_", ""): v 
                                                for k, v in st.session_state.left_user_result.items() 
                                                if v.strip()}
                                with st.status("Processing left-side results...") as status:
                                    st.write("Relax dude this will not take long")
                                    time.sleep(1)

                                    bact_left = st.session_state.get("bact_name_left")
                                    group = st.session_state.get("clinical_group_left")
              
                                    if not bact_left:
                                        st.error(f"❌ Bacterium name not found for: {st.session_state.get('left_name_input')}. Please check your input.")
                                    else:
                                        st.success(f"✅ Results recorded for {bact_left}:")
                                        refined_bps = get_refined_breakpoints(
                                            bacterium_name=bact_left,
                                            preset_antibiotics=st.session_state["antibiotics_left"],
                                            normalized_data=all_data,
                                            clinical_group=group)

                                if refined_bps:
                                    matches_left = find_matching_rules(st.session_state["bact_name_left"], extracted_rules)
                                    interpretations_left = process_user_results(final_results,st.session_state["mic_disc_filter"],matches_left,refined_bps)
                                    for ab, info in interpretations_left.items():
                                        # Add color coding for interpretation
                                        color = "green" if info['interpretation'] == "Sensitive" else "orange" if info['interpretation'] == "Intermediate" else "red"
                                        st.markdown(f"<p><b>🔬 {ab} ({info['site']})</b><br>"f"User Value: {info['value']}| S: {info['S']} | R: {info['R']}<br>"
                                        f"<span style='color:{color}; font-weight:bold;'>➤ {info['interpretation']}</span></p>",unsafe_allow_html=True)
                                        
                                        #display rules
                                        if "notes" in info and info["notes"]:
                                            for note in info ["notes"] if isinstance(info["notes"], list) else [info["notes"]]:

                                                st.markdown(f"<span style='color:orange;'>⚠ {note}</span>", unsafe_allow_html=True)

                                        print(f"[DEBUG for color] Interpretation for {ab}: '{info['interpretation']}'")
                                        print(f"[DEBUG] {ab}: {info}")


                                        with st.expander(f"Further info for {ab}"):
                                            st.write(f"🔬 {ab} ({info['site']})")
                                            st.write(f"User Value: {info['value']}")
                                            st.write(f"Eucast INPUT DATE breakpoints:")
                                            st.write(f"Interpretation: {info['interpretation']}")
                                            if st.session_state['mic_disc_filter'] == 'MIC':
                                            # create MIC graph

                                                graph = complete_graph(
                                                    ab_name=ab,
                                                    s_val=extract_numeric(info["S"]),
                                                    r_val=extract_numeric(info["R"]),
                                                    user_val=extract_numeric(info["value"]),
                                                    test_type="mic")
                                            else:
                                            # create disk graph
                                                st.write("Disk interpretations.")
                                                graph = create_circular_zones(
                                                    ab_name2=ab,
                                                    s_val2=extract_numeric(info["S"]),
                                                    r_val2=extract_numeric(info["R"]),
                                                    user_val2=extract_numeric(info["value"]))

                                            st.plotly_chart(graph, use_container_width=True)
                                       
                                    st.success("✅ Left-side results processed successfully!")       
                                    st.session_state.left_user_result = {}
                                    status.update(label="Left-side results processed successfully")
                                else:
                                    st.warning("❌ No breakpoints found for this organism")
                                    st.session_state.left_user_result = {}
            with tab3:      
                st.header("Panel Verification")
                st.subheader("This section will allow you to verify your panels against the presets and rules.")
                st.warning("This section is under development. Please check back later.")

                with st.container(border=True):
                    left, right = st.columns(2, vertical_alignment="top")
                    with left:
                        st.subheader("Input Panel Image", help="Use your device camera to take a picture of the antibiotic panel.")
                        enable_camera = st.checkbox("Enable Camera 📷")
                        picture = st.camera_input("Take a picture of the panel", disabled = not enable_camera)

                        if picture:
                            st.image(picture, caption="Panel Image")

                    with right:
                        st.subheader("Results")
                        st.info("Panel verification results here")
                    


    elif option == "🦠 Bacteria Lookup":
        lookup_container = st.container(border=True)
        filter_container = st.container(border=True)

        lookup_container.header("🔬 Bacteria Lookup Module")
        lookup_container.write("Look up Gram stain, enzymes, resistance genes, etc.")

        with filter_container:
            filter_options = ["Species", "Genus", "Family"]
            selected_filters = st.segmented_control("Filter by", filter_options, selection_mode="multi")

        st.markdown(f"Your selections are: {', '.join(selected_filters)}")
        print(f"[DEBUG] Lookup filters selected: {selected_filters}")

        if "Species" in selected_filters:
            species_filter_container = st.container(border=True)
            with species_filter_container:
                st.subheader("🔍 Search by Species Name")
                species_input = st.text_input("Enter species name to filter:", key="species").strip().lower()
                if species_input:
                    matched_df = df[df['species'] == species_input]
                    if not matched_df.empty:
                        st.success(f"✅ Found species: {species_input}")
                        st.dataframe(matched_df)
                    else:
                        st.warning(f"❌ '{species_input}' not found in the database.")

        if "Genus" in selected_filters:
            genus_input = st.text_input("Enter genus name to filter:", key="genus").strip().lower()
            if genus_input:
                matched_df = df[df['genus'] == genus_input]
                if not matched_df.empty:
                    st.success(f"✅ Found genus: {genus_input}")
                    st.dataframe(matched_df)
                else:
                    st.warning(f"❌ '{genus_input}' not found in the database.")

        if "Family" in selected_filters:
            family_input = st.text_input("Enter family name to filter:", key="family_filter").strip().lower()
            if family_input:
                matched_df = df[df['family'] == family_input]
                if not matched_df.empty:
                    st.success(f"✅ Found family: {family_input}")
                    st.dataframe(matched_df)
                else:
                    st.warning(f"❌ '{family_input}' not found in the database.")

    elif option == "🔔Notifications":
        notifications = load_notifications() # to read the notifications from the json file
        new_notification_container = st.container(border=True)
        with new_notification_container:
            st.title("🔔Notifications")
            high,medium,low = st.tabs(["🚨High","⚠️Medium","📢Low"])
        with high:
            highs = [n for n in notifications if n["level"] == "🚨High"]
            if not highs:
                st.info("No high priority notifications")
            for n in sorted(highs, key=lambda x: x["timestamp"], reverse=True):
                st.markdown(f"**{n['title']}** ({n['timestamp']})")
                st.write(n["message"])
                st.divider()
                        
        with medium: 
            mediums = [n for n in notifications if n["level"] == "⚠️Medium"]
            if not mediums:
                st.info("No medium priority notifications")
            for n in sorted(mediums, key=lambda x: x["timestamp"], reverse=True):
                st.markdown(f"**{n['title']}** ({n['timestamp']})")
                st.write(n["message"])
                st.divider()
                        
        with low:
            lows = [n for n in notifications if n["level"] == "📢Low"]
            if not lows:
                st.info("No low priority notifications")
            for n in sorted(lows, key=lambda x: x["timestamp"], reverse=True):
                st.markdown(f"**{n['title']}** ({n['timestamp']})")
                st.write(n["message"])
                st.divider()
                
    st.sidebar.markdown("Developed by Martin Galea, version 1.0")

# --- App Entry Point ---
if not st.session_state.get("logged_in", False):
    print("[INFO] Showing login form")
    

    left_spacer, main, right_spacer = st.columns([1,2,1])
    with main:
        st.header("Bacteriology helper app")
        with st.container(border=False,width=900,height="content", horizontal_alignment="center"):
            
            left, right = st.columns([1, 1], vertical_alignment="center")
            
            with left:
                st.image(logo_image,width=150)   # Display logo on login page
            
            with right:
                st.subheader("🔐 Login to Access the App")
            
            with st.form("login_form"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    submitted = st.form_submit_button("Login")

        if submitted:
            users = st.secrets["users"]
            matched_user = None
            for key, user in users.items():
                if username == user.get("username"):
                    matched_user = user
                    break
            print(f"[DEBUG] Login submitted with username: {username}")
            if check_login(username, password):
                # Initialize all session state variables HERE after successful login
                st.session_state.update({
                    "logged_in": True,
                    "username": username,
                    "left_submitted": False,
                    "right_submitted": False,
                    "left_user_result": {},
                    "right_user_result": {},
                    "bact_name_left": "",
                    "clinical_group_left": "",
                    "antibiotics_left": [],
                    "bact_name_right": "",
                    "clinical_group_right": "",
                    "antibiotics_right": []
                })
                st.success(f"✅ Welcome, {username}!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
else:
    # Ensure all variables exist (in case of page refresh)
    default_state = {
        "left_submitted": False,
        "right_submitted": False,
        "left_user_result": {},
        "right_user_result": {},
        # Other variables...
    }
    for key, value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = value
    print('[Info] user {st.session_state.username} is logged in, showing app')
    show_app()
