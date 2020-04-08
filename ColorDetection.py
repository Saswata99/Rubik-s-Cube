import cv2
import time
#from urllib.request import urlopen
import requests
import numpy as np


class Camera:
    def __init__(self):
        self.height = 720
        self.width = 1080
        self.middle = (self.width//2 + 100, self.height//2)

        # main cube(center) coordination
        self.main_cube_coordinates = [
            [self.middle[0] - 190, self.middle[1] - 190], [self.middle[0] - 50, self.middle[1] - 190], [self.middle[0] + 90, self.middle[1] - 190],
            [self.middle[0] - 190, self.middle[1] - 50],  [self.middle[0] - 50, self.middle[1] - 50],  [self.middle[0] + 90, self.middle[1] - 50],
            [self.middle[0] - 190, self.middle[1] + 90],  [self.middle[0] - 50, self.middle[1] + 90], [self.middle[0] + 90,  self.middle[1] + 90]
        ]

        # current cube(left-top) coordination
        self.current_cube_coordinates = [
            [50, 60], [94, 60], [138, 60],
            [50, 104], [94, 104], [138, 104],
            [50, 148], [94, 148], [138, 148]
        ]

        # preview cube(left-bottom) coordination
        self.preview_cube_coordinates = [
            [50, 260], [94, 260], [138, 260],
            [50, 304], [94, 304], [138, 304],
            [50, 348], [94, 348], [138, 348]
        ]

        # hsv value for colors
        self.hsv_data = {}

    def name_to_rgb(self, name):
        """
        Convert color name to rgb value
        :param name: name of the color
        :return: rgb value of the color
        """
        color = {
            'red': (0, 0, 255),
            'orange': (0, 165, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'white': (255, 255, 255),
            'yellow': (0, 255, 255)
        }
        return color[name]

    def hsv_to_name(self, hsv):
        """
        Convert hsv value to color name
        :param hsv: hsv value
        :return: color name
        """
        h, s, v = hsv

        if s < 70:
            return 'white'
        elif h > 118 or h < 4:
            return 'red'
        elif h > 75:
            return 'blue'
        elif h > 35:
            return 'green'
        elif h > 16:
            return 'yellow'
        elif h > 3:
            return 'orange'

        return 'white'

    def average_hsv(self, box):
        """
        Calculate average value of hsv
        :param box: list of hsv values
        :return: average hsv value
        """
        h = 0
        s = 0
        v = 0
        num = 0
        for y in range(len(box)):
            if y % 10 == 0:
                for x in range(len(box[y])):
                    if x % 10 == 0:
                        hsv = box[y][x]
                        num += 1
                        h += hsv[0]
                        s += hsv[1]
                        v += hsv[2]
        h /= num
        s /= num
        v /= num
        return int(h), int(s), int(v)

    def draw_main_cube(self, frame):
        """
        Draw main(center) cube
        :param frame: VideoCapture window
        :return: none
        """
        for x, y in self.main_cube_coordinates:
            cv2.rectangle(frame, (x, y), (x + 50, y + 50), (255, 255, 255), 2)

    def draw_current_cube(self, frame, state):
        """
        Draw current(left-top) cube
        :param state: data of a side
        :param frame: VideoCapture window
        :return: none
        """
        for index, (x, y) in enumerate(self.current_cube_coordinates):
            cv2.rectangle(frame, (x, y), (x + 40, y + 40), self.name_to_rgb(state[index]), -1)

    def draw_preview_cube(self, frame, state):
        """
        Draw preview(left-bottom) cube
        :param state: data of a side
        :param frame: VideoCapture window
        :return: none
        """
        for index, (x, y) in enumerate(self.preview_cube_coordinates):
            cv2.rectangle(frame, (x, y), (x + 40, y + 40), self.name_to_rgb(state[index]), -1)

    def color_to_notation(self, color):
        """
        Convert color name to notation of the cube
        By default Green is face color and White is top color
        :param color: color
        :return: notation of the cube
        """
        notation = {
            'green': 'F',
            'white': 'U',
            'blue': 'B',
            'red': 'R',
            'orange': 'L',
            'yellow': 'D'
        }
        return notation[color]

    def get_hsv(self):
        """
        Calibrate colors' hsv value(Use only if color calibration is required)
        You have to manually change hsv value in hsv_to_name function
        :return: none
        """

        # cam = cv2.VideoCapture(0)
        url = "http://192.168.137.88:8080/shot.jpg?rnd=422444"

        flag = False
        end_time = 0
        hsv = []

        while True:
            # _, frame = cam.read()
            # frame = cv2.flip(frame, 1)

            frame = ""
            try:
                response = requests.get(url)
                imgNp = np.array(bytearray(response.content), dtype=np.uint8)
                frame = cv2.imdecode(imgNp, -1)
            except Exception as err:
                print("URL connection don not established properly. Try again")
                exit()

            frame = cv2.resize(frame, (self.width, self.height))

            cv2.rectangle(frame, (200, 120), (300, 220), (255, 255, 255), 2)
            key = cv2.waitKey(10) & 0xff

            if key == 32:
                if not flag:
                    end_time = time.time() + 1    # scan time : 1 sec
                flag = True

            if key == 27:
                break

            if flag:
                box = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)[120:220, 200:300]
                hsv.extend(box)
                if time.time() > end_time:
                    avg_hsv = self.average_hsv(hsv)
                    print(avg_hsv)
                    flag = False
                    hsv.clear()
            cv2.imshow("Color Detection", frame)

        # cam.release()
        cv2.destroyAllWindows()


    def scan(self):
        """
        Scan 6 sides of the cube by camera
        :return: list of notation value of all 6 sides
        """
        url = "http://192.168.137.88:8080/shot.jpg?rnd=422444"

        # cam = cv2.VideoCapture(0)
        # cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        # cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)

        sides = {}
        preview = ['white', 'white', 'white',
                   'white', 'white', 'white',
                   'white', 'white', 'white']
        state = [0, 0, 0,
                 0, 0, 0,
                 0, 0, 0]
        while True:
            # _, frame = cam.read()
            # frame = cv2.flip(frame, 1)

            frame = ""
            try:
                response = requests.get(url)
                imgNp = np.array(bytearray(response.content), dtype=np.uint8)
                frame = cv2.imdecode(imgNp, -1)
            except Exception as err:
                print("URL connection don not established properly. Try again")
                exit()

            frame = cv2.resize(frame, (self.width, self.height))

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            key = cv2.waitKey(10) & 0xff

            self.draw_main_cube(frame)
            self.draw_preview_cube(frame, preview)

            for index, (x, y) in enumerate(self.main_cube_coordinates):
                box = hsv[y:y + 50, x:x + 50]
                avg_hsv = self.average_hsv(box)
                color_name = self.hsv_to_name(avg_hsv)
                state[index] = color_name

            cv2.putText(frame, "Current Side : ", (30, 40), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
            self.draw_current_cube(frame, state)
            cv2.putText(frame, "Last Scanned Side :", (30, 240), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)

            if key == 32:  # Space bar
                face = self.color_to_notation(state[4])
                notation = [self.color_to_notation(color) for color in state]
                if face not in sides:
                    preview = list(state)
                    sides[face] = notation
                    print(f"Side with {face} center is successfully scanned.")
                    print(f"Remaning faces : {6-len(sides)}")
                else:
                    print("Some mistake in scanning the side. Try again")

                if len(sides) == 6:
                    break

            text = 'Scanned sides: {}/6'.format(len(sides))
            cv2.putText(frame, text, (int(self.middle[0]*.7), int(self.middle[1]*1.8)), cv2.FONT_HERSHEY_DUPLEX, .9, (102,255,0), 1, cv2.LINE_AA)

            if key == 27:  # Esc
                print("\nProgramme is terminated('Esc').")
                break
            cv2.imshow("Rubik's Cube", frame)

        # cam.release()
        cv2.destroyAllWindows()
        if len(sides) == 6:
            return sides
        else:
            return False

if __name__ == "__main__":
    camera = Camera()
    camera.get_hsv()
