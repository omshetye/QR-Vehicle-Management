import streamlit as st
import cv2
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
from pyzbar.pyzbar import decode
firebase_initialized = False
ref = None
import json
from streamlit_option_menu import option_menu
from datetime import datetime
FIREBASE_APP_NAME="myapp"


def initialize_firebase():
    global firebase_initialized, ref
    if not firebase_initialized:
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": "qr-vehicle-database",
            "private_key_id": "45960d3d11593a52ef1d0c2fafa805d287e056f4",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDXS2DcAfeofZSn\nQy4fnbSy5vSLPsleNdrIMQC9uWzvY67HbZgZvC50N2oopeFIQ9CBPjMGP/jtOhOG\nCXhD0etyZ2GX46Miq21dbVbiqUDwomPIrcX/4e2NPF9YoSPfZ/K7AinRi4xkXUUI\nlpROZas2CrsbVyljpqLXSH/OCoz93aalblEcEeiDOSAzHleNp18kEfH4B+8X/NCZ\nNwsK55z7gJKzlYb6uKjEk8E1hQsn2COx5/VhyZ/AktMu+W6hAtG8/RmrJgl1tOHq\nkJAugRqgE7P5ki4lRLWhrTf8l2At03UgaPum8OW4KqtkKMhXiucY3ShfxftwaK/d\nF2Gwd6+xAgMBAAECggEACE/pWsxydxprk05aa/r58mR7bo9lj3IO2M+jhwzGfdXJ\nJOP6mOjbJNW1Dxk+/A2Lq+1i7x1LLj+485wgWhpWFOIJGzODAqBL69XGC0OFEssl\nKAQORE+pu6Hzt7YDKQDd8/qY8unljCz8mWxgVry19oTRLij1bSCxbbdQOJ8VTBjm\nw4O8EF7Z4F0AOrQdZUPRwogyO6smZM6BJtX6QFfhmxwhdID97n0unCObpTbHcQBF\n21T2deV68MPm3HZaWINu4ghzDxvIHVIa2ybl12VnRqPC5RrVkmuyAB6cz74YwKr6\nfTxqUcrvs1b6jsezmTdhpjLSdI6xW791ayaKF0qwTQKBgQD9tRAuTtZk8jJx0rqp\noJ9qLfRoNgq+pdu6zw4mtUOlQkVnp9Lr91F8rgkgDHIh1nmQ64wqc+HGajYlGIHp\nCImnoG11tvV/4vFNnfZuRe2uc2xcwDNTYrSWn/tpx2/f3T+aMm4WwAgbq4nnlKNT\nf05dl8OvQrXSxTBmWbMkwmfEvwKBgQDZPXMHoVTIXLQZa/1ant2Um3xMYG+jqSkG\n5qQkRa2hYrBasLZ3alwksof3Mgtw4KvPzgw3d6gZBBFQoTYNtSyUvVAOeKl5VpIB\nDfs5Zbau2CQsVunT8kDw/aQGbMg8g7562y4t+aWT39u95wqOF21DByUyy57qeawB\nUri0KvR3jwKBgCRooIrUu4W/ECgvgqQnLdlyANoXr1EOwkq7vh8l8jA8I3OtrOI6\nGtKWsy6LOrHKcqWud+37tVHhGiYWr0X++Ko6ppq3B+IzckeePKg0lthrLgjdeEAm\nMR5QlSbn/REWUjNRu2S+aCt4YZD/TrUD1v4tcmKrYyZ9L+XwR3ol//hHAoGANFtW\nBOnCGEQXd+UJ+7Q8LRvIOlQns+cKJ0qhFsjgTvwNCt56K4+rw4BvuokKLttHLV84\nnImvLtBHKAqij20x4Gs8BzDXj5HowG5RNQUpoTwgg7sywc0qD6rhxFalb8hEuTFo\nENaRLHGQcVVkutg0kin/sh1XIKXQacU5FNshbksCgYAUd9eAyRZsSQXIFqeM0r+E\nvrkdoEh3IbnPKFdITv39zpIJixho5f2AVtpfteFjoqPCOHwEA/vSMGWT4DdqGJdF\nCyTuendM8Td3lRABRv02pDAU9+SsiQDfl530IaO8LkkXQkIEuOv4IhGPLPmLXro7\ntsFq04mF5NRTZe2/bRVYzA==\n-----END PRIVATE KEY-----\n",
            "client_email": "firebase-adminsdk-3r0gg@qr-vehicle-database.iam.gserviceaccount.com",
            "client_id": "112997496607568420682",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-3r0gg%40qr-vehicle-database.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        })

        firebase_admin.initialize_app(cred, {'databaseURL': 'https://qr-vehicle-database-default-rtdb.asia-southeast1.firebasedatabase.app/'})
        ref = db.reference("/")
        firebase_initialized = True
    else:
        app = firebase_admin.get_app(name=FIREBASE_APP_NAME)
        ref = db.reference("/", app=app)


# Video Capture Function
def capture_video():
    start = st.empty()
    if start.button("Start"):
        start.empty()
        cap = cv2.VideoCapture(2)
        stop = st.button("Stop", key="stop_button")
        frame_placeholder = st.empty()
        while cap.isOpened() and not stop:
            ret, frame = cap.read()

            if not ret:
                st.write("The video capture has ended.")
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_placeholder.image(frame, channels="RGB")
            info = decode(gray)
            if info:
                for qr_code in info:
                    decoded_data = qr_code.data.decode("utf-8")
                    decoded_data = json.loads(decoded_data)
                    name = decoded_data.get('name')
                    st.write("Data collected for: ", name)
                    return decoded_data
                else:
                    return
            if cv2.waitKey(1) & 0xFF == ord("q") or stop:
                stop = st.button("Start")
                break
        cap.release()
        cv2.destroyAllWindows()


def datetime_serializer(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()


def send_data(decoded_data):
    ct = datetime.datetime.now()
    ts = "timestamp"
    decoded_data[ts] = ct    
    decoded_data = json.dumps(decoded_data, default=datetime_serializer)
    ref = db.reference("/")
    data = ref.get()
    st.text(decoded_data)
    new_ref=ref.push()
    new_ref.set(json.loads(decoded_data))  # Use push to add data with a unique key
    

def display_firebase_data():
    st.title("Firebase Data Display")
    ref = db.reference("/")

    # Retrieve data from Firebase
    firebase_data = ref.get()

    if firebase_data:
        # Flatten the JSON data for tabular display
        flattened_data = []
        for key, value in firebase_data.items():
            flattened_data.append({**{'Key': key}, **value})

        # Convert to DataFrame
        df = pd.DataFrame(flattened_data)

        # Display the data as a table
        st.table(df)
    else:
        st.write("No data found in Firebase.")


# def get_data_from_firebase():
#     initialize_firebase()
#     ref = db.reference("/")
#     data_snapshot = ref.get()
#     if data_snapshot:
#         data = dict(data_snapshot)
#         return data
#     else:
#         return {}


def calculate_time_difference(entry_timestamp, exit_timestamp):
    entry_time = datetime.datetime.fromisoformat(entry_timestamp)
    exit_time = datetime.datetime.fromisoformat(exit_timestamp)
    time_diff = exit_time - entry_time
    return time_diff


def generate_bill_amount(time_difference, rate_per_hour):
    total_hours = time_difference.total_seconds() / 3600
    bill_amount = total_hours * rate_per_hour
    return bill_amount


# data = get_data_from_firebase()
# record_keys = list(data.keys())
#
# if len(record_keys) >= 2:
#     exit_record_key = record_keys[-1]
#     exit_record = data[exit_record_key]
#
#     for entry_record_key in record_keys[:-1]:
#         entry_record = data[entry_record_key]
#
#         if entry_record['name'] == exit_record['name'] and entry_record['number'] == exit_record['number']:
#             if entry_record['timestamp'] < exit_record['timestamp']:
#                 time_diff = calculate_time_difference(entry_record['timestamp'], exit_record['timestamp'])
#
#                 billing_rate_per_hour = 20
#                 bill_amount = generate_bill_amount(time_diff, billing_rate_per_hour)
#
#                 print(f"Time Difference for {exit_record['name']}: {time_diff}")
#                 print(f"Bill Amount for {entry_record['name']}: ${bill_amount:.2f}")
# else:
#     print("Not enough data to calculate the bill.")

# def gen_bill(decoded_data):
#     ref = db.reference("/")
#     data_snapshot = ref.get()
#     if data_snapshot:
#         data = dict(data_snapshot)
#         return data
#     else:
#         return {}
#     counter=0
#     for i in data:
#         if i["number"]==decoded_data["number"]:
#             counter+=1
#     print(counter)


# Create a navigation bar using st.sidebar
nav_option = option_menu(
    menu_title=None,
    options=['Home', 'Scan QR', 'Database', 'Bills'],
    icons=['house', 'qr-code', 'database', 'currency-rupee'],
    default_index=0,
    orientation='horizontal'
)

# Display content based on the selected navigation option
if nav_option == "Home":
    st.title("Home Page")
    st.write("Welcome to the home page.")

elif nav_option == "Scan QR":
    st.title("Scan QR")
    data = capture_video()
    if data:
        send_data(data)
    # gen_bill(data)

elif nav_option == "Database":
    display_firebase_data()

elif nav_option == "Bills":
    st.title("Bills Page")
    user_input = st.text_input("Enter your name or car number: ")
    ref = db.reference("/")
    counter = 1
    all_entries = ref.get()
    timestamps=[]
    if all_entries:
        for key, value in all_entries.items():
            name = value.get("name")
            number = value.get("number")
            timestamp = value.get("timestamp")
            if user_input.lower() == name.lower() or user_input.lower() == number.lower():
                counter += 1
                timestamps.append(timestamp)
    timestamps.sort(reverse=True)
    if counter % 2 != 0:
        if counter >= 2:
            latest_timestamp1 = datetime.fromisoformat(timestamps[0])
            latest_timestamp2 = datetime.fromisoformat(timestamps[1])

            time_difference = latest_timestamp1 - latest_timestamp2
            time_difference_hours = round(time_difference.total_seconds() / 3600, 2)
            st.text(f"Time your vehicle has been parked for:  {time_difference_hours} Hours")
            bill = generate_bill_amount(time_difference, 25)
            st.text(f"Your Bill: {round(bill, 4)} $")
    else:
        st.text("No Pending Bills for you")