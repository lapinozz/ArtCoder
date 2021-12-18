import os
import math

import torch
import shutil
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
from torchvision import transforms

from timeit import default_timer as timer

unloader = transforms.ToPILImage()
load = transforms.ToTensor()

def load_image(filename, size=None, scale=None):
    img = Image.open(filename)
    if size is not None:
        img = img.resize((size, size), Image.ANTIALIAS)
    elif scale is not None:
        img = img.resize((int(img.size[0] / scale), int(img.size[1] / scale)), Image.ANTIALIAS)
    return img

alignement_coords = [
    [],
    [6, 18],
    [6, 22],
    [6, 26],
    [6, 30],
    [6, 34],
    [6, 22, 38],
    [6, 24, 42],
    [6, 26, 46],
    [6, 28, 50],
    [6, 30, 54],
    [6, 32, 58],
    [6, 34, 62],
    [6, 26, 46, 66],
    [6, 26, 48, 70],
    [6, 26, 50, 74],
    [6, 30, 54, 78],
    [6, 30, 56, 82],
    [6, 30, 58, 86],
    [6, 34, 62, 90],
    [6, 28, 50, 72, 94],
    [6, 26, 50, 74, 98],
    [6, 30, 54, 78, 102],
    [6, 28, 54, 80, 106],
    [6, 32, 58, 84, 110],
    [6, 30, 58, 86, 114],
    [6, 34, 62, 90, 118],
    [6, 26, 50, 74, 98, 122],
    [6, 30, 54, 78, 102, 126],
    [6, 26, 52, 78, 104, 130],
    [6, 30, 56, 82, 108, 134],
    [6, 34, 60, 86, 112, 138],
    [6, 30, 58, 86, 114, 142],
    [6, 34, 62, 90, 118, 146],
    [6, 30, 54, 78, 102, 126, 150],
    [6, 24, 50, 76, 102, 128, 154],
    [6, 28, 54, 80, 106, 132, 158],
    [6, 32, 58, 84, 110, 136, 162],
    [6, 26, 54, 82, 110, 138, 166],
    [6, 30, 58, 86, 114, 142, 170]
]

def add_pattern(target_PIL, code_PIL, version, module_number, module_size):
    target_img = np.asarray(target_PIL)
    code_img = np.array(code_PIL)
    output = target_img
    output = np.require(output, dtype='uint8', requirements=['O', 'W'])
    ms = module_size  # module size
    mn = module_number  # module_number
    output[0 * ms:(8 * ms), 0 * ms:(8 * ms), :] = code_img[0 * ms:(8 * ms), 0 * ms:(8 * ms), :]
    output[((mn - 8) * ms):(mn * ms), 0 * ms:(8 * ms), :] = code_img[((mn - 8) * ms):(mn * ms),
                                                                    0 * ms:(8 * ms),
                                                                    :]
    output[0 * ms: (8 * ms), ((mn - 8) * ms):(mn * ms), :] = code_img[0 * ms: (8 * ms),
                                                                     ((mn - 8) * ms):(mn * ms), :]

    coords = alignement_coords[version - 1]
    for cX in coords:
        for cY in coords:
            x = cX - 2
            y = cY - 2

            if x <= 7 and y <= 7: continue
            if x <= 7 and y + 5 >= module_number - 7: continue
            if x + 5 >= module_number - 7 and y <= 7: continue

            output[x*ms:x*ms + 5*ms, y*ms:y*ms + 5*ms, :] = code_img[x*ms:x*ms + 5*ms, y*ms:y*ms + 5*ms,:]
            #output[28 * ms:(33 * ms) - 1, 28 * ms:(33 * ms) - 1, :] = code_img[28 * ms:(33 * ms) - 1, 28 * ms:(33 * ms) - 1,:]

    output = Image.fromarray(output.astype('uint8'))
    print('Added finder and alignment patterns.')
    return output


def del_file(filepath):
    del_list = os.listdir(filepath)
    for f in del_list:
        file_path = os.path.join(filepath, f)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def gram_matrix(y):
    (b, ch, h, w) = y.size()
    features = y.view(b, ch, w * h)
    features_t = features.transpose(1, 2)
    gram = features.bmm(features_t) / (ch * h * w)
    return gram

def get_action_matrix(img_target, ideal, ideal_inv, module_size, Dis_b=50, Dis_w=200):
    img_target = transforms.Grayscale()(img_target)

    #print(img_target.shape)
   # transforms.ToPILImage()(img_target.squeeze(0).squeeze(0)).save("output./img_target.png")

    dis_b = Dis_b / 255;
    dis_w = Dis_w / 255;

    centers = img_target.squeeze(0).squeeze(0).unfold(0, module_size, module_size).unfold(1, module_size, module_size)

    c1 = int(module_size / 4)
    c2 = int(module_size - c1)

    #c1 = 0
    #c2 = int(module_size)

    i = centers[..., c1:c2, c1:c2].mean([-1, -2])
    ons = torch.lt(i, dis_w) * ideal
    offs = torch.gt(i, dis_b) * ideal_inv

    errors = offs + ons

    #transforms.ToPILImage()(errors.cpu()).save("output./errors.png")

    return errors

def get_ideal_result(img_code, module_size, module_number):
    img_code = np.require(np.asarray(img_code.convert('L')), dtype='uint8', requirements=['O', 'W'])
    return get_binary_result(img_code, module_size, module_number)


def get_binary_result(img_code, module_size, module_number):
    binary_result = np.zeros((module_number, module_number))
    for j in range(module_number):
        for i in range(module_number):
            module = img_code[i * module_size:(i + 1) * module_size, j * module_size:(j + 1) * module_size]
            module_color = np.around(np.mean(module), decimals=2)
            if module_color < 128:
                binary_result[i, j] = 0
            else:
                binary_result[i, j] = 1
    return binary_result


def get_target(binary_result, b_robust, w_robust, module_num, module_size):
    img_size = module_size * module_num
    target = np.require(np.ones((img_size, img_size)), dtype='uint8', requirements=['O', 'W'])

    for i in range(module_num):
        for j in range(module_num):
            one_binary_result = binary_result[i, j]
            if one_binary_result == 0:
                target[i * module_size:(i + 1) * module_size, j * module_size:(j + 1) * module_size] = b_robust
            else:
                target[i * module_size:(i + 1) * module_size, j * module_size:(j + 1) * module_size] = w_robust

    target = load(Image.fromarray(target.astype('uint8')).convert('RGB')).unsqueeze(0).cuda()
    return target


def get_epoch_image(tensor, path, code_pil, version, module_num, module_size, addpattern=True):
    image = tensor.clone()
    image = image.squeeze(0)
    image = unloader(image)
    if addpattern == True:
        image = add_pattern(image, code_pil, version, module_num, module_size)
    image = ImageOps.expand(image, border=module_size*4, fill='white')
    return image


def save_image_epoch(tensor, path, name, code_pil, version, module_num, module_size, addpattern=True):
    image = get_epoch_image(tensor, path, code_pil, version, module_num, module_size, addpattern)
    image.save(os.path.join(path, "epoch_" + str(name)))


def tensor_to_PIL(tensor):
    image = tensor.clone()
    image = image.squeeze(0)
    image = unloader(image)
    return image


def get_3DGauss(s=0, e=15, sigma=1.5, mu=7.5, moduleSize=16):
    #e = moduleSize - 1
    x, y = np.mgrid[s:e:moduleSize * 1j, s:e:moduleSize * 1j]
    z = (1 / (2 * math.pi * sigma ** 2)) * np.exp(-((x - mu) ** 2 + (y - mu) ** 2) / (2 * sigma ** 2))
    z = torch.from_numpy(MaxMinNormalization(z.astype(np.float32)))
    for j in range(moduleSize):
        for i in range(moduleSize):
            if z[i, j] < 0.1:
                z[i, j] = 0
    return z


def MaxMinNormalization(loss_img):
    maxvalue = np.max(loss_img)
    minvalue = np.min(loss_img)
    img = (loss_img - minvalue) / (maxvalue - minvalue)
    img = np.around(img, decimals=2)
    return img


def print_options(opt):
    """Print and save options
    It will print both current options and default values(if different).
    It will save options into a text file / [checkpoints_dir] / opt.txt
    """
    message = ''
    message += '----------------- Options ---------------\n'
    for k, v in sorted(vars(opt).items()):
        comment = ''
        message += '{:>25}: {:<30}{}\n'.format(str(k), str(v), comment)
    message += '----------------- End -------------------'
    print(message)
