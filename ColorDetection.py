import cv2
import time
from urllib.request import urlopen
import numpy as np


class Camera:
    def __init__(self):
        # main cube(center) coordination
        self.main_cube_coordinates = [
            [200, 120], [300, 120], [400, 120],
            [200, 220], [300, 220], [400, 220],
            [200, 320], [300, 320], [400, 320]
        ]

        # current cube(left-top) coordination
        self.current_cube_coordinates = [
            [20, 20], [54, 20], [88, 20],
            [20, 54], [54, 54], [88, 54],
            [20, 88], [54, 88], [88, 88]
        ]

        # preview cube(left-bottom) coordination
        self.preview_cube_coordinates = [
            [20, 130], [54, 130], [88, 130],
            [20, 164], [54, 164], [88, 164],
            [20, 198], [54, 198], [88, 198]
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
        if h < 15 and v < 100:
            return 'red'
        if h <= 10 and v > 100:
            return 'orange'
        elif h <= 30 and s <= 100:
            return 'white'
        elif h <= 40:
            return 'yellow'
        elif h <= 85:
            return 'green'
        elif h <= 130:
            return 'blue'

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
            cv2.rectangle(frame, (x, y), (x + 30, y + 30), (255, 255, 255), 2)

    def draw_current_cube(self, frame, state):
        """
        Draw current(left-top) cube
        :param frame: VideoCapture window
        :return: none
        """
        for index, (x, y) in enumerate(self.current_cube_coordinates):
            cv2.rectangle(frame, (x, y), (x + 32, y + 32), self.name_to_rgb(state[index]), -1)

    def draw_preview_cube(self, frame, state):
        """
        Draw preview(left-bottom) cube
        :param frame: VideoCapture window
        :return: none
        """
        for index, (x, y) in enumerate(self.preview_cube_coordinates):
            cv2.rectangle(frame, (x, y), (x + 32, y + 32), self.name_to_rgb(state[index]), -1)

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

        :return:
        """

        #cam = cv2.VideoCapture(0)
        url = "http://192.168.137.34:8080/shot.jpg?rnd=705060"

        flag = False
        end_time = 0
        hsv = []

        while True:
            #_, frame = cam.read()
            #frame = cv2.flip(frame, 1)

            with urlopen(url) as u:
                imgResp = u.read()
            imgNp = np.array(bytearray(imgResp), dtype=np.uint8)
            frame = cv2.imdecode(imgNp, -1)

            cv2.rectangle(frame, (200, 120), (430, 350), (255, 255, 255), 2)
            key = cv2.waitKey(10) & 0xff

            if key == 32:
                if not flag:
                    end_time = time.time() + 1.5    # scan time : 1.5 sec
                flag = True

            if key == 27:
                break

            if flag:
                hsv.extend(cv2.cvtColor(frame, cv2.COLOR_BGR2HSV))
                if time.time() > end_time:
                    avg_hsv = self.average_hsv(hsv)
                    print(avg_hsv)
                    flag = False

            cv2.imshow("Color Detection", frame)

        #cam.release()
        cv2.destroyAllWindows()

    def define_color(self):
        for i in range(10):
            self.get_hsv()

    def scan(self):
        """
        Scan 6 sides of the cube by camera
        :return: list of notation value of all 6 sides
        """
        cam = cv2.VideoCapture(0)
        sides = {}
        preview = [
            'white', 'white', 'white',
            'white', 'white', 'white',
            'white', 'white', 'white'
        ]

        state = [
            0, 0, 0,
            0, 0, 0,
            0, 0, 0
        ]

        while cam.isOpened():
            _, frame = cam.read()
            frame = cv2.flip(frame, 1)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            key = cv2.waitKey(10) & 0xff

            self.draw_main_cube(frame)
            self.draw_preview_cube(frame, preview)

            for index, (x, y) in enumerate(self.main_cube_coordinates):
                box = hsv[y:y + 32, x:x + 32]
                avg_hsv = self.average_hsv(box)
                color_name = self.hsv_to_name(avg_hsv)
                state[index] = color_name

            self.draw_current_cube(frame, state)

            if key == 32:  # Space bar
                preview = list(state)
                self.draw_preview_cube(frame, state)
                face = self.color_to_notation(state[4])
                notation = [self.color_to_notation(color) for color in state]
                if face not in sides:
                    sides[face] = notation
                else:
                    print("You have done some mistake in scanning the sides. Try again")
                    exit()

                if len(sides) == 6:
                    break

            text = 'Scanned sides: {}/6'.format(len(sides))
            cv2.putText(frame, text, (20, 460), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            if key == 27:  # Esc
                break

            cv2.imshow("Rubik's Cube", frame)

        cam.release()
        cv2.destroyAllWindows()
        if len(sides) == 6:
            return sides
        else:
            print("Sorry, you did not scan all 6 sides. Try again")
            exit()


if __name__ == "__main__":
    camera = Camera()
    camera.get_hsv()
""" (63, 156, 185)
(65, 152, 166)
(64, 164, 188)
(97, 159, 212)


(57, 202, 209)


(52, 97, 160)

"""