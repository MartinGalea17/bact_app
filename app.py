import streamlit as st
import json
import pandas as pd
import bcrypt
import plotly
from streamlit_lottie import st_lottie
from test import (
    clean_get_gram_neg,
    clean_get_gram_pos,
    get_data_in_classified_data,
    get_relevant_preset,
    match_bacterium_name_to_clinical_group,
    load_all_breakpoints, 
    get_breakpoints,
    process_user_results
)

# --- Authentication function ---
def check_login(username, password):
    try:
        hashed_pw = st.secrets["users"][username]
        hashed_pw = "".join(hashed_pw.split())
        print(f"[DEBUG] Checking login for user: {username}")
        return bcrypt.checkpw(password.encode(), hashed_pw.encode())
    except KeyError:
        st.warning("Username not found.")
        print(f"[ERROR] Username '{username}' not found in secrets")
        return False


# --- Show App Logic ---
def show_app():
    print("[INFO] Running show_app()")
# Load data once at the top
    all_data = load_all_breakpoints()

    # Load assets
    with open("animated_logo.json", "r") as f:
        lotties_json = json.load(f)

    species, df, genus, family, clinical_group, gram_stain, cell_shape = get_data_in_classified_data()
    print("[DEBUG] Loaded classified data")

    with open('eucast_gram_neg_preset.json', 'r', encoding='utf-8') as f:
        presets = json.load(f)
        print("[DEBUG] Loaded gram-negative presets")

    names, clinical_groups = clean_get_gram_neg(presets)
    unique_names = sorted(set(names))
    unique_groups = sorted(set(clinical_groups))

    with open('eucast_gram_pos_preset.json', 'r', encoding='utf-8') as f:
        pos_presets = json.load(f)
        print("[DEBUG] Loaded gram-positive presets")

    pos_names, pos_clinical_groups = clean_get_gram_pos(pos_presets)
    unique_pos_names = sorted(set(pos_names))
    unique_pos_groups = sorted(set(pos_clinical_groups))

    container = st.container(border=True)
    container.title('🧫 Bacteriology helper APP')
    container.markdown(
        "Welcome to the Bacterial Antibiotic Susceptibility App! "
        "This app helps you find the relevant antibiotic susceptibility data for various bacteria. "
        "Please select a section from the dropdown list below to get started."
    )

    with st.sidebar:
        st_lottie(lotties_json, speed=1, reverse=False, loop=True, quality="high", height=100, width=100)
        st.sidebar.title(" ☰   MENU")
        st.sidebar.write("Use the menu below to navigate:")
        user_info = st.sidebar.selectbox("User Info", ["-- Select --", "🔑 Login", "logout", "👤 User Info"])

        if user_info == "👤 User Info":
            user_info_container = st.container(border=True)
            with user_info_container:
                if st.session_state.get("logged_in", False):
                    st.success(f"🔓 Logged in as {st.session_state.username}")
                else:
                    st.warning("You are not logged in.")

        if user_info == "logout":
            if st.button("Logout"):
                print("[INFO] User logged out")
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.success("🔒 You have been logged out.")
                st.rerun()

    option = st.sidebar.selectbox("Select a section", ["-- Select --", "🧪 Antibiotic lookup/ Sensitivites", "🦠 Bacteria Lookup"])
    print(f"[DEBUG] Selected option: {option}")

    if option == "🧪 Antibiotic lookup/ Sensitivites":
        container1 = st.container(border=True)
        container1.header("Antibiotic Preset & Sensitivity Section")
        container1.markdown(
            "This section provides antibiotic preset information for various bacteria and automatic antibiotic results. "
            "Please select from the following tabs."
        )
        tab1, tab2 = container1.tabs(["🔍 AST preset lookup", "💊Antibiotic Sensitivities"])

        with tab1:
            container2 = st.container(border=True)
            container2.header("📋 Antibiotic Presets Module")
            left, middle, right, last = st.columns(4, vertical_alignment="center")

            with middle:
                gram_type = st.radio("Filter by Gram", ["Gram Positive 🟣", "Gram Negative 🔴"])
            with right:
                search_type = st.radio("Search by", ["Species Name", "Clinical Group"])
            with last:
                sterility_check = st.radio("Filter by sterility", ["Sterile", "Urine", "❔ Other"])

            with left:
                species_clinical_dynamic_input = ""
                if gram_type == "Gram Positive 🟣" and search_type == "Species Name":
                    species_clinical_dynamic_input = st.selectbox("Enter Species Name", unique_pos_names)
                elif gram_type == "Gram Positive 🟣" and search_type == "Clinical Group":
                    species_clinical_dynamic_input = st.selectbox("Enter Clinical Group", unique_pos_groups)
                elif gram_type == "Gram Negative 🔴" and search_type == "Species Name":
                    species_clinical_dynamic_input = st.selectbox("Enter Species Name", unique_names)
                elif gram_type == "Gram Negative 🔴" and search_type == "Clinical Group":
                    species_clinical_dynamic_input = st.selectbox("Enter Clinical Group", unique_groups)
                else:
                    st.warning("Please select a Gram type and search type to proceed.")

            print(f"[DEBUG] Input selected: {species_clinical_dynamic_input}")
            main_antibiotic_presets_container = st.container(border=True)
            main_antibiotic_presets_container.subheader("This section provides antibiotic presets for various bacteria. Please select from the options below.")

            with main_antibiotic_presets_container:
                target_presets = pos_presets if gram_type == "Gram Positive 🟣" else presets
                selected_preset = None
                if species_clinical_dynamic_input:
                    for entry in target_presets:
                        key = 'name' if search_type == "Species Name" else 'clinical_group'
                        if entry.get(key, "").strip().lower() == species_clinical_dynamic_input.strip().lower():
                            selected_preset = entry
                            break

                if selected_preset:
                    st.success(f"✅ Found preset for {species_clinical_dynamic_input}")
                    st.json(selected_preset)
                else:
                    st.warning(f"❌ No preset found for {species_clinical_dynamic_input}. Please check your input or try a different search type.")

        with tab2:
            container3 = st.container(border=True)
            container3.header("💊 Antibiotic Sensitivities")
            container3.write("Use the filters below to obtain your results.")
            input_results_container = st.container(border=True)

        # Top filters
        left, middle, right = container3.columns(3, vertical_alignment="center")
       
        with left:
            sterility_type = st.radio("Filter by", ["Sterile", "Urine", "Other"])
        with middle:
            mic_disc_filter = st.radio("Select MIC or Disc", ["MIC", "Disc","MIC & Disc"])
        with right:
            infection_site = st.selectbox("Select a section", ["-- Select --", "Normal", "❤️ Endocarditis", "🧠CSF"])

        # Ensure session state is initialized
        if "user_result" not in st.session_state:
            st.session_state.user_result = {}

        with input_results_container:     
            left, right = st.columns(2, vertical_alignment="center")
            with left:
                st.header("📊 Antibiotic Sensitivities Input")
                left_name_input = st.text_input("Enter species name")
                left_submit = False #initially set button to False to avoid immediate submission
                _, clinical_group = match_bacterium_name_to_clinical_group(left_name_input, df, species)
                print(f"[DEBUG] Sensitivity inputs - Bacteria: {left_name_input}, Group: {clinical_group}, Sterility: {sterility_type}, Type: {mic_disc_filter}")
                print(f"[DEBUG] Bacterial name entered: {left_name_input.strip().lower()}")
                bact_name_left, clinical_group_left = match_bacterium_name_to_clinical_group(left_name_input, df, species)
                name, antibiotics_left, sterility_check = get_relevant_preset(
                    bacterium_name=bact_name_left if bact_name_left else left_name_input.strip().lower(),
                    clinical_group=clinical_group_left.strip().lower() if clinical_group_left else "",
                    sterility_check=sterility_type.strip().lower(),
                    mic_disc=mic_disc_filter.strip().lower())
                    
                left_input_container_1 = st.container(border=False)
                with left_input_container_1:
                    if left_name_input.strip():
                        if antibiotics_left:
                            st.success(f"✅ Found antibiotics for {name} ({mic_disc_filter.upper()}):")
                            for antibiotic in antibiotics_left:
                                result = st.text_input(f"Enter result for {antibiotic}:", key=f"left_{name}_{antibiotic}")
                                st.session_state.user_result[f"left_{antibiotic}"] = result
                                if "left_submitted" not in st.session_state:
                                    st.session_state.left_submitted = False
                            # Set left_submit to True when the button is clicked
                            if st.button("submit", type="primary", key="left_submit"):
                                st.session_state.left_submitted = True
                                print(f"[DEBUG] Left submit clicked for {name} with results: {st.session_state.user_result}")
                            
                        else:
                            st.warning(f"❌ No preset found for {name} (clinical group: {clinical_group_left}) with sterility: {sterility_type}.")
                            print(f"[DEBUG] No preset found for {name} (clinical group: {clinical_group_right}) with sterility: {sterility_type}.")
                        
                    else:
                        st.info("ℹ️ Please enter a bacterial species to begin.")

            with right:
                st.header("📊 Antibiotic Sensitivities Input")
                right_name_input = st.text_input("Enter species name: ")
                right_submit = False #initially set button to False to avoid immediate submission
                _, clinical_group = match_bacterium_name_to_clinical_group(right_name_input, df, species)
                print(f"[DEBUG] Sensitivity inputs - Bacteria: {right_name_input}, Group: {clinical_group}, Sterility: {sterility_type}, Type: {mic_disc_filter}")
                print(f"[DEBUG] Bacterial name entered: {right_name_input.strip().lower()}")
                bact_name_right, clinical_group_right = match_bacterium_name_to_clinical_group(right_name_input, df, species)
                name, antibiotics_right, sterility_check = get_relevant_preset(
                    bacterium_name=bact_name_right if bact_name_right else right_name_input.strip().lower(),
                    clinical_group=clinical_group_right.strip().lower() if clinical_group_right else "",
                    sterility_check=sterility_type.strip().lower(),
                    mic_disc=mic_disc_filter.strip().lower())

                right_input_container_1 = st.container(border=False)
                with right_input_container_1:
                    if right_name_input.strip():
                        if antibiotics_right:
                            st.success(f"✅ Found antibiotics for {name} ({mic_disc_filter.upper()}):")
                            for antibiotic in antibiotics_right:
                                result = st.text_input(f"Enter result for {antibiotic}:", key=f"right_{name}_{antibiotic}")
                                st.session_state.user_result[f"right_{antibiotic}"] = result
                            if "right_submitted" not in st.session_state:
                                    st.session_state.right_submitted = False
                            # Set right_submit to True when the button is clicked
                            if st.button("submit", type="primary", key="right_submit"):
                                st.session_state.right_submitted = True
                                print(f"[DEBUG] Right submit clicked for {name}  with results: {st.session_state.user_result}")

                        else:
                            st.warning(f"❌ No preset found for {name} (clinical group: {clinical_group_right}) with sterility: {sterility_type}.")
                            print(f"[DEBUG] No preset found for {name} (clinical group: {clinical_group_right}) with sterility: {sterility_type}.")
                    else:
                        st.info("ℹ️ Please enter a bacterial species to begin.")

            result_container = st.container(border=True)
            with result_container:
                left, right = st.columns(2, vertical_alignment="center")
                with left:
                    st.header("📄Results")
                    result_container = st.container(border=False)
                    if st.session_state.left_submitted:
                        final_results = {k.replace("left_", ""): v for k, v in st.session_state.user_result.items() if k.startswith("left_") and v.strip()}
                        #To add debug comment regarding final result 

                        st.success(f"✅ Results recorded for {bact_name_left}:")
                        result = get_breakpoints(bact_name_left, all_data, clinical_group_left)

                        if result:
                            interpretations = process_user_results(result, final_results, mic_disc_filter)
                            for ab, info in interpretations.items():
                                # Add color coding for interpretation
                                color = "green" if info['interpretation'] == "Sensitive" else "orange" if info['interpretation'] == "Intermediate" else "red"
                                st.markdown(
                                    f"<p><b>🔬 {ab} ({info['site']})</b><br>"
                                    f"User Value: {info['value']} | S: {info['S']} | R: {info['R']}<br>"
                                    f"<span style='color:{color}; font-weight:bold;'>➤ {info['interpretation']}</span></p>",
                                    unsafe_allow_html=True)
                                print(f"[DEBUG for color] Interpretation for {ab}: '{info['interpretation']}'")
                                print(f"[DEBUG] {ab}: {info}")
                                

                        else:
                            st.warning("❌ No breakpoints found for this organism")
                            st.session_state.user_result = {}

                with right:
                    st.header("📄Results")
                    result_container = st.container(border=False)
                    if st.session_state.right_submitted:
                        final_results = {k.replace("right_", ""): v for k, v in st.session_state.user_result.items() if k.startswith("right_") and v.strip()}
                        #To add debug comment regarding final_results


                        st.success(f"✅ Results recorded for {bact_name_right}:")
                        result = get_breakpoints(bact_name_right, all_data, clinical_group_right)

                        if result:
                            interpretations = process_user_results(result, final_results, mic_disc_filter)
                            for ab, info in interpretations.items():
                                # Add color coding for interpretation
                                color = "green" if info['interpretation'] == "Sensitive" else "orange" if info['interpretation'] == "Intermediate" else "red"
                                st.markdown(
                                    f"<p><b>🔬 {ab} ({info['site']})</b><br>"
                                    f"User Value: {info['value']} | S: {info['S']} | R: {info['R']}<br>"
                                    f"<span style='color:{color}; font-weight:bold;'>➤ {info['interpretation']}</span></p>",
                                    unsafe_allow_html=True)
                                print(f"[DEBUG] {ab}: {info}")
                        else:
                            st.warning("❌ No breakpoints found for this organism")
                            st.session_state.user_result = {}

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

    st.sidebar.markdown("Developed by Martin Galea, version 1.0")


# --- App Entry Point ---
if not st.session_state.get("logged_in", False):
    print("[INFO] Showing login form")
    st.subheader("🔐 Login to Access the App")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            print(f"[DEBUG] Login submitted with username: {username}")
            if check_login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"✅ Welcome, {username}!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
else:
    print(f"[INFO] Logged in as {st.session_state.get('username')}")
    show_app()
