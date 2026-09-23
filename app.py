import streamlit as st
import pandas as pd
import json
import os

DATA_FILE = "lonerevision_data.json"

# Standard arbetsmoment
STANDARD_TASKS = {
    "Projektledning": 20.0,
    "Förberedelse": 20.0,
    "Ritarbete": 20.0,
    "Handläggning": 20.0,
    "Granskning": 20.0
}

# --- 1. SPARA/LADDA DATA FUNKTIONER ---
def load_data():
    data = None
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
            
    if not data:
        data = {
            "roles": {
                "Junior konsult": dict(STANDARD_TASKS),
                "Handläggare": dict(STANDARD_TASKS),
                "Senior konsult": dict(STANDARD_TASKS),
                "Specialist": dict(STANDARD_TASKS),
                "Senior specialist": dict(STANDARD_TASKS)
            },
            "employees": {},
            "settings": {"exp_threshold": 3.0}
        }
    else:
        for role, tasks in data["roles"].items():
            for task_name in STANDARD_TASKS.keys():
                if task_name not in tasks:
                    tasks[task_name] = 0.0 
    return data

def save_data():
    data = {
        "roles": st.session_state.roles,
        "employees": st.session_state.employees,
        "settings": st.session_state.settings
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 2. INITIALISERA MINNET ---
if 'initialized' not in st.session_state:
    data = load_data()
    st.session_state.roles = data["roles"]
    st.session_state.employees = data["employees"]
    st.session_state.settings = data.get("settings", {"exp_threshold": 3.0})
    st.session_state.initialized = True

if 'edit_emp_id' not in st.session_state:
    st.session_state.edit_emp_id = None

# --- 3. APP KONFIGURATION & MENY ---
st.set_page_config(page_title="Lönerevision System", layout="wide")
st.title("💼 System för Lönerevision och Utvärdering")

st.sidebar.title("Navigering")
menu = st.sidebar.radio("Gå till:", [
    "👥 Sök & Hantera Anställda", 
    "⚙️ Arbetstitlar & Moment", 
    "⭐ Utvärdera Anställd", 
    "📊 Lönerevisionsunderlag",
    "🛠️ Inställningar"
])

# --- MENY 1: HANTERA ANSTÄLLDA ---
if menu == "👥 Sök & Hantera Anställda":
    st.header("Hantera Anställda")
    
    edit_id = st.session_state.edit_emp_id
    is_editing = edit_id in st.session_state.employees
    
    if is_editing:
        st.warning(f"✏️ Du redigerar anställd med ID: **{edit_id}**. (Klicka på knappen nedan för att avbryta)")
        if st.button("Avbryt redigering"):
            st.session_state.edit_emp_id = None
            st.rerun()
        curr_data = st.session_state.employees[edit_id]
    else:
        curr_data = {}

    with st.form("employee_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            emp_id = st.text_input("Anställningsnummer (Krävs)*", value=edit_id if is_editing else curr_data.get("Anställningsnummer", ""), disabled=is_editing)
            first_name = st.text_input("Förnamn", value=curr_data.get("Förnamn", ""))
            last_name = st.text_input("Efternamn", value=curr_data.get("Efternamn", ""))
            
            default_title_idx = 0
            if is_editing and curr_data.get("Grundtitel") in ["Junior konsult", "Handläggare"]:
                default_title_idx = 0 if curr_data.get("Grundtitel") == "Junior konsult" else 1
            base_title = st.selectbox("Grundtitel (om inga specialkompetenser väljs)", ["Junior konsult", "Handläggare"], index=default_title_idx)
            
        with col2:
            street = st.text_input("Gatuadress", value=curr_data.get("Gatuadress", ""))
            zipcode = st.text_input("Postnummer", value=curr_data.get("Postnummer", ""))
            city = st.text_input("Kommun", value=curr_data.get("Kommun", ""))
            edu_years = st.number_input("Utbildning (antal år)", min_value=0.0, step=0.1, format="%.1f", value=float(curr_data.get("Utbildning (år)", 0.0)))
            exp_years = st.number_input("Erfarenhet (antal år)", min_value=0.0, step=0.1, format="%.1f", value=float(curr_data.get("Erfarenhet (år)", 0.0)))
            
        with col3:
            st.write("**Kompetenser & Behörigheter:**")
            självgående = st.checkbox("Självgående", value=curr_data.get("Självgående", False))
            kundkontakt = st.checkbox("Kundkontakt", value=curr_data.get("Kundkontakt", False))
            sättningsberäkningar = st.checkbox("Sättningsberäkningar", value=curr_data.get("Sättningsberäkningar", False))
            stabilitetsberäkningar = st.checkbox("Stabilitetsberäkningar", value=curr_data.get("Stabilitetsberäkningar", False))
            granskning = st.checkbox("Kan utföra granskning", value=curr_data.get("Granskningsbehörig", False))
        
        btn_text = "Spara ändringar" if is_editing else "Spara ny anställd"
        submit_btn = st.form_submit_button(btn_text)
        
        if submit_btn:
            target_id = edit_id if is_editing else emp_id
            if not target_id or not first_name or not last_name:
                st.error("❌ Anställningsnummer, förnamn och efternamn måste fyllas i.")
            else:
                final_title = base_title
                if granskning and sättningsberäkningar and stabilitetsberäkningar:
                    final_title = "Senior specialist"
                elif sättningsberäkningar and stabilitetsberäkningar:
                    final_title = "Specialist"
                elif granskning:
                    final_title = "Senior konsult"

                existing_poäng = st.session_state.employees.get(target_id, {}).get("Poäng", {})

                st.session_state.employees[target_id] = {
                    "Anställningsnummer": target_id,
                    "Förnamn": first_name,
                    "Efternamn": last_name,
                    "Gatuadress": street,
                    "Postnummer": zipcode,
                    "Kommun": city,
                    "Utbildning (år)": round(edu_years, 1),
                    "Erfarenhet (år)": round(exp_years, 1),
                    "Grundtitel": base_title,
                    "Titel": final_title,
                    "Självgående": självgående,
                    "Kundkontakt": kundkontakt,
                    "Sättningsberäkningar": sättningsberäkningar,
                    "Stabilitetsberäkningar": stabilitetsberäkningar,
                    "Granskningsbehörig": granskning,
                    "Poäng": existing_poäng
                }
                save_data()
                st.session_state.edit_emp_id = None
                st.success(f"✅ Anställd {first_name} {last_name} sparades!")
                st.rerun()

    st.divider()
    st.subheader("Sök & Lista befintliga anställda")
    
    search_query = st.text_input("🔍 Sök på namn, anställningsnummer eller titel:", "")
    
    if st.session_state.employees:
        for emp_id, emp in st.session_state.employees.items():
            full_text = f"{emp['Anställningsnummer']} {emp['Förnamn']} {emp['Efternamn']} {emp['Titel']} {emp['Kommun']}".lower()
            if search_query.lower() in full_text or not search_query:
                with st.expander(f"👤 {emp['Förnamn']} {emp['Efternamn']} (Anst.nr: {emp['Anställningsnummer']} - {emp['Titel']})"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.write(f"**Adress:** {emp['Gatuadress']}, {emp['Postnummer']} {emp['Kommun']}")
                        st.write(f"**Utbildning:** {emp['Utbildning (år)']} år | **Erfarenhet:** {emp['Erfarenhet (år)']} år")
                    with c2:
                        st.write(f"**Självgående:** {'Ja' if emp.get('Självgående') else 'Nej'}")
                        st.write(f"**Kundkontakt:** {'Ja' if emp.get('Kundkontakt') else 'Nej'}")
                        st.write(f"**Granskning:** {'Ja' if emp.get('Granskningsbehörig') else 'Nej'}")
                    with c3:
                        st.write(f"**Sättning:** {'Ja' if emp.get('Sättningsberäkningar') else 'Nej'}")
                        st.write(f"**Stabilitet:** {'Ja' if emp.get('Stabilitetsberäkningar') else 'Nej'}")
                    
                    if st.button(f"Redigera {emp['Anställningsnummer']}", key=f"edit_btn_{emp_id}"):
                        st.session_state.edit_emp_id = emp_id
                        st.rerun()

# --- MENY 2: ARBETSTITLAR & MOMENT ---
elif menu == "⚙️ Arbetstitlar & Moment":
    st.header("Hantera arbetstitlar och arbetsuppgifter")
    
    selected_role = st.selectbox("Välj arbetstitel att konfigurera", list(st.session_state.roles.keys()))
    current_tasks = st.session_state.roles[selected_role]
    
    with st.form(f"tasks_form_{selected_role}"):
        updated_tasks = {}
        tasks_to_delete = []
        
        for task, weight in current_tasks.items():
            col_a, col_b, col_c = st.columns([3, 2, 1])
            with col_a:
                new_name = st.text_input(f"Momentnamn", value=task, key=f"name_{selected_role}_{task}")
            with col_b:
                new_weight = st.number_input(f"Vikt (%)", min_value=0.0, max_value=100.0, value=float(weight), step=0.1, format="%.1f", key=f"weight_{selected_role}_{task}")
            with col_c:
                remove = st.checkbox("Ta bort", key=f"del_{selected_role}_{task}")
            
            if remove:
                tasks_to_delete.append(task)
            elif new_name:
                updated_tasks[new_name] = new_weight

        st.divider()
        st.write("**Lägg till nytt arbetsmoment:**")
        col_new1, col_new2 = st.columns([3, 2])
        with col_new1:
            new_task_name = st.text_input("Nytt arbetsmoment namn")
        with col_new2:
            new_task_weight = st.number_input("Nytt moment vikt (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f")

        submitted = st.form_submit_button("Spara ändringar för titel")
        
        if submitted:
            if new_task_name and new_task_name not in updated_tasks:
                updated_tasks[new_task_name] = new_task_weight
            
            st.session_state.roles[selected_role] = updated_tasks
            save_data()
            st.success("✅ Arbetsmomenten har uppdaterats!")
            st.rerun()

    total = sum(st.session_state.roles[selected_role].values())
    if round(total, 1) == 100.0:
        st.success("✅ Total vikt är exakt 100.0%. Perfekt!")
    else:
        st.warning(f"⚠️ Total vikt är {round(total, 1)}%. Justera så att summan blir exakt 100.0%.")

# --- MENY 3: UTVÄRDERA ANSTÄLLD ---
elif menu == "⭐ Utvärdera Anställd":
    st.header("Sätt poäng inför lönerevision")
    
    if not st.session_state.employees:
        st.info("ℹ️ Du måste lägga till anställda först.")
    else:
        period = st.text_input("Ange utvärderingsperiod (t.ex. 2026, Lönerevision 2026/2027):", value="2026")
        
        emp_options = {f"{e['Förnamn']} {e['Efternamn']} - {e['Anställningsnummer']}": k for k, e in st.session_state.employees.items()}
        selected_display = st.selectbox("Välj anställd att utvärdera", list(emp_options.keys()))
        emp_id = emp_options[selected_display]
        
        emp = st.session_state.employees[emp_id]
        role = emp["Titel"]
        tasks = st.session_state.roles.get(role, {})
        
        st.write(f"Bedöm **{emp['Förnamn']} {emp['Efternamn']}** ({role}) för perioden **{period}**.")
        
        if not tasks:
            st.warning("Inga arbetsmoment hittades för denna titel. Gå till 'Arbetstitlar & Moment' och lägg till några.")
        else:
            with st.form("eval_form"):
                scores = {}
                existing_period_scores = emp.get("Poäng", {}).get(period, {})
                
                for task in tasks.keys():
                    current = existing_period_scores.get(task, 5.0)
                    scores[task] = st.slider(task, 1.0, 10.0, float(current), 0.1, format="%.1f")
                
                if st.form_submit_button("Spara utvärdering"):
                    if "Poäng" not in st.session_state.employees[emp_id]:
                        st.session_state.employees[emp_id]["Poäng"] = {}
                    
                    st.session_state.employees[emp_id]["Poäng"][period] = scores
                    save_data()
                    st.success(f"✅ Utvärdering för period '{period}' har sparats!")

# --- MENY 4: LÖNEREVISIONSRAPPORT ---
elif menu == "📊 Lönerevisionsunderlag":
    st.header("Sammanställning & Lönerevisionsunderlag")
    
    threshold = st.session_state.settings.get("exp_threshold", 3.0)
    
    if not st.session_state.employees:
        st.info("ℹ️ Inget data att visa ännu.")
    else:
        all_periods = set()
        for emp in st.session_state.employees.values():
            if "Poäng" in emp and isinstance(emp["Poäng"], dict):
                all_periods.update(emp["Poäng"].keys())
        
        if not all_periods:
            st.info("ℹ️ Inga utvärderingar har gjorts ännu. Gå till 'Utvärdera Anställd' först.")
        else:
            selected_report_period = st.selectbox("Välj period att visa underlag för:", sorted(list(all_periods)))
            
            report_data = []
            for emp_id, emp in st.session_state.employees.items():
                role = emp["Titel"]
                tasks = st.session_state.roles.get(role, {})
                
                exp = round(emp["Erfarenhet (år)"], 1)
                edu = round(emp["Utbildning (år)"], 1)
                
                if exp > threshold:
                    competence_value = exp 
                else:
                    competence_value = (exp + edu) / 2 
                
                total_score = 0.0
                period_scores = emp.get("Poäng", {}).get(selected_report_period, {})
                
                if tasks and period_scores:
                    for task, weight in tasks.items():
                        score = period_scores.get(task, 0)
                        total_score += score * (weight / 100)
                
                total_revision_score = competence_value + total_score
                        
                report_data.append({
                    "Anst.nr": emp_id,
                    "Namn": f"{emp['Förnamn']} {emp['Efternamn']}",
                    "Titel": role,
                    "Kommun": emp["Kommun"],
                    "Period": selected_report_period,
                    "Erfarenhet": round(exp, 1),
                    "Utbildning": round(edu, 1),
                    "Grundkompetens": round(competence_value, 1),
                    "Viktad Prestationspoäng": round(total_score, 1),
                    "Totalt Underlag": round(total_revision_score, 1)
                })
                
            df_report = pd.DataFrame(report_data)
            
            # Sortera så att personal med samma befattning (Titel) hamnar tillsammans
            df_report = df_report.sort_values(by=["Titel", "Namn"])
            
            search_report = st.text_input("🔍 Sök i underlaget:", key="search_report")
            if search_report:
                mask = df_report.apply(lambda row: row.astype(str).str.contains(search_report, case=False).any(), axis=1)
                df_report = df_report[mask]
                
            # Formatera tabellen så att numeriska värden visas med en decimal
            numeric_cols = ["Erfarenhet", "Utbildning", "Grundkompetens", "Viktad Prestationspoäng", "Totalt Underlag"]
            styled_df = df_report.style.format(formatter="{:.1f}", subset=numeric_cols).highlight_max(subset=['Totalt Underlag'], color='lightgreen')

            st.dataframe(styled_df, use_container_width=True)

# --- MENY 5: INSTÄLLNINGAR ---
elif menu == "🛠️ Inställningar":
    st.header("Globala Inställningar")
    
    with st.form("settings_form"):
        current_threshold = st.session_state.settings.get("exp_threshold", 3.0)
        
        st.write("### Gränsvärde för Erfarenhet")
        new_threshold = st.number_input(
            "Max erfarenhet innan utbildning ignoreras (år):", 
            min_value=0.0, 
            value=float(current_threshold), 
            step=0.1,
            format="%.1f"
        )
        
        if st.form_submit_button("Spara inställningar"):
            st.session_state.settings["exp_threshold"] = round(new_threshold, 1)
            save_data()
            st.success("✅ Inställningarna har uppdaterats!")
