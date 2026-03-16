"""Sign language detection using OpenCV and MediaPipe."""

import cv2
import numpy as np

try:
    import mediapipe as mp
except ImportError:
    mp = None

from signbridge.i18n import _

# Mapping of simple hand gestures to Swedish TAKK/TSS signs.
# This is a basic demonstrator mapping finger-count poses to words.
# A production system would use a trained ML model on TAKK datasets.
SIGN_MAP = {
    "open_hand": "Hej",
    "fist": "Stopp",
    "thumb_up": "Bra",
    "peace": "Tack",
    "pointing": "Du",
    "three_fingers": "Jag",
    "four_fingers": "Vi",
    "pinch": "Liten",
}


class SignDetector:
    """Detects hand signs from camera frames using MediaPipe."""

    def __init__(self):
        self._cap = None
        self._hands = None
        self._mp_hands = None
        self._mp_draw = None
        self._last_sign = None
        self._stable_count = 0
        self._confirmed_sign = None

        if mp is not None:
            self._mp_hands = mp.solutions.hands
            self._mp_draw = mp.solutions.drawing_utils

    def start_camera(self, device_index=0):
        """Open the camera. Returns True on success."""
        self._cap = cv2.VideoCapture(device_index)
        if not self._cap.isOpened():
            self._cap = None
            return False

        if self._mp_hands is not None:
            self._hands = self._mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.6,
                min_tracking_confidence=0.5,
            )
        return True

    def stop_camera(self):
        """Release camera and MediaPipe resources."""
        if self._hands:
            self._hands.close()
            self._hands = None
        if self._cap:
            self._cap.release()
            self._cap = None
        self._last_sign = None
        self._stable_count = 0
        self._confirmed_sign = None

    def process_frame(self):
        """Capture and process one frame.

        Returns:
            (frame_rgb, detected_sign) — frame_rgb is a numpy array (RGB)
            suitable for display; detected_sign is a string or None.
        """
        if self._cap is None or not self._cap.isOpened():
            return None, None

        ret, frame = self._cap.read()
        if not ret:
            return None, None

        frame = cv2.flip(frame, 1)  # mirror
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        detected_sign = None

        if self._hands is not None:
            results = self._hands.process(frame_rgb)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks on frame
                    self._mp_draw.draw_landmarks(
                        frame_rgb,
                        hand_landmarks,
                        self._mp_hands.HAND_CONNECTIONS,
                    )
                    gesture = self._classify_gesture(hand_landmarks)
                    if gesture:
                        sign_text = SIGN_MAP.get(gesture)
                        if sign_text:
                            detected_sign = sign_text

        # Stabilization: require same sign for several consecutive frames
        if detected_sign == self._last_sign:
            self._stable_count += 1
        else:
            self._last_sign = detected_sign
            self._stable_count = 1

        if self._stable_count >= 5 and detected_sign:
            if detected_sign != self._confirmed_sign:
                self._confirmed_sign = detected_sign
                return frame_rgb, detected_sign

        return frame_rgb, None

    def _classify_gesture(self, hand_landmarks):
        """Classify a hand pose into a named gesture using landmark positions."""
        lm = hand_landmarks.landmark

        # Finger tip and pip indices
        tips = [4, 8, 12, 16, 20]  # thumb, index, middle, ring, pinky
        pips = [3, 6, 10, 14, 18]

        fingers_up = []

        # Thumb: compare x position (tip vs ip joint) — works for right hand
        if lm[tips[0]].x < lm[pips[0]].x:
            fingers_up.append(True)
        else:
            fingers_up.append(False)

        # Other fingers: tip above pip means extended
        for i in range(1, 5):
            fingers_up.append(lm[tips[i]].y < lm[pips[i]].y)

        count = sum(fingers_up)
        thumb, index, middle, ring, pinky = fingers_up

        # Pinch: thumb and index close together, others down
        thumb_tip = np.array([lm[4].x, lm[4].y])
        index_tip = np.array([lm[8].x, lm[8].y])
        pinch_dist = np.linalg.norm(thumb_tip - index_tip)

        if pinch_dist < 0.05 and count <= 2:
            return "pinch"

        if count == 0:
            return "fist"
        elif count == 5:
            return "open_hand"
        elif thumb and not index and not middle and not ring and not pinky:
            return "thumb_up"
        elif not thumb and index and not middle and not ring and not pinky:
            return "pointing"
        elif not thumb and index and middle and not ring and not pinky:
            return "peace"
        elif count == 3 and index and middle and ring:
            return "three_fingers"
        elif count == 4 and not thumb:
            return "four_fingers"

        return None
