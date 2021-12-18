from PIL import Image

def combine(codeImg, contentImg, colorized, moduleSize, contrast=1.15, brightness=1.3):    
    qr = codeImg
    qr = qr.convert('RGBA') if colorized else qr
    
    bg0 = contentImg.convert('RGBA')

    ms = moduleSize
    ms8 = moduleSize * 8
    ms16 = moduleSize * 16 
        
    bg = bg0 if colorized else bg0.convert('1')

    c1 = moduleSize/4
    c2 = moduleSize-c1

    #c1 -= 1
    c2 -= 1

    ratio = 0.2

    target = Image.new('RGBA', size=qr.size, color=(0, 0, 0, 0));

    for i in range(qr.size[0]):
        for j in range(qr.size[1]):
            x=i%moduleSize
            y=j%moduleSize

            if not ((x >= c1 and x <= c2 and y >= c1 and y <= c2) or (bg0.getpixel((i,j))[3]==0)):
                qr.putpixel((i,j), bg.getpixel((i,j)))
            else:
                target.putpixel((i,j), qr.getpixel((i,j)))


    #target.show()

    #qr_name = os.path.join(save_dir, os.path.splitext(os.path.basename(bg_name))[0] + '_qrcode.png') if not save_name else os.path.join(save_dir, save_name)
    
    #return qr.resize((qr.size[0]*3, qr.size[1]*3))

    result = bg.copy()

    result.paste(target, (0, 0), target)

    #result = Image.blend(result, bg, alpha=ratio)

    return result