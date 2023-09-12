import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendancertd-default-rtdb.firebaseio.com/"

})

ref = db.reference('Students')

data = {
    "474730":
        {
            "name": "Rashmi",
            "major": "CSE(General)",
            "starting year": 2020,
            "total_attendance": 19,
            "standing": "Excellent",
            "year":3,
            "last_attendance_time": "2023-03-08 00:54:34"

        },
    "321654":
        {
            "name": "MW",
            "major": "Robotics",
            "starting year": 2021,
            "total_attendance": 14,
            "standing": "Good",
            "year":2,
            "last_attendance_time": "2023-03-08 00:54:34"

        },
    "852741":
        {
            "name": "Emily",
            "major": "Computer science and Engineering",
            "starting year": 2020,
            "total_attendance": 15,
            "standing": "Good",
            "year":3,
            "last_attendance_time": "2023-03-08 00:54:34"

        },
    "963852":
        {
            "name": "Elon Musk",
            "major": "Computer science and Engineering",
            "starting year": 2020,
            "total_attendance": 24,
            "standing": "Outstanding",
            "year":3,
            "last_attendance_time": "2023-03-08 00:54:34"

        }
}
for key, value in data.items():
    ref.child(key).set(value)
