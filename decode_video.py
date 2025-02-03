import cv2
import json
import os
import sys
import logging
from tqdm import tqdm
from checksum import checksum
from reedsolo import RSCodec

from common import *

from v3 import decode_from_image

reedEC = global_reedEC
rs = RSCodec(nsym = reedEC, nsize = global_reedN)
grid_size = global_gridSize

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_frame(frame):
    data = decode_from_image(frame, grid_size)

    num_encoded = data[ : (8 + reedEC)]
    num_decoded, _, _ = rs.decode(num_encoded)
    index = int.from_bytes(num_decoded[0:4], 'little')
    length = int.from_bytes(num_decoded[4:8], 'little')

    data_encoded = data[ (8 + reedEC) :  (8 + reedEC) + length]

    data, _, errata_pos = rs.decode(data_encoded)

    if len(errata_pos) > 0:
        logging.info("Fixed Number of Errors in this frame: ", len(errata_pos))

    return data, index

def decode_video(cap, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    pbar = tqdm(total= (total_frames - 1), desc="Processing Frames")

    ret, first_frame = cap.read()
    if not ret:
        logging.error("Cannot read first frame")
        return

    metadata, _ = process_frame(first_frame)
    if metadata is None:
        logging.error("No QR code in first frame; cannot proceed")
        return
    meta_data = json.loads(metadata.decode('utf8'))
    dest = os.path.join(dest_folder, meta_data["Filename"])

    i = 1
    with open(dest,"wb") as f:
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                data, index = process_frame(frame)
                if index < i:
                    logging.info(f"Drop duplicate frame {index}")
                    continue
                if index != i:
                    logging.info(f"The index {index} needs to be equal to {i}")
                f.write(data)
                i+=1
                pbar.update(1)
            else:
                break

    cap.release()
    pbar.close()

    logging.info("Verifying file integrity for %s", dest)
    md5_sum = checksum(dest)
    if md5_sum != meta_data["Filehash"]:
        logging.error("Data corrupted for file %s", dest)
        raise ValueError("Data corrupted")
    logging.info("File integrity verified: %s", dest)

def decode(src, dest_folder):
    cap = cv2.VideoCapture(src)
    decode_video(cap, dest_folder)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        logging.error("Usage: python script.py source_file.mp4 destination_folder")
        sys.exit(1)
    src = sys.argv[1]
    dest_folder = sys.argv[2]
    decode(src, dest_folder)
