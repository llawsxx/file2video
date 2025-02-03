from encode import create_video
from decode_video import decode
import argparse
import sys

from common import *

def enc_file(source_file, output_video, chunk_size):
    print (f"Encoding {source_file} to {output_video}")
    create_video(source_file, output_video, chunk_size)

def dec_video(source_video, destination_folder):
    print (f"Decoding {source_video} to {destination_folder}")
    decode(source_video, destination_folder)

def main():

    # First, check if '--docker' is in the command line arguments
    docker_mode = '--docker' in sys.argv
    if docker_mode:
        sys.argv.remove('--docker')  # Remove it so it doesn't interfere with the main parser

    docker_usage = """\
docker run --rm -v $(pwd):/data karaketir16/file2video [-h]  [--encode source_file output_video] 
                                                        [--decode source_video destination_folder]"""
    
    if docker_mode:
        parser = argparse.ArgumentParser(description="Program to encode files into videos and decode videos back to files.", usage=docker_usage)
    else:
        parser = argparse.ArgumentParser(description="Program to encode files into videos and decode videos back to files.")

    # Optional argument for encoding
    parser.add_argument("--encode", nargs=2, metavar=('source_file', 'output_video'), 
                        help="Encode a file into a video: source_file output_video.mp4")
    
    # Optional argument for decoding
    parser.add_argument("--decode", nargs=2, metavar=('source_video', 'destination_folder'), 
                        help="Decode a video to a file: source_video.mp4 destination_folder")

    args = parser.parse_args()

    # Check which command is used and call the corresponding function
    if args.encode:
        enc_file(*args.encode,chunk_size = global_chunkSize)
    elif args.decode:
        dec_video(*args.decode)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()