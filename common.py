# defaults
global_reedN = 255
global_reedEC = 10
GreedK = global_reedN - global_reedEC
global_gridSize = (135,240)
frame_rate = 25.0
pixel_size = 8
grid_size = global_gridSize
reedK = global_reedN - global_reedEC
grid_byte = grid_size[0] * grid_size[1] // 8 - (8 + global_reedEC)
global_chunkSize = reedK * (grid_byte // global_reedN)
if grid_byte % global_reedN > 0:
    extra_len = grid_byte % global_reedN - global_reedEC
    if extra_len > 0 and extra_len <= reedK:
        global_chunkSize += extra_len