import cv2
import math
import wave
from tqdm import tqdm
import argparse

class DefinedValues:
    def __init__(self):
        self.carrier = 2400
        self.baud = 4160
        self.oversample = 3
        self.sample_rate = self.baud * self.oversample
        self.max_width = 910
        self.max_height = 1270
        self.sync_a = "000011001100110011001100110011000000000"
        self.sync_b = "000011100111001110011100111001110011100"

    def map_value(self, value, f1, t1, f2, t2):
        return f2 + ((t2 - f2) * (value - f1)) / (t1 - f1)

class EncodeImages(DefinedValues):
    def __init__(self, output_wav="output.wav"):
        super().__init__()
        self.image_1 = None
        self.image_2 = None
        self.image_1_width = None
        self.image_1_height = None
        self.image_2_width = None
        self.image_2_height = None
        self.sample_counter = 0
        self.wav_file = wave.open(output_wav, 'wb')
        self.wav_file.setnchannels(1)
        self.wav_file.setsampwidth(1)
        self.wav_file.setframerate(self.sample_rate)

    def close_wav(self):
        self.wav_file.close()

    def input_images(self, image_path_1: str = None, image_path_2: str = None) -> bool:
        try:
            if image_path_1 is not None:
                self.image_1 = cv2.imread(image_path_1, cv2.IMREAD_GRAYSCALE)
            if image_path_2 is not None:
                self.image_2 = cv2.imread(image_path_2, cv2.IMREAD_GRAYSCALE)
            else:
                self.image_2 = self.image_1.copy() if self.image_1 is not None else None

            return self.image_1 is not None
        except Exception as error:
            print(f"Failed to load images. Error: {error}")
            return False

    def resize_image(self, cv2_image):
        h, w = cv2_image.shape
        if w > self.max_width:
            scaling_factor = self.max_height / float(h)
            if self.max_width / float(w) < scaling_factor:
                scaling_factor = self.max_width / float(w)
            cv2_image = cv2.resize(cv2_image, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)
        return cv2_image

    def get_image_res(self):
        try:
            if self.image_1 is None:
                print("Error: Image 1 is not loaded properly.")
                return False
            if self.image_2 is None:
                print("Warning: Image 2 is not provided, using Image 1 as a fallback.")
                self.image_2 = self.image_1.copy()

            self.image_1 = self.resize_image(self.image_1)
            self.image_2 = self.resize_image(self.image_2)

            self.image_1_height, self.image_1_width = self.image_1.shape
            self.image_2_height, self.image_2_width = self.image_2.shape

            return True
        except Exception as error:
            print(f"Failed to get resolution: {error}")
            return False

    def write_audio_value(self, value: int):
        for _ in range(self.oversample):
            samp = math.sin(self.carrier * 2.0 * math.pi * (self.sample_counter / self.sample_rate))
            samp *= self.map_value(value, 0, 255, 0.0, 0.7)

            audio_sample = int(self.map_value(samp, -1.0, 1.0, 0, 255))
            self.wav_file.writeframes(bytes([audio_sample]))
            self.sample_counter += 1

    def get_pixel(self, cv2_image, x, y):
        if 0 <= x < cv2_image.shape[1] and 0 <= y < cv2_image.shape[0]:
            return int(cv2_image[y, x])
        return 0

    def process_images(self):
        height = max(self.image_1_height, self.image_2_height)
        line = 0

        for line in tqdm(range(height), desc="Processing images"):
            frame_line = line % 128

            for bit in self.sync_a:
                self.write_audio_value(0 if bit == '0' else 255)

            for _ in range(47):
                self.write_audio_value(0)

            for i in range(self.image_1_width):
                self.write_audio_value(self.get_pixel(self.image_1, i, line) if line < self.image_1_height else 0)

            for _ in range(45):
                wedge = frame_line // 8
                v = 0
                if wedge < 8:
                    wedge += 1
                    v = int(255 * ((wedge % 8) / 8.0))
                self.write_audio_value(v)

            for bit in self.sync_b:
                self.write_audio_value(0 if bit == '0' else 255)

            for _ in range(47):
                self.write_audio_value(0)

            for i in range(self.image_2_width):
                self.write_audio_value(self.get_pixel(self.image_2, i, line) if line < self.image_2_height else 0)

            for _ in range(45):
                wedge = frame_line // 8
                v = 0
                if wedge < 8:
                    wedge += 1
                    v = int(255 * ((wedge % 8) / 8.0))
                self.write_audio_value(v)

        self.close_wav()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encode images into APT signal")
    parser.add_argument("first_image", type=str, help="Path to the first image")
    parser.add_argument("second_image", type=str, nargs='?', default="", help="Path to the second image (optional)")
    parser.add_argument("output_wav", type=str, help="Output WAV file name")

    args = parser.parse_args()

    obj = EncodeImages(output_wav=args.output_wav)

    if obj.input_images(image_path_1=args.first_image, image_path_2=args.second_image):
        obj.get_image_res()
        obj.process_images()
        print(f"APT signal saved as {args.output_wav}")
