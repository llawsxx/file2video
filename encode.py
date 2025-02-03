import os
import sys
import math
import json
import av
from tqdm import tqdm
from reedsolo import RSCodec
from v3 import encode_to_image

from checksum import checksum

from common import *

rs = RSCodec(nsym = global_reedEC, nsize = global_reedN)

def process_chunk(data,index):
    """Encode data chunk into BitCode and return as image."""
    data_encoded = rs.encode(data)
    length_byte = len(data_encoded).to_bytes(4,'little')
    index_byte = index.to_bytes(4,'little')
    num_encoded = rs.encode(index_byte + length_byte)
    data = num_encoded + data_encoded

    return encode_to_image(data, grid_size, pixel_size)

def encode_and_write_frames(frames, stream, container):
    """Encode frames and write to video container."""
    for frame in frames:
        video_frame = av.VideoFrame.from_ndarray(frame, format='rgb24')
        for packet in stream.encode(video_frame):
            container.mux(packet)

def create_video(src, dest, chunk_size):
    """Create video from source file using PyAV."""

    md5_checksum = checksum(src)
    file_stats = os.stat(src)
    file_size = file_stats.st_size
    chunk_count = math.ceil(file_size / chunk_size)
    print("chunk count:", chunk_count)

    pbar = tqdm(total=chunk_count, desc="Generating Frames")

    meta_data = {
        "Filename": os.path.basename(src),
        "ChunkCount": chunk_count,
        "Filehash": md5_checksum,
        "ConverterUrl": "https://github.com/llawsxx/file2video",
        "ConverterVersion": "python_v3",
        "FileSize": file_size
    }

    first_frame_data = json.dumps(meta_data, indent=4)
    first_frame = process_chunk(first_frame_data.encode('utf-8'),0)

    # Open output file
    container = av.open(dest, mode='w')
    stream = container.add_stream('h264', rate=frame_rate)
    stream.width = grid_size[1] * pixel_size
    stream.height = grid_size[0] * pixel_size
    stream.pix_fmt = 'yuv420p'
    stream.options = {'crf': '10'}

    # Write the first frame
    video_frame = av.VideoFrame.from_ndarray(first_frame, format='rgb24')
    for packet in stream.encode(video_frame):
        container.mux(packet)

    # Process chunks
    with open(src, 'rb') as f:
        i = 1
        while True:
            chunk = f.read(chunk_size)
            if len(chunk) == 0:
                break
            frame = process_chunk(chunk,i)
            encode_and_write_frames([frame], stream, container)
            pbar.update(1)
            i+=1

    pbar.close()

    # Finalize the video file
    for packet in stream.encode():
        container.mux(packet)
    container.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python file2video.py source_file output_file.mp4")
        sys.exit(1)
    src = sys.argv[1]
    dest = sys.argv[2]
    create_video(src, dest)
