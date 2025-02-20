import cv2

class DefinedValues:
    def __init__(self):
        self.carrier = 2400
        self.baud = 4160
        self.oversample = 3

        self.sync_a = "000011001100110011001100110011000000000"
        self.sync_b = "000011100111001110011100111001110011100"

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
    def get_image_res(self):
        try:
            self.image_1_height, self.image_1_width, _ = self.image_1.shape
            self.image_2_height, self.image_2_width, _ = self.image_2.shape

        except Exception as error:
            print(f'Failed to get res : {error}')
            return False

first_image = "./test_img/test.png"
second_image = ""

EncodeImages().input_images(image_path_1=first_image)
