import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- DATABASE CONNECTION ---------------- #
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ashu_2004",
    database="hospital1"
)

cursor = conn.cursor()

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="Hospital Management System",
    page_icon="🏥",
    layout="wide"
)

# ---------------- CUSTOM CSS ---------------- #
st.markdown("""
<style>
.main {

   background-color: #f9fafc;
}
.stButton>button {
    border-radius: 10px;
    height: 3em;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

st.title("🏥 Hospital Management System")

# ---------------- SIDEBAR ---------------- #
menu = st.sidebar.selectbox(
    "Select Menu",
    [
        "Add Patient",
        "Manage Patients",
        "Add Doctor",
        "Manage Doctors",
        "Book Appointment",
        "Update Appointment Status",
        "Generate Bill",
        "View Appointments",
        "Dashboard"
    ]
)

# ============================================================
# ADD PATIENT
# ============================================================

if menu == "Add Patient":

    st.header("🧍 Add Patient")

    name = st.text_input("Patient Name")

    age = st.number_input("Age", min_value=0)

    gender = st.selectbox(
        "Gender",
        ["Male", "Female", "Other"]
    )

    phone = st.text_input("Phone Number")

    if st.button("Add Patient"):

        if name == "":
            st.error("Name cannot be empty")

        elif len(phone) != 10 or not phone.isdigit():
            st.error("Phone number must be 10 digits")

        else:

            cursor.execute(
                """
                INSERT INTO Patients(name, age, gender, phone)
                VALUES(%s,%s,%s,%s)
                """,
                (name, age, gender, phone)
            )

            conn.commit()

            st.success("Patient Added Successfully ✅")

# ============================================================
# MANAGE PATIENTS
# ============================================================

elif menu == "Manage Patients":

    st.header("📋 Manage Patients")

    search = st.text_input("Search Patient")

    query = "SELECT * FROM Patients WHERE name LIKE %s"

    cursor.execute(query, ('%' + search + '%',))

    data = cursor.fetchall()

    if data:

        df = pd.DataFrame(
            data,
            columns=["Patient ID", "Name", "Age", "Gender", "Phone"]
        )

        st.dataframe(df, use_container_width=True)

        patient_ids = [row[0] for row in data]

        delete_id = st.selectbox(
            "Select Patient ID to Delete",
            patient_ids
        )

        if st.button("Delete Patient"):

            cursor.execute(
                "DELETE FROM Patients WHERE patient_id=%s",
                (delete_id,)
            )

            conn.commit()

            st.success("Patient Deleted Successfully")

# ============================================================
# ADD DOCTOR
# ============================================================

elif menu == "Add Doctor":

    st.header("👨‍⚕️ Add Doctor")

    name = st.text_input("Doctor Name")

    specialization = st.selectbox(
        "Department",
        [
            "Cardiologist",
            "Neurologist",
            "Dermatologist",
            "Orthopedic",
            "Pediatrician",
            "Eye Specialist",
            "ENT Specialist"
        ]
    )

    fees = st.number_input(
        "Consultation Fees",
        min_value=0
    )

    if st.button("Add Doctor"):

        if name == "":
            st.error("Doctor name cannot be empty")

        else:

            cursor.execute(
                """
                INSERT INTO Doctors(name, specialization, fees)
                VALUES(%s,%s,%s)
                """,
                (name, specialization, fees)
            )

            conn.commit()

            st.success("Doctor Added Successfully ✅")

# ============================================================
# MANAGE DOCTORS
# ============================================================

elif menu == "Manage Doctors":

    st.header("🩺 Manage Doctors")

    cursor.execute("SELECT * FROM Doctors")

    data = cursor.fetchall()

    if data:

        df = pd.DataFrame(
            data,
            columns=["Doctor ID", "Name", "Specialization", "Fees"]
        )

        st.dataframe(df, use_container_width=True)

        doctor_ids = [row[0] for row in data]

        delete_id = st.selectbox(
            "Select Doctor ID to Delete",
            doctor_ids
        )

        if st.button("Delete Doctor"):

            cursor.execute(
                "DELETE FROM Doctors WHERE doctor_id=%s",
                (delete_id,)
            )

            conn.commit()

            st.success("Doctor Deleted Successfully")

# ============================================================
# BOOK APPOINTMENT
# ============================================================

elif menu == "Book Appointment":

    st.header("📅 Book Appointment")

    cursor.execute("SELECT patient_id, name FROM Patients")
    patients = cursor.fetchall()

    cursor.execute("SELECT doctor_id, name FROM Doctors")
    doctors = cursor.fetchall()

    if patients and doctors:

        patient_dict = {name: pid for pid, name in patients}
        doctor_dict = {name: did for did, name in doctors}

        selected_patient = st.selectbox(
            "Select Patient",
            list(patient_dict.keys())
        )

        selected_doctor = st.selectbox(
            "Select Doctor",
            list(doctor_dict.keys())
        )

        appointment_date = st.date_input("Appointment Date")

        status = st.selectbox(
            "Appointment Status",
            ["Booked", "Completed", "Cancelled"]
        )

        if st.button("Book Appointment"):

            cursor.execute(
                """
                INSERT INTO Appointments
                (patient_id, doctor_id, appointment_date, status)
                VALUES(%s,%s,%s,%s)
                """,
                (
                    patient_dict[selected_patient],
                    doctor_dict[selected_doctor],
                    appointment_date,
                    status
                )
            )

            conn.commit()

            st.success("Appointment Booked Successfully ✅")

    else:

        st.warning("Please add patients and doctors first")

# ============================================================
# UPDATE APPOINTMENT STATUS
# ============================================================

elif menu == "Update Appointment Status":

    st.header("🔄 Update Appointment Status")

    cursor.execute("SELECT appointment_id FROM Appointments")

    appointments = cursor.fetchall()

    if appointments:

        appointment_ids = [a[0] for a in appointments]

        selected_id = st.selectbox(
            "Select Appointment ID",
            appointment_ids
        )

        new_status = st.selectbox(
            "New Status",
            ["Booked", "Completed", "Cancelled"]
        )

        if st.button("Update Status"):

            cursor.execute(
                """
                UPDATE Appointments
                SET status=%s
                WHERE appointment_id=%s
                """,
                (new_status, selected_id)
            )

            conn.commit()

            st.success("Appointment Status Updated ✅")

# ============================================================
# GENERATE BILL
# ============================================================

elif menu == "Generate Bill":

    st.header("💰 Generate Bill")

    cursor.execute("SELECT patient_id, name FROM Patients")
    patients = cursor.fetchall()

    cursor.execute("SELECT doctor_id, name FROM Doctors")
    doctors = cursor.fetchall()

    patient_dict = {name: pid for pid, name in patients}
    doctor_dict = {name: did for did, name in doctors}

    if patients and doctors:

        selected_patient = st.selectbox(
            "Select Patient",
            list(patient_dict.keys())
        )

        selected_doctor = st.selectbox(
            "Select Doctor",
            list(doctor_dict.keys())
        )

        medicine_cost = st.number_input(
            "Medicine Cost",
            min_value=0
        )

        cursor.execute(
            "SELECT fees FROM Doctors WHERE doctor_id=%s",
            (doctor_dict[selected_doctor],)
        )

        fee = cursor.fetchone()[0]

        total = fee + medicine_cost

        st.info(f"Consultation Fee: ₹{fee}")
        st.info(f"Total Bill: ₹{total}")

        if st.button("Generate Bill"):

            cursor.execute(
                """
                INSERT INTO Billing
                (patient_id, doctor_id, consultation_fee,
                medicine_cost, total_amount)
                VALUES(%s,%s,%s,%s,%s)
                """,
                (
                    patient_dict[selected_patient],
                    doctor_dict[selected_doctor],
                    fee,
                    medicine_cost,
                    total
                )
            )

            conn.commit()

            st.success(
                f"Bill Generated Successfully 💰 Total = ₹{total}"
            )

# ============================================================
# VIEW APPOINTMENTS
# ============================================================

elif menu == "View Appointments":

    st.header("📊 Appointment Details")

    cursor.execute("""
        SELECT
            a.appointment_id,
            p.name,
            d.name,
            d.specialization,
            a.appointment_date,
            a.status
        FROM Appointments a
        JOIN Patients p
        ON a.patient_id = p.patient_id
        JOIN Doctors d
        ON a.doctor_id = d.doctor_id
    """)

    data = cursor.fetchall()

    if data:

        df = pd.DataFrame(
            data,
            columns=[
                "Appointment ID",
                "Patient",
                "Doctor",
                "Specialization",
                "Date",
                "Status"
            ]
        )

        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode('utf-8')

        st.download_button(
            "Download CSV",
            csv,
            "appointments.csv",
            "text/csv"
        )

    else:

        st.info("No Appointments Found")

# ============================================================
# DASHBOARD
# ============================================================

elif menu == "Dashboard":

    st.header("📈 Dashboard")

    # ============================================================
    # KPI CARDS
    # ============================================================

    # Total Patients
    cursor.execute("SELECT COUNT(*) FROM Patients")
    total_patients = cursor.fetchone()[0]

    # Total Doctors
    cursor.execute("SELECT COUNT(*) FROM Doctors")
    total_doctors = cursor.fetchone()[0]

    # Total Revenue
    cursor.execute("SELECT SUM(total_amount) FROM Billing")
    revenue = cursor.fetchone()[0]

    revenue = revenue if revenue else 0

    # Total Appointments
    cursor.execute("SELECT COUNT(*) FROM Appointments")
    total_appointments = cursor.fetchone()[0]

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Patients", total_patients)
    col2.metric("Total Doctors", total_doctors)
    col3.metric("Appointments", total_appointments)
    col4.metric("Total Revenue", f"₹{revenue}")

    st.markdown("---")

    # ============================================================
    # GRAPH 1 → PATIENTS BY GENDER
    # ============================================================

    st.subheader("🧍 Patients By Gender")

    cursor.execute("""
        SELECT gender, COUNT(*)
        FROM Patients
        GROUP BY gender
    """)

    gender_data = cursor.fetchall()

    genders = [row[0] for row in gender_data]
    counts = [row[1] for row in gender_data]

    fig1, ax1 = plt.subplots(figsize=(6,4))

    ax1.bar(genders, counts)

    ax1.set_xlabel("Gender")
    ax1.set_ylabel("Patients")
    ax1.set_title("Patients Distribution")

    st.pyplot(fig1)

    plt.close(fig1)

    st.markdown("---")

    # ============================================================
    # GRAPH 2 → APPOINTMENT STATUS PIE CHART
    # ============================================================

    st.subheader("📅 Appointment Status")

    cursor.execute("""
        SELECT status, COUNT(*)
        FROM Appointments
        GROUP BY status
    """)

    status_data = cursor.fetchall()

    labels = [row[0] for row in status_data]
    sizes = [row[1] for row in status_data]

    fig2, ax2 = plt.subplots(figsize=(6,6))

    ax2.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%'
    )

    ax2.set_title("Appointment Status Distribution")

    st.pyplot(fig2)

    plt.close(fig2)

    st.markdown("---")

    # ============================================================
    # GRAPH 3 → REVENUE BY DOCTOR
    # ============================================================

    st.subheader("💰 Revenue By Doctor")

    cursor.execute("""
        SELECT d.name, SUM(b.total_amount)
        FROM Billing b
        JOIN Doctors d
        ON b.doctor_id = d.doctor_id
        GROUP BY d.name
    """)

    revenue_data = cursor.fetchall()

    if revenue_data:

        doctor_names = [row[0] for row in revenue_data]
        revenues = [row[1] for row in revenue_data]

        fig3, ax3 = plt.subplots(figsize=(8,5))

        ax3.bar(doctor_names, revenues)

        ax3.set_xlabel("Doctors")
        ax3.set_ylabel("Revenue")
        ax3.set_title("Revenue Generated By Doctors")

        plt.xticks(rotation=45)

        st.pyplot(fig3)

        plt.close(fig3)

    else:

        st.info("No Billing Data Available")

# ---------------- CLOSE CONNECTION ---------------- #

conn.close()