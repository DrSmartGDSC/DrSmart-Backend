# -*- coding: utf-8 -*-
"""Untitled19.ipynb

Automatically generated by Colaboratory.
Creat by Ahmed Haytham
Original file is located at
    https://colab.research.google.com/drive/1JBjjBMqPLcZYulf0xiOIfBZL4EHW0G2s
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras import models, layers
import matplotlib.pyplot as plt
from tensorflow import keras
from models import SkinDisease, LungDisease

skin_class_names = None
# class_names =['Acne and Rosacea Photos',
# 'Actinic Keratosis Basal Cell Carcinoma and other Malignant Lesions',
# 'Atopic Dermatitis Photos',
# 'Cellulitis Impetigo and other Bacterial Infections',
# 'Eczema Photos',
# 'Lupus and other Connective Tissue diseases',
# 'Melanoma Skin Cancer Nevi and Moles',
# 'Nail Fungus and other Nail Disease',
# 'Poison Ivy Photos and other Contact Dermatitis',
# 'Psoriasis pictures Lichen Planus and related diseases',
# 'Tinea Ringworm Candidiasis and other Fungal Infections',
# 'Urticaria Hives',
# 'Warts Molluscum and other Viral Infections']
lung_class_names = None

image_size = 128

skin_model = keras.models.load_model('../skin_model.h5')  # Model Path .h5
lung_model = keras.models.load_model('../lung_model.h5')  # Model Path .h5


def getSkinClasses(app):
    global skin_class_names
    with app.app_context():
        skin_class_names = {c.name: c.id for c in SkinDisease.query.order_by(SkinDisease.id).all()}

def getLungClasses(app):
    global lung_class_names
    with app.app_context():
        lung_class_names = {c.name: c.id for c in LungDisease.query.order_by(LungDisease.id).all()}



def predict_s(img):
    arr = plt.imread(img, 0)  # image path don't forget 0

    # image size  don't play in it
    n = tf.image.resize(arr, (image_size, image_size))

    img_array = tf.keras.preprocessing.image.img_to_array(n.numpy())
    img_array = tf.expand_dims(img_array, 0)

    test_predict = skin_model.predict(img_array)

    prob_test = np.sort(test_predict, axis=1)
    name_test = np.argsort(test_predict, axis=1)
    prob_names = prob_test[:, -3:].tolist()
    names = name_test[:, -3:].tolist()
    names = [[list(skin_class_names.keys())[i] for i in n] for n in names]

    result = []

    for i, n, p in zip(range(1, 5), names, prob_names):
        for clas, pp in zip(n[::-1], p[::-1]):
            result.append({
                'name': clas,
                "confidence": pp*100,
                'id': skin_class_names[clas]
            })

    return result

def predict_l(img):
    class_names = lung_class_names
    
    arr = plt.imread(img, 0)  # image path don't forget 0

    # image size  don't play in it
    n = tf.image.resize(arr, (224, 224))

    img_array = tf.keras.preprocessing.image.img_to_array(n.numpy())
    img_array = tf.expand_dims(img_array, 0)

    test_predict = lung_model.predict(img_array)

    prob_test = np.sort(test_predict, axis=1)
    name_test = np.argsort(test_predict, axis=1)
    prob_names = prob_test[:, -3:].tolist()
    names = name_test[:, -3:].tolist()
    names = [[list(class_names.keys())[i] for i in n] for n in names]

    result = []

    for i, n, p in zip(range(1, 5), names, prob_names):
        for clas, pp in zip(n[::-1], p[::-1]):
            result.append({
                'name': clas,
                "confidence": pp*100,
                'id': class_names[clas]
            })

    return result
