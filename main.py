import cv2
import math

class DefinedValues:
    def __init__(self):
        self.carrier = 2400
        self.baud = 4160
        self.oversample = 3
        self.max_width = 910
        self.sync_a = "000011001100110011001100110011000000000"
        self.sync_b = "000011100111001110011100111001110011100"
        self.max_height = 1270
class EncodeImages(DefinedValues):
    def __init__(self):
        super().__init__()        
        self.image_1 = None
        self.image_2 = None
        self.image_1_width = None
        self.image_1_height = None
        self.image_2_width = None
        self.image_2_height = None

    def input_images(self,image_path_1:str=None,image_path_2:str=None) -> bool:
        try:
            if image_path_1 is not None:
                self.image_1 = cv2.imread(image_path_1)
                self.image_2 = cv2.imread(image_path_1)
            if image_path_2 is not None:
                self.image_2 = cv2.imread(image_path_2)
            return True
        except Exception as error:
            print(f'Failed to load images. error : {error}')
            return False
    def resize_image(self,cv2_image):
        h,w,_ = cv2_image.shape
        if w > self.max_width:
            scaling_factor = self.max_height / float(h)
            if self.max_width/float(w) < scaling_factor:
                scaling_factor = self.max_width / float(w)
            # resize image
            cv2_image = cv2.resize(cv2_image, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)
        return cv2_image
    def get_image_res(self):
        try:
            self.image_1 = self.resize_image(self.image_1)
            self.image_2 = self.resize_image(self.image_2)
            self.image_1_height, self.image_1_width, _ = self.image_1.shape
            self.image_2_height, self.image_2_width, _ = self.image_2.shape
            cv2.imshow('ex',self.image_1)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except Exception as error:
            print(f'Failed to get res : {error}')
            return False

    def write_audio_value(value:int):
        sn = 0
        for i in range(0,self.oversample):
            samp = math.sin(self.carrier * 2.0 * math.pi * (sn/(self.baud * self.oversample)))
            samp *= math.map(value,0,255,0.0,0.7) # recheck
            # uint8_t buf[1];
            # buf[0] = map(samp, -1.0, 1.0, 0, 255);
            # fwrite(buf, 1, 1, stdout);
    def get_pixel(self,cv2_image,x,y):
        return cv2_image[x,y]
        # pass
first_image = "./test_img/test.png"
second_image = ""
obj = EncodeImages()
obj.input_images(image_path_1=first_image)
obj.get_image_res()

height = max(obj.image_1_height,obj.image_2_height)

line = 0

while line < height:
    frame_line = line % 128

    line=+1
    # sync A
    for i in range(0,len(DefinedValues().sync_a)):
        obj.write_audio_value(0 if DefinedValues().sync_a[i] == '0' else 255)
    # space A
    for i in range(0,47):
        obj.write_audio_value(0)
    # Image A
    for i in range(0,obj.image_1_width):
        if line < obj.image_1_height:
            obj.write_audio_value(obj.get_pixel(i,line))
        else:
            obj.write_audio_value(0)
    # Telemetry A
    for i in range(0,45):
        wedge = frame_line / 8
        v = 0
        if wedge < 8:
            wedge+=1
            v = 255*(wedge % 8 / 8)
        obj.write_audio_value(v)
    # sync B
    for i in range(0,len(DefinedValues().sync_b)):
        obj.write_audio_value(0 if DefinedValues().sync_b[i] == '0' else 255)
    # space B
    for i in range(0,47):
        obj.write_audio_value(0)
    # Image B
    for i in range(0,obj.image_2_width):
        if line < obj.image_2_height:
            obj.write_audio_value(obj.get_pixel(i,line))
        else:
            obj.write_audio_value(0)
    # Telemetry B
    for i in range(0,45):
        wedge = frame_line / 8
        v = 0
        if wedge < 8:
            wedge+=1
            v = 255*(wedge % 8 / 8)
        obj.write_audio_value(v)
        
