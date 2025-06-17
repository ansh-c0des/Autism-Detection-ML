import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="Consult a Psychologist")

# Initialize database
def init_db():
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS psychologists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            photo TEXT,
            specialization TEXT,
            experience TEXT,
            rating TEXT,
            bio TEXT,
            contact TEXT,
            languages TEXT,
            location TEXT,
            availability TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            psychologist_id INTEGER,
            patient_id INTEGER,
            patient_name TEXT,
            date TEXT,
            time TEXT,
            status TEXT DEFAULT 'Scheduled',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(psychologist_id) REFERENCES psychologists(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Sample data population
def populate_sample_data():
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM psychologists")
    if c.fetchone()[0] == 0:
        sample_psychologists = [
            (1, "Dr. Sarah Johnson", "https://images.unsplash.com/photo-1559839734-2b71ea197ec2", 
             "Anxiety & Depression", "8 years", "4.9 (127 reviews)",
             "Cognitive behavioral therapist specializing in anxiety disorders.", 
             "sarah.j@psychclinic.com", "English,Spanish", "New York",
             "Mon 9AM-12PM,Wed 2PM-5PM,Fri 10AM-1PM"),
            (2, "Dr. Michael Chen", "https://images.unsplash.com/photo-1622253692010-333f2da6031d",
             "Child Psychology", "12 years", "4.8 (89 reviews)",
             "Pediatric psychologist with expertise in ADHD and autism spectrum disorders.",
             "michael.c@childpsych.org", "English,Mandarin", "New York",
             "Tue 10AM-3PM,Thu 1PM-6PM"),
            (3, "Dr. Emily Wilson", "https://images.unsplash.com/photo-1594824476967-48c8b964273f",
             "Trauma Therapy", "10 years", "4.7 (156 reviews)",
             "Trauma specialist using EMDR and somatic experiencing techniques.",
             "emily.w@traumacare.uk", "English,French", "London",
             "Mon-Fri 9AM-4PM")
        ]
        
        c.executemany('''
            INSERT INTO psychologists VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ''', sample_psychologists)
        conn.commit()
    
    conn.close()

# Initialize the database
init_db()
populate_sample_data()

def main():
    st.title(":blue[🧠 Consult a Psychologist]")
    
    tab1, tab2 = st.tabs(["Find Psychologist", "Manage Appointments"])
    
    with tab1:
        find_psychologist()
    
    with tab2:
        manage_appointments()

def find_psychologist():
    st.write("Find qualified mental health professionals in your city")
    
    conn = sqlite3.connect('appointments.db')
    locations = pd.read_sql("SELECT DISTINCT location FROM psychologists", conn)['location'].tolist()
    conn.close()
    
    location = st.selectbox(
        "📍 Select your location",
        locations,
        index=None,
        placeholder="Choose your city..."
    )
    
    if location:
        show_psychologists(location)

def show_psychologists(location):
    conn = sqlite3.connect('appointments.db')
    psychologists = pd.read_sql(
        f"SELECT * FROM psychologists WHERE location = '{location}'", 
        conn
    ).to_dict('records')
    conn.close()
    
    if not psychologists:
        st.warning("No psychologists found in this location. Try another nearby city.")
        return
    
    cols = st.columns(3)
    for idx, psych in enumerate(psychologists):
        with cols[idx % 3]:
            with st.container(border=True):
                st.image(psych["photo"], width=200)
                st.subheader(psych["name"])
                st.caption(f"⭐ {psych['rating']}")
                st.write(psych["specialization"])
                
                if st.button("View Profile", key=f"btn_{psych['id']}"):
                    st.session_state.selected_psych = psych
                    st.rerun()
    
    if "selected_psych" in st.session_state:
        show_profile(st.session_state.selected_psych)

def show_profile(psychologist):
    st.divider()
    st.subheader("Psychologist Profile")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(psychologist["photo"], width=250)
    
    with col2:
        st.title(psychologist["name"])
        st.subheader(psychologist["specialization"])
        st.write(f"**Experience:** {psychologist['experience']}")
        st.write(f"**Rating:** {psychologist['rating']}")
        st.write(f"**Languages:** {psychologist['languages']}")
        st.write(f"**Contact:** {psychologist['contact']}")
        
        st.divider()
        st.write("**Availability:**")
        for slot in psychologist["availability"].split(','):
            st.write(f"- {slot.strip()}")
        
        st.divider()
        st.write("**About:**")
        st.write(psychologist["bio"])
        
        with st.form("booking_form"):
            st.write("### Book Appointment")
            appointment_date = st.date_input("Select date", min_value=datetime.today())
            available_times = ["9:00 AM", "10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM"]
            appointment_time = st.selectbox("Select time", available_times)
            user_notes = st.text_area("Any special requests")
            
            if st.form_submit_button("Confirm Appointment"):
                book_appointment(psychologist, appointment_date, appointment_time, user_notes)
        
        if st.button("← Back to list"):
            del st.session_state.selected_psych
            st.rerun()

def book_appointment(psychologist, date, time_str, notes):
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    
    patient_id = st.session_state.get("user_id", 1)
    patient_name = st.session_state.get("username", "Test User")
    
    c.execute('''
        INSERT INTO appointments (psychologist_id, patient_id, patient_name, date, time, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (psychologist["id"], patient_id, patient_name, str(date), time_str, notes))
    
    conn.commit()
    conn.close()
    
    st.success(f"""
    Appointment booked with {psychologist['name']}!
    **Date:** {date.strftime('%B %d, %Y')}
    **Time:** {time_str}
    """)
    time.sleep(2)
    del st.session_state.selected_psych
    st.rerun()

def manage_appointments():
    st.subheader("Your Appointments")
    
    patient_id = st.session_state.get("user_id", 1)
    
    conn = sqlite3.connect('appointments.db')
    appointments = pd.read_sql(f'''
        SELECT a.id, p.name as psychologist, p.photo, a.date, a.time, a.status, a.notes
        FROM appointments a
        JOIN psychologists p ON a.psychologist_id = p.id
        WHERE a.patient_id = {patient_id} AND a.status != 'Cancelled'
        ORDER BY a.date DESC, a.time DESC
    ''', conn)
    conn.close()
    
    if appointments.empty:
        st.info("You have no upcoming appointments")
        return
    
    for _, appt in appointments.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(appt["photo"], width=100)
            
            with col2:
                st.subheader(appt["psychologist"])
                st.write(f"**Date:** {appt['date']}")
                st.write(f"**Time:** {appt['time']}")
                st.write(f"**Status:** {appt['status']}")
                
                if appt['notes']:
                    with st.expander("View Notes"):
                        st.write(appt['notes'])
                
                col_act1, col_act2, _ = st.columns([1, 1, 2])
                with col_act1:
                    if st.button("Cancel", key=f"cancel_{appt['id']}"):
                        cancel_appointment(appt['id'])
                
                with col_act2:
                    if st.button("Reschedule", key=f"reschedule_{appt['id']}"):
                        st.session_state.reschedule_appt = appt['id']
                        st.rerun()
    
    if "reschedule_appt" in st.session_state:
        st.divider()
        st.subheader("Reschedule Appointment")
        
        conn = sqlite3.connect('appointments.db')
        current_appt = pd.read_sql(f'''
            SELECT a.*, p.name as psychologist 
            FROM appointments a
            JOIN psychologists p ON a.psychologist_id = p.id
            WHERE a.id = {st.session_state.reschedule_appt}
        ''', conn).iloc[0]
        conn.close()
        
        st.write(f"Current appointment with {current_appt['psychologist']}")
        st.write(f"Scheduled for {current_appt['date']} at {current_appt['time']}")
        
        with st.form("reschedule_form"):
            new_date = st.date_input("New date", min_value=datetime.today())
            new_time = st.selectbox("New time", ["9:00 AM", "10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM"])
            reschedule_notes = st.text_area("Reason for rescheduling")
            
            if st.form_submit_button("Confirm Reschedule"):
                reschedule_appointment(
                    st.session_state.reschedule_appt,
                    new_date,
                    new_time,
                    reschedule_notes
                )
        
        if st.button("Cancel Rescheduling"):
            del st.session_state.reschedule_appt
            st.rerun()

def cancel_appointment(appt_id):
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    
    c.execute('''
        UPDATE appointments 
        SET status = 'Cancelled' 
        WHERE id = ?
    ''', (appt_id,))
    
    conn.commit()
    conn.close()
    
    st.success("Appointment cancelled successfully")
    time.sleep(2)
    st.rerun()

def reschedule_appointment(appt_id, new_date, new_time, notes):
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    
    c.execute('''
        UPDATE appointments 
        SET date = ?, time = ?, notes = COALESCE(notes, '') || '\nRescheduled: ' || ?,
            status = 'Rescheduled'
        WHERE id = ?
    ''', (str(new_date), new_time, notes, appt_id))
    
    conn.commit()
    conn.close()
    
    st.success("Appointment rescheduled successfully")
    time.sleep(2)
    if "reschedule_appt" in st.session_state:
        del st.session_state.reschedule_appt
    st.rerun()

# Auth Check
if not st.session_state.get("logged_in", False):
    st.error("Please log in to Consult a psychologist.")
    st.stop()

# Sidebar logout
# Sidebar
with st.sidebar:
    if st.session_state.get("logged_in", False):
        st.success(f"Logged in as {st.session_state.username}")
        if st.sidebar.button("Logout"):
            st.switch_page("pages/8Logout.py")

if __name__ == "__main__":
    main()