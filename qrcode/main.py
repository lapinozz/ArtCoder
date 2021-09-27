from PIL import ImageOps

from pyzbar.pyzbar import decode
 
from .pyqart.qr import QrData
from .pyqart.art import QArtist
from .pyqart.qr.printer import QrImagePrinter, QrStringPrinter

import os
from timeit import default_timer as timer

def decodeQr(codeImg, outputDir):
    startTime = timer()

    codeImg = ImageOps.expand(codeImg, border=50, fill='white')

    codes = decode(codeImg)
    if len(codes) <= 0:
        print("No code found in: ", CODE_PATH)
        quit()

    data = codes[0].data.decode('utf-8')

    open(os.path.join(outputDir, "data.txt"), "w").write(data)

    print("decoded: {}s".format(timer() - startTime))

    return data

def encodeQr(segments, level, version, contentModules, contentWeights, moduleSize, outputDir):
    startTime = timer()

    dither = False
    only_data = False
    rand = False
    yx = [None, None]
    #version = 20  # 1 to 40
    mask = None # 0 to 7
    rotation = 0
    point_size = moduleSize
    board = 0
    color = None
    background = None
    content = None # contentImg

    start = timer()

    data = QrData("", level)

    for segment in segments:
        if segment['mode'] == 'NUMERIC':
            data.put_numbers(segment['text'])
        elif segment['mode'] == 'ALPHANUMERIC':
            data.put_alpha_numeric(segment['text'])
        else:
            data.put_string(segment['text'])

    artist = QArtist(data, contentModules, contentWeights, version, mask, level,
                     rotation, dither, only_data, rand,
                     yx[0], yx[1])

    result = QrImagePrinter.print(artist, None, point_size, board, color, background)

    result.save(os.path.join(outputDir, "base_code.png"))

    print("encoded: {}s".format(timer() - startTime))

    return result