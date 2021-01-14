"""
@company: FSVIC
@author: kindred
@date: 2021-01-10
@version: 1.0
@desc:
    1 正向CRC8校验（直接算法）
    2 CRC8查表法校验
    3 生成CRC8校验表（.CSV）
    4 通过两组数据及对应CRC值，反查CRC模型参数
"""
import re
import os
import pandas as pd
import multiprocessing


def get_input_data():
    """返回输入的16进制数据列表"""
    data_1 = input('数据1(用空格隔开)：')
    data_2 = input('数据2(用空格隔开)：')
    byt_1 = [int(i, 16) for i in data_1.split()]
    byt_2 = [int(i, 16) for i in data_2.split()]
    return byt_1, byt_2


def get_log_data():
    """导入log，提取指定ID的2个信号数据"""
    data_list = []
    byt1 = []
    byt2 = []

    _id = input('输入CAN ID(16进制):')
    log = input('log文件路径：')         # log_file = r'C:\Users\kindred\Desktop\logger.asc'

    f = open(log, encoding='gbk')
    lines = f.readlines()
    for line in lines[:10000]:
        line_list = line.split()
        try:
            if int(_id, 16) == int(line_list[2], 16):
                _match = re.match(r'.*?Rx.*?\d (.*?)$', line)
                data_list.append(_match.group(1))
        except ValueError:
            pass
    if len(data_list) >= 2:
        byt1 = [int(i, 16) for i in data_list[0].split(' ')]
        byt2 = [int(i, 16) for i in data_list[1].split(' ')]
    else:
        print("所选Message在总线前10000条通讯不足2个")
    f.close()
    return byt1, byt2


def data_reverse(data):
    """用于处理数据的输入输出反转"""
    reverse_data = '{:08b}'.format(data)[::-1]
    new_data = int(reverse_data, 2)
    return new_data


def get_crc_value(init, poly, data, refin1, refout1, xorout1):
    """计算CRC校验值"""
    crc = init
    if refin1:
        data = [data_reverse(m) for m in data]
    for i in range(len(data)):                         # 遍历原数据
        crc ^= data[i]
        for j in range(8):                             # 按位异或（8位）
            if crc & 0x80:                             # 判断最高位是否为1
                crc = (crc << 1) ^ poly                # 移位后与多项式异或
            else:
                crc = crc << 1
            crc = crc & 0xff
    if refout1:
        crc = data_reverse(crc)
    crc = crc ^ xorout1
    return crc


def create_crc_table(_ploy):
    """根据多项式，生成CRC表"""
    crc_table = []
    for i in range(256):
        crc = i
        for j in range(8):
            if crc & 0x80:                              # 判断最高位是否为1
                crc = (crc << 1) ^ _ploy
            else:
                crc = crc << 1
        crc = crc & 0xff
        crc_table.append(crc)
    return crc_table


def get_crctable_csv(crc_table):
    """将生成的CRC表存为CSV文件"""
    total_list = []
    headers = []
    table = []
    for crc in crc_table:
        _crc = '0x' + format(crc & 0xff, '02x')                # 格式化输出
        total_list.append(_crc)                                # 加进列表
    for n in range(0, len(total_list), 16):                    # 分割列表，每个列表长度为16
        table.append(total_list[n:n + 16])
    for h in range(16):                                        # 生成表头，为转成CSV文件准备
        headers.append(h)
    writer = pd.DataFrame(columns=headers, data=table)
    if not os.path.exists('file'):
        os.mkdir('file')
    writer.to_csv('file/CRC_Table.csv', index=False, header=False)  # 生成CSV文件，隐藏表头和序列


def table_method(crctable, data, init, refin1, refout1, xorout1):
    """查表法计算CRC值"""
    crc = init
    if refin1:
        data = [data_reverse(m) for m in data]
    for i in range(len(data)):
        crc = crctable[crc ^ data[i]]
    if refout1:
        crc = data_reverse(crc)
    crc = crc ^ xorout1
    print("CRC值(查表法)：", hex(crc))


def reverse_crc_1(data1, data2, crc1, crc2):
    """通过两组数组及对应CRC反推CRC多项式、初始值，
        输入、输出反转
    """
    for _poly in range(256):                                            # 多项式范围
        for i in range(256):                                        # 初始值范围
            for xorout in range(256):
                if get_crc_value(i, _poly, data1, True, True, xorout) == crc1:              # 校验数据
                    if get_crc_value(i, _poly, data2, True, True, xorout) == crc2:
                        _f = open('file/reverse_crc_1.txt', 'a', encoding='utf-8')
                        _f.write("多项式：0x{:02x}\n".format(_poly))
                        _f.write("初始值：0x{:02x}\n".format(i))
                        _f.write("输入反转：True\n")
                        _f.write("输出反转：True\n")
                        _f.write("结果异或值：0x{:02x}\n".format(xorout))
                        _f.write("------------\n")
                        _f.close()


def reverse_crc_2(data1, data2, crc1, crc2):
    """通过两组数组及对应CRC反推CRC多项式、初始值，
        输入反转，输出不反转
    """
    for _poly in range(256):                                            # 多项式范围
        for i in range(256):                                        # 初始值范围
            for xorout in range(256):
                if get_crc_value(i, _poly, data1, True, False, xorout) == crc1:              # 校验数据
                    if get_crc_value(i, _poly, data2, True, False, xorout) == crc2:
                        _f = open('file/reverse_crc_2.txt', 'a', encoding='utf-8')
                        _f.write("多项式：0x{:02x}\n".format(_poly))
                        _f.write("初始值：0x{:02x}\n".format(i))
                        _f.write("输入反转：True\n")
                        _f.write("输出反转：False\n")
                        _f.write("结果异或值：0x{:02x}\n".format(xorout))
                        _f.write("-*-*-*-*-*-*-\n")
                        _f.close()


def reverse_crc_3(data1, data2, crc1, crc2):
    """通过两组数组及对应CRC反推CRC多项式、初始值，
        输入不反转，输出反转
    """
    for _poly in range(256):                                            # 多项式范围
        for i in range(256):                                        # 初始值范围
            for xorout in range(256):
                if get_crc_value(i, _poly, data1, False, True, xorout) == crc1:              # 校验数据
                    if get_crc_value(i, _poly, data2, False, True, xorout) == crc2:
                        _f = open('file/reverse_crc_3.txt', 'a', encoding='utf-8')
                        _f.write("多项式：0x{:02x}\n".format(_poly))
                        _f.write("初始值：0x{:02x}\n".format(i))
                        _f.write("输入反转：False\n")
                        _f.write("输出反转：True\n")
                        _f.write("结果异或值：0x{:02x}\n".format(xorout))
                        _f.write("*-*-*-*-*-*-*\n")
                        _f.close()


def reverse_crc_4(data1, data2, crc1, crc2):
    """通过两组数组及对应CRC反推CRC多项式、初始值，
        输入、输出不反转
    """
    for _poly in range(256):                                            # 多项式范围
        for i in range(256):                                        # 初始值范围
            for xorout in range(256):
                if get_crc_value(i, _poly, data1, False, False, xorout) == crc1:              # 校验数据
                    if get_crc_value(i, _poly, data2, False, False, xorout) == crc2:
                        _f = open('file/reverse_crc_4.txt', 'a', encoding='utf-8')
                        _f.write("多项式：0x{:02x}\n".format(_poly))
                        _f.write("初始值：0x{:02x}\n".format(i))
                        _f.write("输入反转：False\n")
                        _f.write("输出反转：False\n")
                        _f.write("结果异或值：0x{:02x}\n".format(xorout))
                        _f.write("*************\n")
                        _f.close()


def handle_data():
    """用于CRC模型参数输入"""
    refin2 = False
    refout2 = False
    init2 = int(input("c.输入初始值(16进制)："), 16)
    mark_in = input("输入反转：1.反转；2.不反转：")
    mark_out = input("输出反转：1.反转；2.不反转：")
    xorout2 = int(input("输入结果异或值(16进制)："), 16)

    check_data = input('a.输入需校验的数据位(用空格隔开)：')
    d = [int(i, 16) for i in check_data.split()]

    if mark_in == '1':
        refin2 = True
    elif mark_in == '2':
        refin2 = False
    else:
        print("请输入1或2")
    if mark_out == '1':
        refout2 = True
    elif mark_out == '2':
        refout2 = False
    else:
        print("请输入1或2")
    return init2, d, refin2, refout2, xorout2


if __name__ == '__main__':
    multiprocessing.freeze_support()
    d1 = []
    d2 = []

    method = int(input('功能选择(1.校验; 2.查表; 3.生成校验表; 4.反查): '))
    if method == 1 or method == 2 or method == 3:
        print('<-----获取数据----->')
        ploy = int(input("b.输入多项式(16进制)："), 16)
        if method == 3:
            get_crctable_csv(create_crc_table(ploy))
        else:
            _init, d1, refin, refout, _xorout = handle_data()
            if method == 1:
                result = get_crc_value(_init, ploy, d1, refin, refout, _xorout)
                print('CRC值（正向校验）：', hex(result))
            if method == 2:
                table_method(create_crc_table(ploy), d1, _init, refin, refout, _xorout)

    elif method == 4:
        sel = int(input('数据录入方式选择(1.输入16进制数据(含校验位，如\'37 40 04 00 00 00 1c e6\'); 2.导入log):'))
        if sel == 1:
            d1, d2 = get_input_data()
        elif sel == 2:
            d1, d2 = get_log_data()
        else:
            print("输入错误")
        if not os.path.exists('file'):
            os.mkdir('file')

        args_t = (d1[:-1], d2[:-1], d1[-1], d2[-1],)

        # 多进程
        p1 = multiprocessing.Process(target=reverse_crc_1, args=args_t)
        p2 = multiprocessing.Process(target=reverse_crc_2, args=args_t)
        p3 = multiprocessing.Process(target=reverse_crc_3, args=args_t)
        p4 = multiprocessing.Process(target=reverse_crc_4, args=args_t)

        p1.start()
        p2.start()
        p3.start()
        p4.start()

        p1.join()
        p2.join()
        p3.join()
        p4.join()
        print("匹配完成，已存入.txt文件")
    else:
        print("输入错误")

    os.system('pause')        # 让程序暂停
