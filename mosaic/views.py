from django.shortcuts import render, redirect
from django.conf import settings

from .forms import ImageForm
from .models import Image

import cv2


def mosaic_image(request):
    form = ImageForm()
    text = '1人、正面を向いて、眼鏡等は外してください。'

    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            max_id = Image.objects.latest('id').id
            img = Image.objects.get(id=max_id)
            input_path = str(settings.BASE_DIR) +'/uploads/' + img.image.name
            out_name = img.image.name.split("/")
            out_name = out_name[1]
            output_path = str(settings.BASE_DIR) + f'/uploads/images/output_{out_name}'
            text = mosaic_exe(input_path, output_path)
            if text:
                return render(request, 'mosaic/index.html', {'form': form, 'text': text})

            img.mosaic_image = str(settings.BASE_DIR) + f'/uploads/images/output_{out_name}'
            img.save()
            return render(request, 'mosaic/index.html', {'form': form, 'img': img})

    return render(request, 'mosaic/index.html', {'form': form, 'text': text})


def make_mosaic(img, rect, size):
    (x1, y1, x2, y2) = rect
    w = x2 - x1
    h = y2 - y1
    i_rect = img[y1:y2, x1:x2]

    i_small = cv2.resize(i_rect, (size, size))
    i_mos = cv2.resize(i_small, (w, h), interpolation=cv2.INTER_AREA)

    img2 = img.copy()
    img2[y1:y2, x1:x2] = i_mos
    return img2


def mosaic_exe(input_path,output_path):
    cascade_file = "mosaic/haarcascade_frontalface_alt.xml"
    cascade = cv2.CascadeClassifier(cascade_file)

    img = cv2.imread(input_path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_list = cascade.detectMultiScale(img_gray, minSize=(150, 150))
    if len(face_list) == 0:
        text = '''モザイクの生成に失敗しました。
        1人、正面を向いて、眼鏡等は外してください。
        '''
        return text
    for (x, y, w, h) in face_list:
        # print("顔の座標=", x, y, w, h)
        img = make_mosaic(img, (x, y, x + w, y + h), 10)
    cv2.imwrite(output_path, img)
    return ''


