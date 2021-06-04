import cv2
import imutils
import numpy as np

cap = cv2.VideoCapture(0)

cv2.namedWindow("Trackbars")
cv2.createTrackbar("L-H", "Trackbars", 0, 180, lambda x:x)
cv2.createTrackbar("L-S", "Trackbars", 0, 255, lambda x:x)
cv2.createTrackbar("L-V", "Trackbars", 0, 255, lambda x:x)
cv2.createTrackbar("U-H", "Trackbars", 0, 180, lambda x:x)
cv2.createTrackbar("U-S", "Trackbars", 0, 255, lambda x:x)
cv2.createTrackbar("U-V", "Trackbars", 0, 255, lambda x:x)

while True:
    _, frame = cap.read()

    l_h = cv2.getTrackbarPos("L-H", "Trackbars")
    l_s = cv2.getTrackbarPos("L-S", "Trackbars")
    l_v = cv2.getTrackbarPos("L-V", "Trackbars")
    u_h = cv2.getTrackbarPos("U-H", "Trackbars")
    u_s = cv2.getTrackbarPos("U-S", "Trackbars")
    u_v = cv2.getTrackbarPos("U-V", "Trackbars")

    lower_color = np.array([l_h, l_s, l_v])
    upper_color = np.array([u_h, u_s, u_v])

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # Contours detection
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)

        if cv2.contourArea(c) > 400:
            x, y, h, w = cv2.boundingRect(c)
            mid_x = int((x + x + w)/2)
            mid_y = int((y + y + h)/2)
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.line(frame, (int(x), 0), (int(x), 480), (0, 255, 0), 3)
            cv2.line(frame, (0, int(y)), (640, int(y)), (0, 255, 0), 3)

    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)

    key = cv2.waitKey(1)
    print(key)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
