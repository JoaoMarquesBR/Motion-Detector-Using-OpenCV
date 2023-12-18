import cv2, time, pandas
from datetime import datetime
import requests
import sys
import os
import shutil

first_frame = None
status_list = [None,None]
times = []
df=pandas.DataFrame(columns=["Start","End"])

api_url = "http://localhost:3333/message/image?key=memorukey"
phone_number = "15196154641"    

video = cv2.VideoCapture(0)

#video writer object
# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

#clear images
current_directory = os.getcwd()

folder_name = "images"

folder_path = os.path.join(current_directory, folder_name)

try:
    shutil.rmtree(folder_path)
    os.makedirs(folder_path)
    print(f"Contents of {folder_path} cleared.")
except Exception as e:
    print(f"Error clearing {folder_path}: {e}")


counter_value = 900
counter =0 ; 
counter_loop =0;
while True:
    check, frame = video.read()
    status = 0
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray,(21,21),0)

    if first_frame is None or counter >= counter_value:
        print("assigning first_frame")
        first_frame=gray
        counter = 0;
        continue

    delta_frame=cv2.absdiff(first_frame,gray)
    thresh_frame=cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
    thresh_frame=cv2.dilate(thresh_frame, None, iterations=2)

    (cnts,_)=cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in cnts:
        if cv2.contourArea(contour) < 10000:
            continue
        status=1

        (x, y, w, h)=cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 3)
     
        data = {
            'id' : phone_number,
            'message' : "There's been moviment in your room",
        }
        try:    
            if counter % 2 is 0 :
                 whatsapp_image = "images/image_"+str(counter)+".jpg";
                 cv2.imwrite(whatsapp_image, frame)
                 files = {
                     'file': (whatsapp_image, open(whatsapp_image, 'rb')),
                     }
                 print("resetting?")
                 counter = counter_value
                #  response = requests.post(api_url, data=data, files=files)
                #  response.raise_for_status()  # Raise an exception for HTTP errors
                 print("POST request successful")
           
        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
        
    status_list.append(status)

    status_list=status_list[-2:]
    
    # if status == 0 :
        # out.release()
        # cv2.destroyAllWindows()        


    if status_list[-1]==1 and status_list[-2]==0:
        times.append(datetime.now())
    if status_list[-1]==0 and status_list[-2]==1:
        times.append(datetime.now())


    # cv2.imshow("Gray Frame",gray)
    # cv2.imshow("Delta Frame",delta_frame)
    # cv2.imshow("Threshold Frame",thresh_frame)
    cv2.imshow("Color Frame",frame)

    key=cv2.waitKey(1)

    if key == ord('q'):
        if status == 1:
            times.append(datetime.now())
        
        if video.isOpened :
            video.release()
            cv2.destroyAllWindows
            sys.exit()
        break

    counter = counter + 1
    counter_loop= counter_loop+ 1

    print(counter_loop)
    
    if counter_loop == 15000:
        files = os.listdir(folder_path)
        for file_name in files:
            file_name = "images/" + file_name
            data = {
                'id' : phone_number,
                'message':"Moviment in your room!"
            }
            files = {
                'file':(file_name,open(file_name,'rb'))
            }
            try:
                response = requests.post(api_url, data=data, files=files)
                response.raise_for_status()  # Raise an exception for HTTP errors
                print("sent image "+ file_name)
            except requests.exceptions.RequestException as e:
                print("Request failed:", e)
        counter_loop = 0
        
       


print(status_list)
print(times)

video.release()
cv2.destroyAllWindows