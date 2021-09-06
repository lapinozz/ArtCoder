from vgg import Vgg16
import utils
from torchvision import transforms
import torch.nn as nn
import torch.optim as optim
import numpy as np
import torch
from SS_layer import SSlayer
from PIL import Image

from timeit import default_timer as timer

epoch = 0

def test():
    target = utils.load_image(filename="./test/target.png")
   # center = utils.load_image(filename="./test/center.png")
    #error = utils.load_image(filename="./test/error.png") * 255
    ideal = utils.load_image(filename="./test/ideal.png")

    #print(target)


    targetTensor = transforms.ToTensor()(target).cuda()[0]
    ideal = transforms.ToTensor()(ideal).cuda()
    inv = (1 - ideal).cuda()

    time = timer()

    centers = targetTensor.unfold(0, 16, 16).unfold(1, 16, 16)

    i = centers[..., 5:12, 5:12].mean([-1, -2])

    ons = ideal * i + inv;
    offs = inv  * i;

    dis_b = 70 / 255;
    dis_w = 180 / 255;

    ons = torch.where(ons > dis_w, 0.0, 1.0)
    offs = torch.where(offs < dis_b, 0.0, 1.0)

    errors = offs + ons

    print("time: {}".format(timer() - time))

    Image.fromarray(np.uint8(transforms.ToPILImage()(errors))).save("./test/error_out.png")

    quit()

