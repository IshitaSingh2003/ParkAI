from flask import Flask, render_template, request, session, redirect, url_for
import cv2
import pickle
import cvzone
import numpy as np
import pandas as pd

app = Flask(__name__)
app.secret_key = 'a'

# Dictionary to store user credentials (Replace with your database logic)
user_credentials = {
    "singhishita78@gmail.com": "isha",
    "user2@example.com": "password2",
    # Add more user credentials as needed
}

# Placeholder for storing parking data
parking_data = []

@app.route('/')
def project():
    return render_template('index.html')

@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/model')
def model():
    return render_template('model.html')

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/aboutus.html')
def aboutus():
    return render_template('aboutus.html')

@app.route('/signup.html')
def signup():
    return render_template('signup.html')

@app.route("/signup", methods=['POST', 'GET'])
def signup1():
    msg = ''
    if request.method == 'POST':
        # Extract user registration data from the form
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Implement your database logic to insert user data (not shown in this code)
        # You can use a database library like SQLAlchemy to interact with your database

        msg = "You have successfully registered!"
    return render_template('login.html', msg=msg)

@app.route("/login", methods=['POST', 'GET'])
def login1():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        # Check if the provided email exists in the user_credentials dictionary
        if email in user_credentials and user_credentials[email] == password:
            session['Loggedin'] = True
            session['id'] = email
            session['email'] = email
            return redirect(url_for('model'))  # Redirect to the model route on successful login
        else:
            msg = "Incorrect Email/password"
            return render_template('login.html', msg=msg)
    else:
        return render_template('login.html')

@app.route('/modelq')
def liv_pred():
    # Video feed
    cap = cv2.VideoCapture('carParkingInput.mp4')
    with open('parkingSlotPosition', 'rb') as f:
        posList = pickle.load(f)
    
    width, height = 107, 48
    parking_data.clear()  # Clear the parking data list before processing

    def checkParkingSpace(imgPro):
        spaceCounter = 0
        for pos in posList:
            x, y = pos
            imgCrop = imgPro[y:y + height, x:x + width]
            count = cv2.countNonZero(imgCrop)
            if count < 900:
                color = (0, 255, 0)
                thickness = 5
                spaceCounter += 1
                status = "Free"
            else:
                color = (0, 0, 255)
                thickness = 2
                status = "Occupied"

            parking_data.append({"Position": pos, "Status": status})

            cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
        cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50), scale=3, thickness=5, offset=20,
                       colorR=(0, 200, 0))

    while True:
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        success, img = cap.read()
        if not success:
            break
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
        imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                             25, 16)
        imgMedian = cv2.medianBlur(imgThreshold, 5)
        kernel = np.ones((3, 3), np.uint8)
        imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)
        checkParkingSpace(imgDilate)
        cv2.imshow("Image", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Save parking data to an Excel file
    parking_df = pd.DataFrame(parking_data)
    parking_df.to_excel("parking_data.xlsx", index=False)

if __name__ == "__main__":
    app.run(debug=True)
