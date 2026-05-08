import mysql.connector
from datetime import datetime
from Arduino import send_command

import requests

# number of available spots
available_spots = 10

# Cost per hour
PARKING_RATE_PER_HOUR = 10.0

# entry gate
def store_in_database(digits, letters,cong_avg,img_path):
    global available_spots

    if digits == 'NULL' or letters == 'NULL':
        print("⚠️ Failed to read data, because it's NULL")
        return

    if len(letters) != 3:
        print("⚠️ Letters must be 3 characters long")
        return

    if len(digits) > 4:
        digits = digits[:4]
    if len(letters) > 3:
        letters = letters[:3]

    if not digits and not letters:
        return


    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='your_password',
        database='vehicle_license_db'
    )
    cursor = conn.cursor()

    cursor.execute('''
                  SELECT * FROM vehicle_data
                  WHERE digits = %s AND letters = %s AND exit_time IS NULL
                  LIMIT 1
                   ''', (digits, letters))
    existing_record = cursor.fetchone()


    if existing_record:
        print("ℹ️ License plate already exists")
    else:
        if available_spots > 0:
            cursor.execute('''INSERT INTO vehicle_data (digits, letters) 
                                  VALUES (%s, %s)''', (digits, letters))
            send_command("OPEN_ENTRY_GATE")
            car_plate = letters + digits
            data = {
                "plateNumber": car_plate,
                "confidence": cong_avg,
                "imageUrl": img_path,
                "entry_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            available_spots -= 1
            requests.post("http://localhost:5000/api/update-entry", json=data)
        else:
            print("The parking is full!")
    conn.commit()

    conn.close()

# exit gate
def log_exit(digits, letters,cong_avg,img_path):
    global available_spots

    if len(digits) > 4:
        digits = digits[:4]
    if len(letters) > 3:
        letters = letters[:3]

    if not digits and not letters:
        print("Invalid License Plate")
        return

    exit_time = datetime.now()

    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='your_password',
            database='vehicle_license_db'
        )
        cursor = conn.cursor()

        # Search for newest log in
        cursor.execute('''
            SELECT id, entry_time FROM vehicle_data
            WHERE digits = %s AND letters = %s AND exit_time IS NULL
            ORDER BY entry_time DESC LIMIT 1
        ''', (digits, letters))

        record = cursor.fetchone()

        if not record:
            print("🚫 Valid to find vehicle, or already logged out")
            return

        log_id, entry_time = record
        duration = (exit_time - entry_time).total_seconds() // 60

        # Calculate total cost
        hours = duration / 60
        cost = round(hours * PARKING_RATE_PER_HOUR, 2)

        # Update log out timestamp
        cursor.execute('''
            UPDATE vehicle_data
            SET exit_time = %s,
                duration_minutes = %s,
                cost = %s
            WHERE id = %s
        ''', (exit_time, int(duration), cost, log_id))
        conn.commit()

        send_command("OPEN_EXIT_GATE")

        car_plate = letters + digits
        data = {
            "plateNumber": car_plate,
            "confidence": cong_avg,
            "imageUrl": img_path,
            "entry_time": entry_time.strftime("%Y-%m-%d %H:%M:%S"),
            "exit_time": exit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "cost": cost,
            "exit": True
        }
        requests.post("http://localhost:5000/api/update-entry", json=data)

        available_spots += 1

        print(f"✅ Logged out successfully with duration: {int(duration)} minutes.")

    except mysql.connector.Error as err:
        print(f"❌ error: {err}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def correct_ocr_digits_errors(digits: str) -> str:
    digit_correction_map = {
        'O': '0',
        'D': '0',
        'Q': '0',
        'I': '1',
        'L': '4',
        'Z': '2',
        'S': '5',
        'B': '8',
        'G': '6'
    }
    corrected = ''
    for char in digits.upper():
        corrected += digit_correction_map.get(char, char)

    return corrected

def correct_ocr_letters_errors(text):
    correction_map = {
        '6': 'G',
        '0': 'O',
        '8': 'B',
        '1': 'I',
        '5': 'S',
        '2': 'Z'
    }
    corrected = ''
    for char in text:
        if char in correction_map:
            corrected += correction_map[char]
        else:
            corrected += char
    return corrected