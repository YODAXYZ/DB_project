from datetime import datetime
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import VideoStream

import numpy as np
import imutils
import time
import cv2
import os


class MaskVideo:
	def __init__(self, face='face_detector', model='mask_detector.model', confidence=0.5):
		self.tools = {
			'face': face,
			'model': model,
			'confidence': confidence
		}
		
	def detect_and_predict_mask(self, frame, faceNet, maskNet):
		(h, w) = frame.shape[:2]
		blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300),
									 (104.0, 177.0, 123.0))
	
		faceNet.setInput(blob)
		detections = faceNet.forward()
	
		faces = []
		locs = []
		preds = []
	
		for i in range(0, detections.shape[2]):
			confidence = detections[0, 0, i, 2]
	
			if confidence > self.tools["confidence"]:
				box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
				(startX, startY, endX, endY) = box.astype("int")
	
				(startX, startY) = (max(0, startX), max(0, startY))
				(endX, endY) = (min(w - 1, endX), min(h - 1, endY))
	
				# resize it to 224x224, and preprocess it
				face = frame[startY:endY, startX:endX]
				face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
				face = cv2.resize(face, (224, 224))
				face = img_to_array(face)
				face = preprocess_input(face)
	
				faces.append(face)
				locs.append((startX, startY, endX, endY))
	
		if len(faces) > 0:
			faces = np.array(faces, dtype="float32")
			preds = maskNet.predict(faces, batch_size=32)
	
		return (locs, preds)

	def run(self):
		prototxt = os.path.sep.join([self.tools["face"], "deploy.prototxt"])
		weights = os.path.sep.join([self.tools["face"],
										"res10_300x300_ssd_iter_140000.caffemodel"])
		faceNet = cv2.dnn.readNet(prototxt, weights)

		maskNet = load_model(self.tools["model"])

		vs = VideoStream(src=0).start()
		time.sleep(2.0)
		status_obj = 0
		count = 0

		while True:
			now = datetime.now()
			dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
			frame = vs.read()
			frame = imutils.resize(frame, width=1080)

			(locs, preds) = self.detect_and_predict_mask(frame, faceNet, maskNet)

			for (box, pred) in zip(locs, preds):
				count += 1
				(startX, startY, endX, endY) = box
				(mask, withoutMask) = pred

				label = "Mask" if mask > withoutMask else "No Mask"

				if mask < withoutMask:
					status_obj += 1
				else:
					status_obj -= 1
				if status_obj == 100:
					status_obj = 0
				if status_obj < 0:
					status_obj = 0

				print(status_obj)

				if mask < withoutMask and status_obj == 90:
					cv2.imwrite(f"intruder/indtruder_{dt_string}.jpg", frame)

				color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

				label = "{}".format(label)

				cv2.putText(frame, label, (startX, startY - 10),
							cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
				cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

			cv2.imshow("Frame", frame)
			key = cv2.waitKey(1) & 0xFF

			if key == ord("q"):
				break

		cv2.destroyAllWindows()
		vs.stop()


if __name__ == '__main__':
	maskVideo = MaskVideo()
	maskVideo.run()