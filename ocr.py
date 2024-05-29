import numpy
from pyautogui import *
from PIL import Image
import numpy as np
from paddleocr import PaddleOCR, draw_ocr
 
def get_curtime(time_format="%Y-%m-%d %H:%M:%S"):
    curTime = time.localtime()
    curTime = time.strftime(time_format, curTime)
    return curTime
 
def ocr_img_text(path="", saveimg=False, printResult=False):
    '''
    图像文字识别
    :param path:图片路径
    :param saveimg:是否把结果保存成图片
    :param printResult:是否打印出识别结果
    :return:result,img_name
    '''
    image = path
 
    # 图片路径为空就默认获取屏幕截图 
    if image == "":
        image = screenshot() #使用pyautogui进行截图操作
        image = np.array(image)
    else:
        # 不为空就打开
        image = Image.open(image).convert('RGB')
 
    ocr = PaddleOCR(use_angle_cls=True, lang="ch")  # need to run only once to download and load model into memory
 
    result = ocr.ocr(image, cls=True)
    result_text = ""
    for line in result:
        for word in line:
            result_text += word[1][0] + "\n"
    if printResult is True:
        print(result_text)
 
    # 识别出来的文字保存为图片
    img_name = "ImgTextOCR-img-" + get_curtime("%Y%m%d%H%M%S") + ".jpg"
    if saveimg is True:
        boxes = [detection[0] for line in result for detection in line]  # Nested loop added
        txts = [detection[1][0] for line in result for detection in line]  # Nested loop added
        scores = [detection[1][1] for line in result for detection in line]  # Nested loop added
        im_show = draw_ocr(image, boxes, txts, scores)
        im_show = Image.fromarray(im_show)
        im_show.save(img_name)
 
    return result_text, img_name

if __name__ == '__main__':
    ocr_img_text(saveimg=False, printResult=True)