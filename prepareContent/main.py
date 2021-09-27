import utils
from .saliency import getSaliency

import cv2
import numpy as np
from PIL import Image

import os
from timeit import default_timer as timer

def asStride(arr,sub_shape,stride):
    '''Get a strided sub-matrices view of an ndarray.
    See also skimage.util.shape.view_as_windows()
    '''
    s0,s1=arr.strides[:2]
    m1,n1=arr.shape[:2]
    m2,n2=sub_shape
    view_shape=(1+(m1-m2)//stride[0],1+(n1-n2)//stride[1],m2,n2)+arr.shape[2:]
    strides=(stride[0]*s0,stride[1]*s1,s0,s1)+arr.strides[2:]
    subs=np.lib.stride_tricks.as_strided(arr,view_shape,strides=strides)
    return subs

def poolingOverlap(mat,ksize,stride=None,method='max',pad=False):
    '''Overlapping pooling on 2D or 3D data.
    <mat>: ndarray, input array to pool.
    <ksize>: tuple of 2, kernel size in (ky, kx).
    <stride>: tuple of 2 or None, stride of pooling window.
              If None, same as <ksize> (non-overlapping pooling).
    <method>: str, 'max for max-pooling,
                   'mean' for mean-pooling.
    <pad>: bool, pad <mat> or not. If no pad, output has size
           (n-f)//s+1, n being <mat> size, f being kernel size, s stride.
           if pad, output has size ceil(n/s).
    Return <result>: pooled matrix.
    '''

    m, n = mat.shape[:2]
    ky,kx=ksize
    if stride is None:
        stride=(ky,kx)
    sy,sx=stride

    _ceil=lambda x,y: int(np.ceil(x/float(y)))

    if pad:
        ny=_ceil(m,sy)
        nx=_ceil(n,sx)
        size=((ny-1)*sy+ky, (nx-1)*sx+kx) + mat.shape[2:]
        mat_pad=np.full(size,np.nan)
        mat_pad[:m,:n,...]=mat
    else:
        mat_pad=mat[:(m-ky)//sy*sy+ky, :(n-kx)//sx*sx+kx, ...]

    view=asStride(mat_pad,ksize,stride)

    if method=='max':
        result=np.nanmax(view,axis=(2,3))
    else:
        result=np.nanmean(view,axis=(2,3))

    return result

def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    # return the edged image
    return edged

def prepareContent(contentImg, moduleCount, moduleSize, outputDir):
    startTime = timer()

    w, h = contentImg.size
    minSize = min(w, h)
    marginW = (w - minSize) / 2
    marginH = (h - minSize) / 2
    contentBox = (marginW, marginH, w - marginW, h - marginH)
    targetSize = (moduleCount * moduleSize, moduleCount * moduleSize)
    contentImg = contentImg.resize(targetSize,  Image.BICUBIC, contentBox, 2.0)
    contentImg.save(os.path.join(outputDir, "content.png"))

    contentModules = utils.get_ideal_result(img_code=contentImg, module_size=moduleSize, module_number=moduleCount).astype(dtype=bool)
    Image.fromarray(contentModules).save(os.path.join(outputDir, "content_modules.png"))

    scale = moduleSize / 2
    canny = np.array(contentImg.convert('RGB'))
    canny = cv2.resize(canny, (0,0), fx=1./scale, fy=1./scale)
    #canny = auto_canny(canny, 1) #cv2.Canny(canny, 200, 300)
    canny = cv2.Canny(canny, 250, 450)
    canny = cv2.resize(canny, (0,0), fx=scale, fy=scale)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    canny = cv2.dilate(canny, kernel)
    Image.fromarray(canny).convert('L').save(os.path.join(outputDir, "content_edges.png"))
    canny = canny.astype(np.float32) / 255

    sal = getSaliency(np.array(contentImg)[...,::-1].astype(np.float32), moduleSize, 15, 100)
    Image.fromarray((sal).astype('uint8') * 255).save(os.path.join(outputDir, "content_saliency.png"))

    width, height = contentImg.size
    heu = np.fromfunction(lambda i, j: (i*width + j*height - i*i - j*j) / width*width*0.5, (width, height), dtype=np.float32)
    minH = np.min(heu)
    heu = (heu - minH)/(np.max(heu) - minH)

    weights = canny*0.67 + sal*0.23 + heu*0.1
    Image.fromarray(weights * 255).convert('L').save(os.path.join(outputDir, "content_weights.png"))

    weights = poolingOverlap(weights, (moduleSize, moduleSize), None, 'mean')
    Image.fromarray(weights * 255).convert('L').save(os.path.join(outputDir, "content_weights_pooled.png"))

    print("content prepared: {}s".format(timer() - startTime))

    return contentImg, contentModules, weights

