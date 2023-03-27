import os
import json
import struct

# 两个字节：’BM’表示Windows位图，’BA’表示OS/2位图；
# 一个4字节整数：表示位图大小；
# 一个4字节整数：保留位，始终为0；
# 一个4字节整数：实际图像的偏移量；
# 一个4字节整数：Header的字节数；
# 一个4字节整数：图像宽度；
# 一个4字节整数：图像高度；
# 一个2字节整数：始终为1；
# 一个2字节整数：颜色数。

class Bmp:
    def __init__(self, path):
        self.load(path)

    def get_pixel(self, x, y):
        return self.lines[y][x]
    
    def set_pixel(self, x, y, value):
        self.lines[y][x] = value

    def get_color(self, x, y):
        data = self.get_pixel(x, y)
        return struct.unpack(self.pixel_format, data)

    def load(self, path):
        with open(path, 'rb') as f:
            head = f.read(54)
            #print(head)

            data = struct.unpack('<ccIIIIIIHH' + 'IIIIII', head)
            #print(data)
            
            self.file_size = data[2]
            self.pixel_data_offset = data[4]
            self.head_size = data[5]
            self.width = data[6]
            self.height = data[7]
            self.pixel_bits = data[9]

            if self.pixel_bits not in [24, 32]:
                raise Exception(f'pixel bits not support: {self.pixel_bits}')

            self.pixel_format = 'BBB' if self.pixel_bits == 24 else 'BBBB'

            self.line_bytes = (self.width*self.pixel_bits + 31) // 8
            self.line_bytes = self.line_bytes // 4 * 4
            # 扫描行从左到右,从下到上

            # Windows规定一个扫描行所占的字节数必须是4的倍数(即以long为单位),不足的以0填充，
            # DataSizePerLine= (biWidth* biBitCount+31)/8;
            f.seek(self.pixel_data_offset)

            self.lines = []
            n = self.pixel_bits // 8
            for i in range(self.height):
                data = f.read(self.line_bytes)
                line_pixels = [data[i*n:(i+1)*n] for i in range(self.width)]
                self.lines.append(line_pixels)
            self.lines.reverse()

def build_map_data():
    bmp = Bmp('./game/data/world_map.bmp')
    print(bmp.width, bmp.height)

    cx = bmp.width // 2
    cy = bmp.height // 2

    data = []
    for y in range(bmp.height):
        for x in range(bmp.width):
            r,g,b = bmp.get_color(x, y)
            item = (x - cx, -(y - cy), r,g,b)
            data.append(item)

    with open('./game/data/world_map.dat', 'wb') as f:
        for item in data:
            x,y,r,g,b = item
            tile = struct.pack('>BBB', r,g,b)
            f.write(tile)

if __name__ == '__main__':
    #bmp = Bmp('./world_map.bmp')
    #print(bmp.width, bmp.pixel_bits, bmp.line_bytes)
    #print(bmp.lines)
    #print(bmp.get_pixel(29, 4))
    #print(bmp.get_color(3, 29))
    
    #build_map_data()

    bmp = Bmp('./data/world_terrain.bmp')
    print(bmp.pixel_data_offset)
    
