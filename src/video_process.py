import cv2 as cv
import os, sys
import subprocess
import platform

def merge_with_fade(original, lipsynced):
    outfile_path = './src/static/video/result1.mp4'
    
    isExist = os.path.exists('./src/static/video/front.ts')
    if isExist:
        os.remove('./src/static/video/front.ts')

    isExist = os.path.exists(outfile_path)
    if isExist:
        os.remove(outfile_path)

    cap = cv.VideoCapture(lipsynced)
    fps = cap.get(cv.CAP_PROP_FPS)      # OpenCV v2.x used "CV_CAP_PROP_FPS"
    frame_count = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    duration_1 = frame_count/fps

    cap = cv.VideoCapture(original)
    fps = cap.get(cv.CAP_PROP_FPS)      # OpenCV v2.x used "CV_CAP_PROP_FPS"
    frame_count = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    duration_2 = frame_count/fps
    fade = 0.1
    lenth = duration_1 + duration_2 - fade


    command = 'ffmpeg -i {} -i {} -filter_complex "color=black:1280x720:d={}[base];  [0:v]setpts=PTS-STARTPTS[v0];  [1:v]format=yuva420p,fade=in:st=0:d={}:alpha=1, setpts=PTS-STARTPTS+(({}-{})/TB)[v1];  [base][v0]overlay[tmp];  [tmp][v1]overlay,format=yuv420p[fv];  [0:a][1:a]acrossfade=d={}[fa]" -map [fv] -map [fa] {}'.format(lipsynced, original, lenth, fade, duration_1, fade, fade, outfile_path)
    subprocess.call(command, shell=platform.system() != 'Windows')
    print('generated outputfile!!!')
    return outfile_path


