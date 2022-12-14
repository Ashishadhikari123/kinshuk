# import and install dependencies
# pip install tensorflow opencv-python mediapipe sklearn matplotlib

import cv2
import numpy as np
import os
from matplotlib import pyplot as plt
import time
import mediapipe as mp

# keypoints using MP Holistic

mp_holistic = mp.solutions.holistic  # Holistic model
mp_drawing = mp.solutions.drawing_utils  # Drawing utilities


def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # COLOR CONVERSION BGR 2 RGB
    image.flags.writeable = False  # Image is no longer writeable
    results = model.process(image)  # Make prediction
    image.flags.writeable = True  # Image is now writeable
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # COLOR COVERSION RGB 2 BGR
    return image, results


def draw_landmark(image, results):
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_TESSELATION)  # Draw face mesh
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS)  # Draw face connections
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)  # Draw pose connections
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks,
                              mp_holistic.HAND_CONNECTIONS)  # Draw left hand connections
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks,
                              mp_holistic.HAND_CONNECTIONS)  # Draw right hand connections


def draw_styled_landmarks(image, results):
    # Draw face mesh
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_TESSELATION,
                              mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
                              mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1)
                              )
    # Draw face connections
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS,
                              mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
                              mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1)
                              )
    # Draw pose connections
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2)
                              )
    # Draw left hand connections
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2)
                              )
    # Draw right hand connections
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                              )


cap = cv2.VideoCapture(0)
# Set mediapipe model
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():
        # Read feed
        ret, frame = cap.read()

        # make detections
        image, results = mediapipe_detection(frame, holistic)
        print(results)

        # draw landmarks
        # draw_landmark(image,results)
        draw_styled_landmarks(image, results)

        # Show to screen
        cv2.imshow('Sign Language Detection Feed', image)

        # Break gracefully
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


# Extract Key Points

def extract_keypoints(results):
    '''
    # handling error if the landmark doesn't exist ,
    # so if it doesn't exist then we will give it empty values
    # as it will be easier for our Nural Network Model to handel the data efficiently.
    # and flattening the data to maintain the format
    '''
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in
                     results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33 * 4)
    face = np.array([[res.x, res.y, res.z] for res in
                     results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468 * 3)
    lh = np.array([[res.x, res.y, res.z] for res in
                   results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21 * 3)
    rh = np.array([[res.x, res.y, res.z] for res in
                   results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(
        21 * 3)
    return np.concatenate([pose, face, lh, rh])

'''
 print(extract_keypoints(results).shape)
 1662 values = 468*3 + 33*4 + 21*3 + 21*3
               face    pose   lh     rh   values of the flattened arrays
'''

# SETUP FOLDERS FOR COLLECTION

# path for exported data,numpy arrays
DATA_PATH = os.path.join('MP_Data')

# action that we try to detect
actions = np.array(['Hello', 'Thanks', 'I_Love_You', 'Like'])

'''
 actions = np.array(['Hello','Thanks','I_Love_You','Like','DisLike','Me','See_You_Later','Father','Mother','Yes','No','Help','Please','Thank_You','Want','What','Dog','Cat','Again_Or_Repeat','EatFood','Milk','More','GoTo','Bathroom','Fine','Like','Learn','Sign','Finish_Or_Done','Name','How'])
 using 30 frames to training for our action detection model  i.e., (30*30*4*1662) frames  for a single action
                                                                   (videos * frames * actions * key-points)
'''
# 30 videos worth of data
no_sequences = 30
# videos are going to be 30 frames in length
sequence_length = 30

# creating  different folders for different sequences
for action in actions:
    for sequence in range(no_sequences):
        try:
            os.makedirs(os.path.join(DATA_PATH, action, str(sequence)))
        except:
            pass

# COLLECTING KEY POINTS VALUES FOR TRAINING AND TESTING
'''
cap = cv2.VideoCapture(0)
# Set mediapipe model
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    # NEW loop
    # loop through actions
    for action in actions:
        # loop through sequences a.k.a. videos
        for sequence in range(no_sequences):
            # loop through video length a.k.a. sequence length
            for frame_num in range(sequence_length):
                # Read feed
                ret, frame = cap.read()

                # make detections
                image, results = mediapipe_detection(frame, holistic)
                print(results)

                # draw landmarks
                # draw_landmark(image,results)
                draw_styled_landmarks(image, results)

                # NEW Apply wait logic
                if frame_num == 0:
                    cv2.putText(image, 'STARTING COLLECTION', (120, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 4,
                                cv2.LINE_AA)
                    cv2.putText(image, 'Collecting frames for {} Video Number {}'.format(action, sequence), (15, 12),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                    # Show to screen
                    cv2.imshow('Sign Language Detection Feed', image)
                    cv2.waitKey(500)
                else:
                    cv2.putText(image, 'Collecting frames for {} Video Number {}'.format(action, sequence), (15, 12),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                    # Show to screen
                    cv2.imshow('Sign Language Detection Feed', image)

                # NEW Export keypoints
                keypoints = extract_keypoints(results)
                npy_path = os.path.join(DATA_PATH, action, str(sequence), str(frame_num))
                np.save(npy_path, keypoints)

                # Show to screen
                cv2.imshow('Sign Language Detection Feed', image)

                # Break gracefully
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
    cap.release()
    cv2.destroyAllWindows()
'''
cap.release()
cv2.destroyAllWindows()
# PREPROCESS DATA AND CREATE LABLES AND FEATURES

from sklearn.model_selection import train_test_split  # Help partation training data from training data and testing data
from keras.utils.np_utils import to_categorical       # convert your data into one hot talbel data

# create label data

label_map = {label: num for num, label in enumerate(actions)}
''' 

'''
# bringing in the data
sequences, labels = [], []
for action in actions:
    for sequence in range(no_sequences):
        window = []
        for frame_num in range(sequence_length):
            res = np.load(os.path.join(DATA_PATH, actions, str(sequence), "{}.np".format(frame_num)))
            window.append(res)
        sequences.append(window)
        labels.append(label_map[action])

X = np.array(sequences)
Y = to_categorical(labels).astype(int)

X_train,X_test,Y_train,Y_test=train_test_split(X,Y,test_size=0.05)

# BUILD AND TRAIN LSTM NEURAL NETWORK

from keras.models import Sequential
from keras.layers import LSTM, Dense
from keras.callbacks import TensorBoard

log_dir=os.path.join('Logs')
tb_callback=TensorBoard(log_dir=log_dir)

model = Sequential()
model.add(LSTM(64, return_sequences=True, activation='relu', input_shape=(30,1662)))
model.add(LSTM(128, return_sequences=True, activation='relu'))
model.add(LSTM(64, return_sequences=False, activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(actions.shape[0], activation='softmax'))

'''

res=[.7,.2,.1,.5]               currently has 4 values as there are currently only 4 values to detect i.e., 'Hello', 'Thanks', 'I_Love_You', 'Like'  : Its called multiple class classification model 
actions[np.argmax(res)]         the result will be hello as it has the highest probability


we used LSTM as it has the highest accuracy and it does not have multiple stacked neural networks 
less data required 
faster to train 
faster detection

'''
model.compile(optimizer='Adam',loss='categorical_crossentropy',metrics=['categorical_accuracy'])
model.fit(X_train,Y_train,epochs=2000,callbacks=[tb_callback])

model.summary()




