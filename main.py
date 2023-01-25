# -*- coding: utf-8 -*-
"""main.ipynb のコピー

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oSV5Ec2pOkpyDKyx6617dHJ1KOfheOZx
"""

import os
from flask import Flask, request, redirect, render_template, flash
from werkzeug.utils import secure_filename
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.utils import array_to_img, img_to_array, load_img
from keras.applications.inception_v3 import preprocess_input

import numpy as np
import tensorflow as tf

os.chdir(os.path.dirname(os.path.abspath(__file__)))


classes = ["OK","DEFECT"]
image_size = 200

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'JPG'])

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# TFliteモデルのロード
interpreter = tf.lite.Interpreter(model_path = "qmodel.tflite")
interpreter.allocate_tensors()

# モデルの入出力情報の取得
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('ファイルがありません')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('ファイルがありません')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.mkdir(UPLOAD_FOLDER)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            # 画像のロード & 正規化
            img = img_to_array(load_img(filepath, target_size=(200, 200)))
            input_img = preprocess_input(img)
            # 入力画像のshapeを整形
            input_data = np.expand_dims(input_img, axis = 0)

            # 予測
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()
            output_data = interpreter.get_tensor(output_details[0]['index'])
            pred = output_data.argmax(axis = 1)

            pred_answer = "これは " + classes[pred] + " です"

            return render_template("index.html",answer=pred_answer)

    return render_template("index.html",answer="")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host ='0.0.0.0',port = port)
