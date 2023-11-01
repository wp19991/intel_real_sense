# python39
# pip install pyrealsense2 opencv-python pyzbar
# linux:pip install apriltag
# win:pip install pupil-apriltags
import apriltag
import cv2
from pyzbar.pyzbar import decode


class cv2_tools:
    @staticmethod
    def read_image(file_path):
        # 读取图像
        return cv2.imread(file_path)

    @staticmethod
    def get_qr_list_data(image):
        # 检测并解码二维码
        decoded_objects = decode(image)
        res = []
        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            # 获取二维码边界框的坐标
            points = obj.polygon
            points = [[point[0], point[1]] for point in points]
            res.append({'data': data,
                        'points': points})
        return res

    @staticmethod
    def get_apriltag_list_data(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 创建一个apriltag检测器
        at_detector = apriltag.Detector(apriltag.DetectorOptions(families='tag36h11'))
        # 进行apriltag检测，得到检测到的apriltag的列表
        tags = at_detector.detect(gray)
        res = []
        for tag in tags:
            res.append({"tag_id": tag.tag_id,
                        "decision_margin": tag.decision_margin,
                        "homography": [list(p) for p in tag.homography],
                        "center": list(tag.center.astype(int)),
                        "points": [list(tag.corners[0].astype(int)), list(tag.corners[1].astype(int)),
                                   list(tag.corners[2].astype(int)), list(tag.corners[3].astype(int))]}
                       )
        return res

    @staticmethod
    def print_apriltag_to_image(image, apriltag_list_data):
        if len(apriltag_list_data) > 0:
            for img_data in apriltag_list_data:
                cv2.putText(image, str(img_data['tag_id']), tuple(img_data['center']),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA, False)
                cv2.circle(image, tuple(img_data['points'][0]), 4, (255, 0, 0), 2)
                cv2.circle(image, tuple(img_data['points'][1]), 4, (255, 0, 0), 2)
                cv2.circle(image, tuple(img_data['points'][2]), 4, (255, 0, 0), 2)
                cv2.circle(image, tuple(img_data['points'][3]), 4, (255, 0, 0), 2)


if __name__ == "__main__":
    image = cv2_tools.read_image('./qr.png')
    data = cv2_tools.get_qr_list_data(image)
    print(len(data), data)
    image = cv2_tools.read_image('./apriltag-1.png')
    data = cv2_tools.get_apriltag_list_data(image)
    print(len(data), data)
