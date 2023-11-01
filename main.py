# python39
# pip install pyrealsense2 opencv-python pyzbar
import datetime
import json

import cv2
import numpy as np
import pyrealsense2 as rs

from cv2_tools import cv2_tools
from mqtt_tools import connect_mqtt, disconnect

client = connect_mqtt()
client.loop_start()

# 初始化QR码检测器
qr_detector = cv2.QRCodeDetector()

# 初始化RealSense相机
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.infrared, 640, 480, rs.format.y8, 30)
pipeline.start(config)

# 获取深度传感器
depth_sensor = pipeline.get_active_profile().get_device().first_depth_sensor()

# 禁用emitter
depth_sensor.set_option(rs.option.emitter_enabled, 0)  # 将0设置为关闭emitter
send_time_second = 0
try:
    while True:
        send_time_second += 1
        # 获取深度数据和彩色图像
        frames = pipeline.wait_for_frames()
        infrared_frame = frames.get_infrared_frame(1)

        if not infrared_frame:
            print("none")
            continue

        # 获取红外数据并进行可视化
        infrared_image = np.asanyarray(infrared_frame.get_data())
        infrared_image = cv2.applyColorMap(cv2.convertScaleAbs(infrared_image), cv2.COLOR_BGR2GRAY)

        # get_apriltag_list_data
        data = cv2_tools.get_apriltag_list_data(infrared_image)
        if len(data) > 0:
            print(f'{datetime.datetime.now()} - have {len(data)} apriltags [{",".join([str(i["tag_id"]) for i in data])}]')
        # print_apriltag_to_image
        cv2_tools.print_apriltag_to_image(infrared_image, data)

        if len(data) > 0 and send_time_second % 30 == 0 and True:
            result = client.publish('python/mqtt', str(data))
            # result: [0, 1]
            status = result[0]
            if status == 0:
                print(f"Send success")
            else:
                print(f"Failed to send message to topic {'python/mqtt'}")

        # 显示图像
        cv2.imshow('Infrared Image', infrared_image)

        # 检查按键，如果按下q，则退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    pipeline.stop()
    cv2.destroyAllWindows()
    disconnect(client)
