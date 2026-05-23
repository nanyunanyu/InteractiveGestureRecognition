import os
import sys

os.environ["GLOG_minloglevel"] = "2"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import cv2
import mediapipe as mp
from mediapipe.python._framework_bindings import resource_util


if getattr(sys, "frozen", False):
    resource_util.set_resource_dir(sys._MEIPASS)


class HandTracker:
    def __init__(self):
        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        )

    def process(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb_frame)
        if not results.multi_hand_landmarks or not results.multi_handedness:
            return []

        frame_height, frame_width = frame.shape[:2]
        hands = []

        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            landmarks = []
            for landmark in hand_landmarks.landmark:
                landmarks.append((int(landmark.x * frame_width), int(landmark.y * frame_height)))

            classification = handedness.classification[0]
            hands.append(
                {
                    "label": classification.label,
                    "score": classification.score,
                    "landmarks": landmarks,
                }
            )

        hands.sort(key=lambda hand: sum(point[0] for point in hand["landmarks"]) / len(hand["landmarks"]))
        return hands

    def close(self):
        self._hands.close()
