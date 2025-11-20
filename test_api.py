import requests
import json

BASE_URL = "http://localhost:8000"

def test_complete_flow():
    print("=" * 60)
    print("E-ATTENDANCE API COMPLETE TEST")
    print("=" * 60)

    # Test 3: Login Lecturer
    print("\n--- TEST 3: Login Lecturer ---")
    login_data = {
        "username": "test_lecturer",
        "password": "SecurePass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        lecturer_token = response.json()["access_token"]
        print("✅ Lecturer logged in successfully")
        print(f"   Token: {lecturer_token[:50]}...")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return
    
    # Test 4: Login Student
    print("\n--- TEST 4: Login Student ---")
    login_data = {
        "username": "test_student",
        "password": "SecurePass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        student_token = response.json()["access_token"]
        print("✅ Student logged in successfully")
        print(f"   Token: {student_token[:50]}...")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return
    
    # Test 5: Create Class (Lecturer)
    print("\n--- TEST 5: Create Class (Lecturer) ---")
    class_data = {
        "name": "Introduction to Python Programming",
        "code": "PY101",
        "description": "Learn Python from scratch",
        "latitude": 6.5244,
        "longitude": 3.3792,
        "radius": 100.0
    }
    
    headers = {"Authorization": f"Bearer {lecturer_token}"}
    response = requests.post(f"{BASE_URL}/classes/create", json=class_data, headers=headers)
    
    if response.status_code == 201:
        class_info = response.json()
        class_id = class_info["id"]
        print("✅ Class created successfully")
        print(f"   Class ID: {class_id}")
        print(f"   Class Code: {class_info['code']}")
        print(f"   Location: ({class_info['latitude']}, {class_info['longitude']})")
        print(f"   Radius: {class_info['radius']} meters")
    elif response.status_code == 400 and "already exists" in response.json()["detail"]:
        print("ℹ️  Class already exists, fetching existing class...")
        # Get class by code
        response = requests.get(f"{BASE_URL}/classes/code/PY101", headers=headers)
        if response.status_code == 200:
            class_info = response.json()
            class_id = class_info["id"]
            print(f"   Using existing Class ID: {class_id}")
        else:
            print(f"❌ Failed to get class: {response.status_code}")
            return
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return
    
    # Test 6: Get All Classes
    print("\n--- TEST 6: Get All Classes ---")
    response = requests.get(f"{BASE_URL}/classes/", headers=headers)
    if response.status_code == 200:
        classes = response.json()
        print(f"✅ Retrieved {len(classes)} class(es)")
        for cls in classes:
            print(f"   - {cls['name']} ({cls['code']})")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
    
    # Test 7: Mark Attendance - Within Geofence (Student)
    print("\n--- TEST 7: Mark Attendance (Within Geofence) ---")
    attendance_data = {
        "class_id": class_id,
        "latitude": 6.5245,  # Very close to class location
        "longitude": 3.3793
    }
    
    headers_student = {"Authorization": f"Bearer {student_token}"}
    response = requests.post(f"{BASE_URL}/attendance/mark", json=attendance_data, headers=headers_student)
    
    if response.status_code == 201:
        attendance_info = response.json()
        print("✅ Attendance marked successfully")
        print(f"   Status: {attendance_info['status']}")
        print(f"   Distance: {attendance_info['distance']:.2f} meters")
        print(f"   Marked at: {attendance_info['marked_at']}")
    elif response.status_code == 400 and "already marked" in response.json()["detail"]:
        print("ℹ️  Attendance already marked today")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
    
    # Test 8: Get Student's Attendance Records (Lecturer View)
    print("\n--- TEST 8: Get Student Attendance Records (Lecturer) ---")
    response = requests.get(f"{BASE_URL}/attendance/my-attendance", headers=headers_student)
    if response.status_code == 200:
        attendance_records = response.json()
        if attendance_records:
            student_id = attendance_records[0]["student_id"]
            
            # Now get as lecturer
            response = requests.get(f"{BASE_URL}/attendance/student/{student_id}", headers=headers)
            if response.status_code == 200:
                records = response.json()
                print(f"✅ Retrieved {len(records)} attendance record(s)")
                for record in records:
                    print(f"   - {record['class_name']} ({record['class_code']})")
                    print(f"     Status: {record['status']}, Distance: {record['distance']:.2f}m")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
        else:
            print("ℹ️  No attendance records found")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
    
    # Test 9: Get Class Attendance Records (Lecturer View)
    print("\n--- TEST 9: Get Class Attendance Records (Lecturer) ---")
    response = requests.get(f"{BASE_URL}/attendance/class/{class_id}", headers=headers)
    if response.status_code == 200:
        records = response.json()
        print(f"✅ Retrieved {len(records)} attendance record(s) for class")
        for record in records:
            print(f"   - {record['student_name']}")
            print(f"     Status: {record['status']}, Distance: {record['distance']:.2f}m")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
    
    # Test 10: Get My Attendance (Student View)
    print("\n--- TEST 10: Get My Attendance (Student View) ---")
    response = requests.get(f"{BASE_URL}/attendance/my-attendance", headers=headers_student)
    if response.status_code == 200:
        records = response.json()
        print(f"✅ Retrieved {len(records)} attendance record(s)")
        for record in records:
            print(f"   - {record['class_name']} ({record['class_code']})")
            print(f"     Status: {record['status']}, Distance: {record['distance']:.2f}m")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_complete_flow()
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to the API server.")
        print("   Make sure the FastAPI server is running on http://localhost:8000")
        print("   Run: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()