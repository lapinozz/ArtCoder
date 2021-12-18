import js2py
import json

from timeit import default_timer as timer

def segmentData(data, level, minVer=1, maxVar=40):
    startTime = timer()

    segmentationGenerator = open("./src/segmentation/segmentation_generator.js", "r").read()
    segmentationGenerator = segmentationGenerator.replace("$DATA", data)
    segmentationGenerator = segmentationGenerator.replace("$LEVEL", str(level))
    segmentationGenerator = segmentationGenerator.replace("$MIN_VER", str(minVer))
    segmentationGenerator = segmentationGenerator.replace("$MAX_VER", str(maxVar))

    result = js2py.eval_js(segmentationGenerator)
    result = json.loads(result)

    minVersion = result['version']
    segments = result['segments']

    print('minimum version:', minVersion)
    print('segments: ', end='')
    for segment in segments:
        print(segment['mode'], ':', segment['num'], ' ', sep='', end='')
    print('')

    print("segmentation time: {}s".format(timer() - startTime))

    return minVersion, segments