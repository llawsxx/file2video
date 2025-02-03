import numpy as np
from PIL import Image

def getBit(data, bit_index):
    """Retrieve the bit at the specified index from the data."""
    byte_index = bit_index // 8
    bit_position = bit_index % 8
    return (data[byte_index] >> bit_position) & 1

def setBit(data, bit_index):
    """Set the bit at the specified index in the data."""
    byte_index = bit_index // 8
    bit_position = bit_index % 8
    data[byte_index] |= (1 << bit_position)

def create_custom_code(data, grid_size):
    """Create a custom encoded image from data."""
    bits2byte = np.unpackbits(data,axis=-1,bitorder="little") * 255
    pad_width = grid_size[0] * grid_size[1] - len(bits2byte)
    if pad_width > 0:
        bitmap = np.pad(bits2byte,((0, pad_width),),'constant')
    else:
        bitmap = bits2byte
    return bitmap.reshape(grid_size)

def encode_to_image(data, grid_size, pixel_size = 2):
    """Encode data into a binary grid and save as an image."""
    grid = create_custom_code(data, grid_size)
    img = Image.fromarray(np.stack([grid]*3, axis=-1), 'RGB')
    return np.array(img.resize((grid_size[1] * pixel_size, grid_size[0] * pixel_size), Image.Resampling.NEAREST))

def decode_from_image(img, grid_size):
    """Decode binary data from an image file."""
    img = Image.fromarray(img)
    img = img.convert('L')
    img = img.resize((grid_size[1], grid_size[0]), Image.Resampling.BOX)
    grid = np.array(img)
    grid = grid > 128
    data = np.packbits(grid.reshape(grid_size[0] * grid_size[1]), axis=-1, bitorder='little')
    return data

def example():
    # Example usage:
    test_string = "Hello, World!"
    data = test_string.encode()

    # Encode to image
    img = encode_to_image(data, grid_size=(480,270))  # Use a smaller grid for visualization

    # Decode from image
    decoded_data = decode_from_image(img, grid_size=(480,270))
    decoded_string = decoded_data.decode("utf-8", errors="ignore")

    # # Display results
    # img.show()
    print("Decoded String:", decoded_string)

if __name__ == "__main__":
    example()
