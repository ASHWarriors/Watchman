def isAlertedBefore(now, before):
    from datetime import timedelta
    return (now - before)  >= timedelta(minutes=10)


def checkViolence(violence_grade):
    return violence_grade >= 0.96

def getLocation():
    import requests
    res = requests.get("https://ipinfo.io/")
    data = res.json()
    city = data["city"]
    state = data["region"]
    location = data["loc"].split(",")
    lat = location[0]
    log = location[1]
    return str(lat) + ',' +  str(log)

def alertAuthorities():
    import pywhatkit as kit
    import keyboard as k
    import time
    from datetime import datetime, timedelta
    import pyautogui
    link = "http://www.google.com/maps/place/" + getLocation()
    t = str(datetime.now() + timedelta(seconds=90))
    hour, minute = t[11:13], t[14:16]
    if hour[0] == "0":
        hour = hour[1]
    if minute[0] == "0":
        minute = minute[1]
    hour, minute = int(hour), int(minute)
    message = f"""🚨🛑 *Emergency* 🛑🚨 A person is in emergency and need your help immediately. Click the link below for location {link}"""
    kit.sendwhatmsg('+91XXXXXXXXXX', message, hour, minute, 30)
    pyautogui.click(1050, 950)
    time.sleep(2)
    k.press_and_release('enter')



def detect():
    from keras.models import load_model
    import cv2
    import numpy as np
    import os
    from datetime import datetime, timedelta

    model = load_model(os.path.join(os.getcwd(), 'model-best'))

    cap = cv2.VideoCapture('violence1.mp4')
    threshold = 10
    bankOfFrames = []
    reshapedFrames = np.zeros((threshold, 227, 227, 1), dtype=np.float)
    numFrames = 0
    prediction = [[0, 0]]
    averages = [-1] * threshold
    i = 0
    before = datetime.now() - timedelta(minutes=10)
    while True:
        status, frame = cap.read()
        grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resizedFrame = cv2.resize(grayFrame, (227, 227))
        reshapedFrame = np.reshape(resizedFrame, (227, 227, 1))
        if numFrames > threshold:
            reshapedFrames = np.asarray(bankOfFrames)
            bankOfFrames = []
            prediction = model.predict(reshapedFrames)
            reshapedFrames = np.zeros((threshold, 227, 227, 1), dtype=np.float)
            numFrames = 0
        else:
            bankOfFrames.append(reshapedFrame)
            numFrames += 1
        average_prediction = np.mean(prediction, axis=0)[1]

        if i < threshold:
            averages[i] = average_prediction
            i += 1
        else:
            isExtreme = checkViolence(sum(averages) / threshold)
            if isExtreme and isAlertedBefore(datetime.now(), before):
                alertAuthorities()
                before = datetime.now()
            i = 0

        cv2.putText(frame, 'Violent Grade: ' + str(average_prediction), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (57, 235, 143), 2)
        
        cv2.imshow("Live-Feed", frame)
        if cv2.waitKey(1) & 0xFF==ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
