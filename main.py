from PIL import Image, ImageDraw, ImageFont
import numpy as np


def make_map(str_list):
    l = []
    for i in str_list:
        im = Image.new("L", (20, 20), "white")
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), i)
        l.append(np.asarray(im).mean())
    l_as = np.argsort(l)
    lenl = len(l)
    l2256 = np.r_[np.repeat(l_as[:-(256 % lenl)], 256//lenl),
                  np.repeat(l_as[-(256 % lenl):], 256//lenl+1)]
    chr_map = np.array(str_list)[l2256]
    return chr_map


def quantize(pixel):
    arr = [196, 128, 64, 0]
    # 各色チャンネルを4階調に減色する
    quantized = [0, 0, 0]
    for i in range(3):
        for j in range(4):
            if pixel[i] >= arr[j]:
                quantized[i] = max(4-j-1, 0)
                break
    return quantized[0] * 16 + quantized[1] * 4 + quantized[2] + 1


def make_AA(file_path, str_list="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz +-*/%'"+'"!?#&()~^|@;:.,[]{}<>_0123456789', width=60):
    img = Image.open(file_path)
    str_list = list(str_list)
    gray_img_array = np.asarray(img.convert('L').resize(
        (width, width*img.height//img.width//2)))
    color_img_array = np.asarray(img.resize(
        (width, width*img.height//img.width//2)))
    chr_map = make_map(str_list)
    aa = chr_map[gray_img_array].tolist()
    colors = [[quantize(pixel) for pixel in row] for row in color_img_array]

    for i in range(len(gray_img_array)):
        print(''.join(aa[i]))

    with open("result/aa.ytt", "w") as f:
        f.write(
            '<?xml version="1.0" encoding="utf-8" ?>\n' +
            '<timedtext format="3">\n' +
            '<head>\n')
        heads = ""
        for i in range(64):
            r = (i // 16) * 64
            g = ((i // 4) % 4) * 85
            b = (i % 4) * 64
            heads += f'<pen id="{i+1}" fc="#{r:02x}{g:02x}{b:02x}" fs="3" sz="0" fo="255" bo="0" b="1" />\n'
        for i in range(25):
            heads += f'<wp id="{i+1}" ap="0" ah="0" av="{i*4}" />\n'
        f.write(heads)
        f.write('</head>\n<body>\n')
        body = ""
        for i in range(len(gray_img_array)):
            body += f'<p t="0" d="10000" wp="{i%25}">\n'
            for j in range(len(gray_img_array[i])):
                body += f'<s p="{colors[i][j]}">{aa[i][j]}</s>'
            body += '</p>\n'
        f.write(body)
        f.write('</body>\n</timedtext>')


make_AA("imgs/input.png")
