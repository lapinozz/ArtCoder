import re 
import os
import glob

from PIL import Image, ImageFont, ImageDraw 

def saveGif(outputDir, inRegex="epoch_epoch=*.jpg"):
    paths = sorted(glob.glob(os.path.join(outputDir, inRegex)))
    paths.sort(key=lambda p: int(re.search('epoch_epoch=(\\d+)', p).group(1)))

    img, *imgs = [Image.open(f) for f in paths]
    durations = [100] * len(imgs)
    durations.append(5000)

    if False:
        font = ImageFont.load_default()
        for idx, img in enumerate(imgs):
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), str(idx), font=font, fill='black')

    img.save(fp=os.path.join(outputDir, "anim.gif"), format='GIF', append_images=imgs, save_all=True, duration=durations, loop=0)
