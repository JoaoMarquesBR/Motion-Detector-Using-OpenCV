import cv2, time, pandas
from datetime import datetime
import requests
import sys

first_frame = None
status_list = [None,None]
times = []
df=pandas.DataFrame(columns=["Start","End"])

api_url = "http://10.0.0.54:3333/message/image?key=memorukey"
phone_number = "15196154641"    

video = cv2.VideoCapture(1)

#video writer object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))


while True:
    check, frame = video.read()
    status = 0
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray,(21,21),0)

    if first_frame is None:
        first_frame=gray
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
            print("printing image")
            whatsapp_image = 'image.jpg'
            # whatsapp_image = "D:\$$FanshaweServer\ENGLISH\WhatsApp Image 2023-12-07 at 11.02.41 AM(1).jpeg"
            cv2.imwrite(whatsapp_image, frame)
            whatsapp_file = {'file': open(whatsapp_image, 'rb')}
            out.write(frame)
            curl_command = [
                'curl',
                '-X', 'POST',
                '-F', f"id={phone_number}",
                '-F', f"message=There's been movement in your room",
                '-F', f"file=@{whatsapp_image}",
                api_url
                ]
            # result = subprocess.run(curl_command, capture_output=True, text=True, check=True)

        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
    

        
    status_list.append(status)

    status_list=status_list[-2:]
    
    if status == 0 :
        out.release()
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

print(status_list)
print(times)

video.release()
cv2.destroyAllWindows