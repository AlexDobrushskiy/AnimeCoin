import math
import random

from core_modules.blackbox_modules import luby
from core_modules.helpers import require_true

if __name__ == "__main__":
    # SETTINGS
    redundancy_factor = 12  # How many times more blocks should we store than are required to regenerate the file?
    block_size = 1024
    # END

    data = b'A'*1024*512 + b'A'*100  # test for padding

    blocks = luby.encode(redundancy_factor, block_size, data)
    print("Generated %s blocks" % len(blocks))

    sample_size = math.ceil(len(blocks)/redundancy_factor*1.2)
    print("Sample size is %s" % sample_size)

    print("Got %s blocks to reconstruct data" % sample_size)
    remaining_blocks = random.sample(blocks, sample_size)

    try:
        decoded = luby.decode(remaining_blocks)
    except luby.NotEnoughChunks:
        print("not enough luby chunks!")
    else:
        require_true(data == decoded)
        print("Successfully reassembled data!")
