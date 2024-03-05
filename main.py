import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
#step - 8...realtime database updation
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancertd-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancertd.appspot.com"
})

bucket = storage.bucket()
#step-1.....to run webcam__start__
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

#step-2....import graphics
imgBackground = cv2.imread('Resources1/background.png')
#list all the modes in for loop to display accordingly
#imoporting the mode images into a list
folderModePath = 'Resources1/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []

for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

#print(len(imgModeList)) #no of images in image folder
#load the encoding file

print("loading encode file........")
file = open('EncodeFile.p', 'rb')
encodelistKnownWithIds = pickle.load(file)
file.close()
encodeListknown, studentIds = encodelistKnownWithIds

#print(studentIds) ...to display id of images
print("encode file loaded...")
#show mode and no of time is display will be given by counter variable
modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:

        #extracted info of encodecurframe go in encoface and facecurframe in faceloc

        for encoFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            #matches the faces from given images or data
            matches = face_recognition.compare_faces(encodeListknown, encoFace)
            #lower the face distance better the matches
            faceDis = face_recognition.face_distance(encodeListknown, encoFace)
            #print("matches", matches)
            #print("faceDis", faceDis)
            matchIndex = np.argmin(faceDis)
            #print("match index of image and person front of webcam__", matchIndex)
            if matches[matchIndex]:

                #print("known face detected")
                #print(studentIds[matchIndex])

                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55+x1, 162+y1, x2-x1, y2-y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]
                print(id)
                #print(id)
                #now after the face has been detected the mode will display one by one with details from db
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1


        if counter!= 0:

            if counter == 1:
                #get the data
                studentInfo = db.reference(f'Students/{id}').get()  #downloading the data from db
                print(studentInfo)
                #get image from the storage
                blob= bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)

                #update data of attendance (realtime)
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed>30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] +=1
                    ref.child('total_attendance').set(studentInfo['total_attendance']) #from AddDataToDatabase file
                    ref.child('last_attendance_tine').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:
                #read and marked done again active foe next attendance
                if 10<counter<20:
                    modeType = 2                  #attendance update window
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                if counter<=10:
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

                    cv2.putText(imgBackground, str(id), (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

                    cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625), cv2.FONT_HERSHEY_COMPLEX, 0.4, (100, 100, 100), 1)

                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.4, (100, 100, 100), 1)

                    cv2.putText(imgBackground, str(studentInfo['starting year']), (1125, 625), cv2.FONT_HERSHEY_COMPLEX, 0.4, (100, 100, 100), 1)
        
                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1 )
                    offset = (414-w)//2                  #code 111 and 112 is for automatically center name of student on total attendance window
                    cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                    #above code is creating problem in launching webcam.....fix it

                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent   #update photo on total atten window

                counter += 1

                if counter>=20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    else:
        modeType = 0
        counter = 0


            #face recognition done step-4....
    cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
#webcam_stop_
