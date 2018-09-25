import sys

from core_modules.blackbox_modules.nsfw import NSFWDetector


if __name__ == "__main__":
    image_file = sys.argv[1]
    image_data = open(image_file, 'rb').read()
    print("Image is nsfw: %s" % NSFWDetector.is_nsfw(image_data))
