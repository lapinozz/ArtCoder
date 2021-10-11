import threading

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms
#from torchviz import make_dot

import numpy as np

from PIL import Image, ImageOps, ImageFilter

from timeit import default_timer as timer

import utils
from SS_layer import SSlayer
from vgg import Vgg16

from segmentation import segmentData
from prepareContent import prepareContent
from qrcode import decodeQr, encodeQr
from saveGif import saveGif

from GPUtil import showUtilization as gpu_usage

epoch = 0

contents = ["boy.jpg", "brad.jpg", "ca.jpg", "dog.jpg", "lapinozz.jpg", "love.jpg", "man.jpg", "panda.jpg", "ship.jpg"]

def combine(codeImg, contentImg, colorized, moduleSize, contrast=1.15, brightness=1.3):
    from PIL import ImageEnhance, ImageFilter
    
    qr = codeImg
    qr = qr.convert('RGBA') if colorized else qr
    
    bg0 = contentImg.convert('RGBA')
    bg0 = ImageEnhance.Contrast(bg0).enhance(contrast)
    bg0 = ImageEnhance.Brightness(bg0).enhance(brightness)

    ms = moduleSize
    ms8 = moduleSize * 8
    ms16 = moduleSize * 16

    #if bg0.size[0] < bg0.size[1]:
    #    bg0 = bg0.resize((qr.size[0]-ms8, (qr.size[0]-ms8)*int(bg0.size[1]/bg0.size[0])))
   # else:
    #    bg0 = bg0.resize(((qr.size[1]-ms8)*int(bg0.size[0]/bg0.size[1]), qr.size[1]-ms8))    
        
    bg = bg0 if colorized else bg0.convert('1')

    c1 = moduleSize/4
    c2 = moduleSize-c1

    #c1 -= 1
    c2 -= 1

    ratio = 0.2

    target = Image.new('RGBA', size=qr.size, color=(0, 0, 0, 0));

    #for i in range(qr.size[0]-ms8):
    #    for j in range(qr.size[1]-ms8):
    for i in range(qr.size[0]):
        for j in range(qr.size[1]):
            #if not ((i in (18,19,20)) or (j in (18,19,20)) or (i<24 and j<24) or (i<24 and j>qr.size[1]-49) or (i>qr.size[0]-49 and j<24) or ((i,j) in aligs) or (i%3==1 and j%3==1) or (bg0.getpixel((i,j))[3]==0)):
            #if not ((i in (18,19,20)) or (j in (18,19,20)) or (i<ms8 and j<ms8) or (i<ms8 and j>qr.size[1]-ms16-1) or (i>qr.size[0]-ms16-1 and j<ms8) or (i%moduleSize==1 and j%moduleSize==1) or (bg0.getpixel((i,j))[3]==0)):
            x=i%moduleSize
            y=j%moduleSize

            #if not ((i<ms8 and j<ms8) or (i<ms8 and j>qr.size[1]-ms16-1) or (i>qr.size[0]-ms16-1 and j<ms8) or (x >= c1 and x <= c2 and y >= c1 and y <= c2) or (bg0.getpixel((i,j))[3]==0)):
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


    return target
    return qr

def artcoder(STYLE_IMG_PATH, CONTENT_IMG_PATH, CODE_PATH, OUTPUT_DIR,
             LEARNING_RATE=0.01, CONTENT_WEIGHT=1e8, STYLE_WEIGHT=1e15, CODE_WEIGHT=1e15, MODULE_SIZE=16, MODULE_NUM=37,
             EPOCHS=50000, Dis_b=80, Dis_w=180, Correct_b=50, Correct_w=200, USE_ACTIVATION_MECHANISM=True):
    # STYLE_IMG_PATH = './style/redwave4.jpg'
    #CONTENT_IMG_PATH = 'C:\\Users\\gsq_apolomat\\OneDrive - Gearbox Software\\Pictures\\Untitled.png'
    # CODE_PATH = './code/boy.jpg'
    # OUTPUT_DIR = './output/'

    utils.del_file(OUTPUT_DIR)

    codeImg = Image.open(CODE_PATH)

    data = decodeQr(codeImg, OUTPUT_DIR)

    #data = 'shc:/5676296952423660346029753764377032273724426270083862254340234565344112613643440433053277380455073940710655655923546329424006676156274533286074605664637428616660372441262860746044427565286166603741327633394460573601064135715371327425270541766261745806740709566142382133033944446861535352686626241270330453637061297409056205083256362256607557613472030928542636002041284052395406277372345457271203364436753076705344763837597604445811265852575204582223775831087569682168074508092962246252412227266221620311286758633839382859113359252050605827686207383808290500073060065407710035210061715559717000072738097722640340652833563736427026622245722806276124066343582968082160084158387465613674127256742076215533052003775223373140724364050050235575083312666061684065755941686176765452122344104028110569567362297227430941597259625241753420642920596924603456684506424538062012266676683344552567076970577776662926326329523171643420225744573827095500586121270671602810384069663471567040292833036164700773457212272232410931216267432603063976077754712559532263384432727174446268673905345727672605124508543457653770304531204475410661417763447176063724755511452270361138426968377512042934037122285030363310542874317129452721220567734228124156406955082137673037003520286824246409387603106744447228386269056554377459626927320468537770525862422720656977607355365760672208247041704237770755003138506624542967576011103310243657345571631139112458723922404572627566737757346766733169295564735735450823301009684073705850770543607600355341625205037066666934526668304520402072573074283420223200570939434441215958086554053169435226712221052560392810223867693504554443596804751126615955044128007574732766533039352366123452307300583430750670745031262471603531407163555827524363327735567235451238390432573272315966686745056576366873290659627611754005535610452742045776070908006375392055502429046135751000215526295009356628253153575854013359443467425837224252350633541056666775203130705311232242690625224442307538746872532671535654767331430812576574716307600655114107205475545674540327437334540469374271112536'
    #data = 'shc:/567629695242366'

    level = 1 # 0 to 3

    version, segments = segmentData(data, level, 1, 40)

    #version += 10
    version = 6
    MODULE_NUM = version * 4 + 17

    contentImg = Image.open(CONTENT_IMG_PATH).convert('RGB')
    contentImg, contentModules, contentWeights = prepareContent(contentImg, MODULE_NUM, MODULE_SIZE, OUTPUT_DIR)

    '''
    for y in contents:
        CONTENT_IMG_PATH = "./content/" + y

        contentImg = Image.open(CONTENT_IMG_PATH)

        contentImg, contentModules, contentWeights = prepareContent(contentImg, MODULE_NUM, MODULE_SIZE, OUTPUT_DIR)
    '''

    codeImg = encodeQr(segments, level, version, contentModules, contentWeights, MODULE_SIZE, OUTPUT_DIR)

    combined = utils.add_pattern(combine(codeImg, contentImg, True, MODULE_SIZE).convert("RGB"), codeImg, version, module_number=MODULE_NUM, module_size=MODULE_SIZE)
    combined.save('test.jpg')
    combined.show()

    #quit()

    #contentImg = combined

    IMAGE_SIZE = MODULE_SIZE * MODULE_NUM

    transform = transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.ToTensor(),
    ])

    torch.cuda.empty_cache()

    vgg = Vgg16(requires_grad=False).cuda()  # vgg16 model
    ss_layer = SSlayer(requires_grad=False, moduleSize=MODULE_SIZE).cuda()

    style_img = utils.load_image(filename=STYLE_IMG_PATH, size=IMAGE_SIZE)
    content_img = contentImg
    code_img = codeImg
    init_img = utils.add_pattern(content_img, code_img, version, module_number=MODULE_NUM, module_size=MODULE_SIZE)

    torch.backends.cudnn.benchmark = True

    #torch.autograd.set_detect_anomaly(False)
    #torch.autograd.profiler.profile(False)
    #torch.autograd.profiler.emit_nvtx(False)

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
        module_size=MODULE_SIZE,
        module_number=MODULE_NUM
    )

    ideal_result = torch.tensor(ideal_result.astype('float32'), device=torch.device('cuda:0'))
    ideal_result_inv = (1 - ideal_result)

    error_matrix = utils.get_action_matrix(
        img_target=y,
        ideal=ideal_result,
        ideal_inv=ideal_result_inv,
        Dis_b=Dis_b, Dis_w=Dis_w,
        module_size=MODULE_SIZE
    )
    code_target = ss_layer(utils.get_target(ideal_result, b_robust=Correct_b, w_robust=Correct_w,
        module_size=MODULE_SIZE,
        module_num=MODULE_NUM))

    trainingTimeStart = timer()
    epochTimeStart = timer()

    print(torch.cuda.get_device_name(0))

    def debug(string, time):
        return
        if True:
            #torch.cuda.empty_cache()
            torch.cuda.synchronize()
            #gpu_usage()
            #print(torch.cuda.memory_summary(device=None, abbreviated=False))
            print(string.format(timer() - time), )

    def closure(code_target=code_target):
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
                module_size=MODULE_SIZE)
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
            activate_num = MODULE_NUM * MODULE_NUM

        time = timer()
        code_loss = CODE_WEIGHT * mse_loss(code_target, code_y)
        content_loss = CONTENT_WEIGHT * mse_loss(fc, fy)  # content loss
        debug("code/content loss: {}", time)

        # tv_loss = TV_WEIGHT * (torch.sum(torch.abs(y[:, :, :, :-1] - y[:, :, :, 1:])) +
        #                        torch.sum(torch.abs(y[:, :, :-1, :] - y[:, :, 1:, :])))

        time = timer()
        total_loss = style_loss + code_loss + content_loss
        #make_dot(total_loss).render("./rnn_torchviz", format="png")
        total_loss.backward(retain_graph=True)
        debug("backward: {}", time)


        if epoch % 20 == 0:
            print(
                "Epoch {}: Style Loss : {:4f}. Content Loss: {:4f}. Code Loss: {:4f}. Activated module number: {:4.2f}. Discriminate_b：{:4.2f}. Discriminate_w：{:4.2f}.".format(
                    epoch, style_loss, content_loss, code_loss, activate_num, Dis_b, Dis_w)
            )

            nonlocal epochTimeStart
            currentTime = timer()
            totalElapsedTime = currentTime - trainingTimeStart
            averageEpoch = currentTime - epochTimeStart
            epochTimeStart = currentTime

            print("Total time: {:4.5f}, Average Epoch Time: {:4.5f}: Global Average Epoch Time: {:4.5f} Time Left: {:4.5f}".format(totalElapsedTime, averageEpoch / 20, totalElapsedTime / (epoch + 1), (EPOCHS - epoch) * totalElapsedTime / (epoch + 1)))

        if epoch % 200 == 0:
            img_name = 'epoch=' + str(epoch) + '__Wstyle=' + str("%.1e" % STYLE_WEIGHT) + '__Wcode=' + str(
                "%.1e" % CODE_WEIGHT) + '__Wcontent' + str(
                "%.1e" % CONTENT_WEIGHT) + '.jpg'
            utils.save_image_epoch(y, OUTPUT_DIR, img_name, code_img, version, module_num=MODULE_NUM, module_size=MODULE_SIZE, addpattern=True)

            threading.Thread(target=saveGif, args=(OUTPUT_DIR,)).start()

            print('Save output: ' + img_name)
        
        return total_loss

    print(" Start training =============================================")
    for e in range(EPOCHS):

        global epoch
        epoch = e

        optimizer.step(closure)
