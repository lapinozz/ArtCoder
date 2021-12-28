import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms

import gc

import numpy as np

from PIL import Image

from timeit import default_timer as timer

import utils
from SS_layer import SSlayer
from vgg import Vgg16

from segmentation import segmentData
from prepareContent import prepareContent
from qrcode import decodeQr, encodeQr
from combine import combine
from saveGif import makeGif, saveGif

epoch = 0
output = None

async def artcoder(style_img, content_img, code_img, OUTPUT_DIR, version,
             LEARNING_RATE=0.01, CONTENT_WEIGHT=1e8, STYLE_WEIGHT=1e15, CODE_WEIGHT=1e12, moduleSize=16, moduleNum=37,
             EPOCHS=50000, discrim=75, correct=55, USE_ACTIVATION_MECHANISM=True):

    Dis_b = discrim
    Dis_w = 255 - discrim
    Correct_b = correct
    Correct_w = 255 - correct

    imageSize = moduleSize * moduleNum

    transform = transforms.Compose([
        transforms.Resize(imageSize),
        transforms.ToTensor(),
    ])

    gc.collect()
    torch.cuda.empty_cache()

    vgg = Vgg16(requires_grad=False).cuda()  # vgg16 model
    ss_layer = SSlayer(requires_grad=False, moduleSize=moduleSize).cuda()

    init_img = utils.add_pattern(content_img, code_img, version, module_number=moduleNum, module_size=moduleSize)

    style_img = transform(style_img)
    content_img = transform(content_img)
    init_img = transform(init_img)

    init_img = init_img.repeat(1, 1, 1, 1).cuda()
    style_img = style_img.repeat(1, 1, 1, 1).cuda()  # make fake batch
    content_img = content_img.repeat(1, 1, 1, 1).cuda()

    features_style = vgg(style_img)  # feature maps extracted from VGG
    features_content = vgg(content_img)

    gram_style = [utils.gram_matrix(i) for i in features_style]  # gram matrix of style feature
    mse_loss = nn.MSELoss()

    y = init_img.detach()  # y is the target output. Optimized start from the content image.
    y = y.requires_grad_()  # let y to require grad

    optimizer = optim.AdamW([y], lr=LEARNING_RATE)  # let optimizer to optimize the tensor y

    ideal_result = utils.get_ideal_result(
        img_code=code_img,
        module_size=moduleSize,
        module_number=moduleNum
    )

    ideal_result = torch.tensor(ideal_result.astype('float32'), device=torch.device('cuda:0'))
    ideal_result_inv = (1 - ideal_result)

    error_matrix = utils.get_action_matrix(
        img_target=y,
        ideal=ideal_result,
        ideal_inv=ideal_result_inv,
        Dis_b=Dis_b, Dis_w=Dis_w,
        module_size=moduleSize
    )
    code_target = ss_layer(utils.get_target(ideal_result, b_robust=Correct_b, w_robust=Correct_w,
        module_size=moduleSize,
        module_num=moduleNum))

    trainingTimeStart = timer()
    epochTimeStart = timer()

    outputImages = []

    def debug(string, time):
        return
        if True:
            #torch.cuda.empty_cache()
            torch.cuda.synchronize()
            #gpu_usage()
            #print(torch.cuda.memory_summary(device=None, abbreviated=False))
            print(string.format(timer() - time))

    def closure(code_target=code_target):

        global output

        time = timer()
        optimizer.zero_grad()
        y.data.clamp_(0, 1)
        debug("init: {}", time)

        time = timer()
        features_y = vgg(y)  # feature maps of y extracted from VGG
        debug("feature: {}", time)
        time = timer()
        gram_style_y = [utils.gram_matrix(i) for i in
                        features_y]  # gram matrixs of feature_y in relu1_2,2_2,3_3,4_3
        debug("gram: {}", time)

        fc = features_content.relu3_3  # content target in relu4_3
        fy = features_y.relu3_3  # y in relu4_3

        time = timer()
        style_loss = 0  # add style_losses in relu1_2,2_2,3_3,4_3
        for i in range(len(gram_style)):
            style_loss += mse_loss(gram_style_y[i], gram_style[i])
        style_loss = STYLE_WEIGHT * style_loss
        debug("style_loss: {}", time)

        time = timer()
        code_y = ss_layer(y)
        debug("ss_layer: {}", time)

        if USE_ACTIVATION_MECHANISM == 1:
            time = timer()
            error_matrix = utils.get_action_matrix(
                img_target=y,
                ideal=ideal_result,
                ideal_inv=ideal_result_inv,
                Dis_b=Dis_b, Dis_w=Dis_w,
                module_size=moduleSize)
            debug("action 1: {}", time)
            time = timer()
            activate_num = error_matrix.sum()
            activate_weight = error_matrix * 10
            code_y = code_y * activate_weight
            code_target = code_target * activate_weight
            debug("action 2: {}", time)
        else:
            code_y = code_y.cpu()
            code_target = code_target.cpu()
            activate_num = moduleNum * moduleNum

        time = timer()
        code_loss = CODE_WEIGHT * mse_loss(code_target, code_y)
        content_loss = CONTENT_WEIGHT * mse_loss(fc, fy)  # content loss
        debug("code/content loss: {}", time)

        time = timer()
        total_loss = style_loss + code_loss + content_loss
        #make_dot(total_loss).render("./rnn_torchviz", format="png")
        total_loss.backward(retain_graph=True)
        debug("backward: {}", time)

        isLastEpoch = epoch == EPOCHS - 1
        isImageUpdate = isLastEpoch or epoch % 200 == 0 
        isTimeUpdate  = isLastEpoch or isImageUpdate or epoch % 20 == 0 

        if isTimeUpdate:
            '''
            print(
                "Epoch {}: Style Loss : {:4f}. Content Loss: {:4f}. Code Loss: {:4f}. Activated module number: {:4.2f}. Discriminate_b：{:4.2f}. Discriminate_w：{:4.2f}.".format(
                    epoch, style_loss, content_loss, code_loss, activate_num, Dis_b, Dis_w)
            )
            '''

            nonlocal epochTimeStart
            currentTime = timer()
            totalElapsedTime = currentTime - trainingTimeStart
            averageEpoch = currentTime - epochTimeStart
            epochTimeStart = currentTime

            averageEpochTime = averageEpoch / 20
            globalAverageEpochTime = totalElapsedTime / (epoch + 1)
            timeLeft = (EPOCHS - epoch) * totalElapsedTime / (epoch + 1)

            '''
            print("Total time: {:4.5f}, Average Epoch Time: {:4.5f}: Global Average Epoch Time: {:4.5f} Time Left: {:4.5f}".format(totalElapsedTime, averageEpoch / 20, totalElapsedTime / (epoch + 1), (EPOCHS - epoch) * totalElapsedTime / (epoch + 1)))
            '''

            output = {}
            output['epoch'] = epoch
            output['timeLeft'] = timeLeft
            output['currentTime'] = currentTime
            output['averageEpoch'] = averageEpoch
            output['totalElapsedTime'] = totalElapsedTime
            output['averageEpochTime'] = averageEpochTime
            output['globalAverageEpochTime'] = globalAverageEpochTime

            if isImageUpdate:
                img_name = 'epoch=' + str(epoch) + '__Wstyle=' + str("%.1e" % STYLE_WEIGHT) + '__Wcode=' + str(
                    "%.1e" % CODE_WEIGHT) + '__Wcontent' + str(
                    "%.1e" % CONTENT_WEIGHT) + '.jpg'

                image = utils.get_epoch_image(y, OUTPUT_DIR, code_img, version, module_num=moduleNum, module_size=moduleSize, addpattern=True)
                outputImages.append(image)

                output['epoch'] = epoch
                output['image'] = image
                output['gif'] = makeGif(outputImages, OUTPUT_DIR)

        return total_loss

    print(" Start training =============================================")
    for e in range(EPOCHS):

        global epoch
        global output

        epoch = e

        optimizer.step(closure)

        if output:
            yield output
            output = None
