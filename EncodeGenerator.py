'''step-3...we have to generate data for all those 128 measurements and we have to store it in a file
and that file we will import in face recognition then it will display whether the face has been detected or not'''
import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancertd-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancertd.appspot.com"
})

#importing students images
folderPath = 'Images'
pathList = os.listdir(folderPath)
print(pathList)
imgList = []
studentIds = []
#step-7....add image data to the storage of firebase so that it match face in real time
#start
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])
    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)
#end

    #print(path)
    #print(os.path.splitext(path)[0])
print(studentIds)

#opencv uses BGR and face_recognition uses RGB colors...
def findEncodings(imagesList):
    encodeList = []
    for img in imgList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #convert bgr to rgb
        encode = face_recognition.face_encodings(img)[0] #find encoding if images
        encodeList.append(encode)
    return encodeList

print("Encoding Started...")
encodeListknown = findEncodings(imgList)
encodeListknownWithIds = [encodeListknown, studentIds]
print(encodeListknown)   #encoding data for images in array
print("Encoding complete....")

#generate a pickle file ..nd dump the encoding list into that
file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListknownWithIds, file)
file.close()
print("File saved....")







