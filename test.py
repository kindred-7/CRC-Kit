

def reverse_crc(data1, data2, crc1, crc2, _f):
    """通过两组数组及对应CRC反推CRC多项式、初始值"""
    for _poly in range(256):                                            # 多项式范围
        for i in range(256):                                        # 初始值范围
            for xorout in range(256):
                if get_crc_value(i, _poly, data1, True, True, xorout) == crc1 and \
                        get_crc_value(i, _poly, data2, True, True, xorout) == crc2:
                    _f.write("多项式：0x{:02x}\n".format(_poly))
                    _f.write("初始值：0x{:02x}\n".format(i))
                    _f.write("输入反转：True\n")
                    _f.write("输出反转：True\n")
                    _f.write("结果异或值：0x{:02x}\n".format(xorout))
                    _f.write("------------\n")

                if get_crc_value(i, _poly, data1, True, False, xorout) == crc1 and \
                        get_crc_value(i, _poly, data2, True, False, xorout) == crc2:
                    _f.write("多项式：0x{:02x}\n".format(_poly))
                    _f.write("初始值：0x{:02x}\n".format(i))
                    _f.write("输入反转：True\n")
                    _f.write("输出反转：False\n")
                    _f.write("结果异或值：0x{:02x}\n".format(xorout))
                    _f.write("-*-*-*-*-*-*-\n")

                if get_crc_value(i, _poly, data1, False, True, xorout) == crc1 and \
                        get_crc_value(i, _poly, data2, False, True, xorout) == crc2:
                    _f.write("多项式：0x{:02x}\n".format(_poly))
                    _f.write("初始值：0x{:02x}\n".format(i))
                    _f.write("输入反转：False\n")
                    _f.write("输出反转：True\n")
                    _f.write("结果异或值：0x{:02x}\n".format(xorout))
                    _f.write("*-*-*-*-*-*-*\n")

                if get_crc_value(i, _poly, data1, False, False, xorout) == crc1 and \
                        get_crc_value(i, _poly, data2, False, False, xorout) == crc2:
                    _f.write("多项式：0x{:02x}\n".format(_poly))
                    _f.write("初始值：0x{:02x}\n".format(i))
                    _f.write("输入反转：False\n")
                    _f.write("输出反转：False\n")
                    _f.write("结果异或值：0x{:02x}\n".format(xorout))
                    _f.write("*************\n")