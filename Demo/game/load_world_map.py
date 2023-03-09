import struct

##两个字节：’BM’表示Windows位图，’BA’表示OS/2位图；
##一个4字节整数：表示位图大小；
##一个4字节整数：保留位，始终为0；
##一个4字节整数：实际图像的偏移量；
##一个4字节整数：Header的字节数；
##一个4字节整数：图像宽度；
##一个4字节整数：图像高度；
##一个2字节整数：始终为1；
##一个2字节整数：颜色数。

# a
# b

class Bmp:
    def __init__(self):
        pass

    def load(self, path):
        with open(path, 'rb') as f:
            head = f.read(54)
            print(head)

            data = struct.unpack('<ccIIIIIIHH' + 'IIIIII', head)
            print(data)
            
            self.file_size = data[2]
            self.pixel_data_offset = data[4]
            self.head_size = data[5]
            self.width = data[6]
            self.height = data[7]
            self.pixel_bits = data[9]

            self.line_bytes = (self.width*self.pixel_bits + 31) // 8
            self.line_bytes = self.line_bytes // 4 * 4
            # 扫描行从左到右,从下到上

            # Windows规定一个扫描行所占的字节数必须是4的倍数(即以long为单位),不足的以0填充，
            # DataSizePerLine= (biWidth* biBitCount+31)/8;
            f.seek(self.pixel_data_offset)

            self.lines = []
            for i in range(self.height):
                data = f.read(self.line_bytes)
                line_pixels = [data[i*3:i*3+3] for i in range(self.width)]
                self.lines.append(line_pixels)
            


if __name__ == '__main__':
    bmp = Bmp()
    bmp.load('../world_map.bmp')
    print(bmp.width, bmp.pixel_bits, bmp.line_bytes)
    print(bmp.lines)
    
