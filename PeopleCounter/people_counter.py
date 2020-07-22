#python people_counter.py --prototxt Objects.prototxt.txt --model Objects.caffemodel --dir cctv.mp4


#importing all the packages
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
import datetime
import matplotlib.pyplot as plt
import csv
import threading

attt = 0
stop_thread = False

def detector():
	global attt, stop_thread
	ap = argparse.ArgumentParser()
	ap.add_argument("-p", "--prototxt", required=True,
		help="path to Caffe 'deploy' prototxt file")
	ap.add_argument("-m", "--model", required=True,
		help="path to Caffe pre-trained model")
	ap.add_argument("-c", "--confidence", type=float, default=0.2,
		help="minimum probability to filter weak detections")
	ap.add_argument("-d", "--dir", default="cctv.mp4",
		help="directory of video test file")
	args = vars(ap.parse_args())

	CLASSES = ["", "", "", "", "",
		"", "", "", "", "", "", "",
		"", "", "", "person", "", "",
		"", "", ""]
	color = np.random.uniform(200,200,200)
	print("[INFO] loading model...")
	net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
	print("[INFO] starting video stream...")
	file = args['dir']
	filetype = file.rsplit(".")[-1]
	if filetype in ['jpg','png']:
		vs = cv2.imread(file)
	elif filetype == "mp4":
		vs = cv2.VideoCapture(file)
	
	time.sleep(2.0)
	fps = FPS().start()

	personId = []
	f = open("data.csv","w+",newline='')
	# attt=0
	t = time.strftime("%I:%M:%S")
	t.strip("2019-12-11")
	pltime=str(t)
	pltime=pltime.split(':')
	mm=int(pltime[1])
	timecheck=mm

	while True:
		t = time.strftime("%I:%M:%S")
		t.strip("2019-12-11")

		pltime=str(t)
		pltime=pltime.split(':')
		hh=int(pltime[0])
		mm=int(pltime[1])

		pid = 0
		personId.clear()
		if filetype in ['jpg','png']:
			frame = vs
		elif filetype == "mp4":
			(grabbed, frame) = vs.read()
		frame = imutils.resize(frame, width=900)

		(h, w) = frame.shape[:2]
		blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
			0.007843, (300, 300), 127.5)

		# predictions:
		net.setInput(blob)
		detections = net.forward()

		for i in np.arange(0, detections.shape[2]):
			confidence = detections[0, 0, i, 2]
			if confidence > args["confidence"]:
				idx = int(detections[0, 0, i, 1])
				box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
				(startX, startY, endX, endY) = box.astype("int")
				#labeling the pesron with id
				label = "id = {} {}".format(pid, CLASSES[idx])
				pid += 1
				personId.append(pid)
				personId.sort()

				cv2.rectangle(frame, (startX, startY), (endX-100, endY),
					color[idx], 2)
				centerX = (startX+endX)//2
				centerY = (startY+endY)//2
				coord = (centerX, centerY)

				y = startY - 15 if startY - 15 > 15 else startY + 15
				cv2.putText(frame, label, (startX, y),
					cv2.FONT_HERSHEY_SIMPLEX, 0.5, color[idx], 2)
                
				try:
					attt+=personId[-1]
				except IndexError:
					pass
				# file writing
				if True:
					try:
						print(mm)
						writer = csv.writer(f)
						writer.writerow([str(hh)+":"+str(mm), int(attt/484)])
						attt=0
						timecheck=mm
						print("last tc: "+str(mm))
					except IndexError:
						personId.clear()
						personId.append(0)
		text = "Total Count: {}".format(len(personId))
		cv2.putText(frame, text, (10, 70 - ((1 * 20) + 20)),
		cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)               
                
		# show the output frame
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF

		if key == ord("q"):
			print("Final pid: "+str(personId))
			break

		# update the FPS counter
		fps.update()

	#stop the timer and display FPS information
	fps.stop()
	print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
	print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
	stop_thread = True
	result.release() 
	vs.release()
	cv2.destroyAllWindows()
	vs.stop()

#for storing count of people across time
def log():
	fig = plt.gcf()
	fig.show()
	fig.canvas.draw()

	while not stop_thread:
		time.sleep(60)
		print("Plot updating...")
		x = []
		y = []

		with open("data.csv", 'r') as csvfile:
			plots = csv.reader(csvfile, delimiter=',')
			x.clear()
			y.clear()
			for row in plots:
				x.append(str(row[0]))
				y.append(int(row[1]))

		plt.title('Data from the CSV File: Time vs NUmber of Person')

		plt.xlabel('Time')
		plt.ylabel('Number of People')

		plt.pause(5)
		fig.canvas.draw()

detect_ = threading.Thread(target=detector)
# log_ = threading.Thread(target=log)
detect_.start()
# log_.start()
