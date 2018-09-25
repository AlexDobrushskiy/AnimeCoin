import sys

from masternode_prototype.masternode_modules.animecoin_modules.animecoin_nsfw import NSFWDetector


if __name__ == "__main__":
    image_file = sys.argv[1]
    image_data = open(image_file, 'rb').read()
    print("Image is nsfw: %s" % NSFWDetector.is_nsfw(image_data))
