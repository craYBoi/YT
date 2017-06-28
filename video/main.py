from predict import MnistClassifier
from PIL import Image
import os
import cv2
import numpy as np

ELIM_FIRST_DIGIT = (87, 595, 97, 612)
ELIM_SECOND_DIGIT = (96, 595, 106, 612)
DEATH_FIRST_DIGIT = (420, 636, 430, 653)
DEATH_SECOND_DIGIT = (429, 636, 439, 653)

ELIM_FIRST_DIGIT_K = (86, 589, 96, 606)
# korean 1
ELIM_SECOND_DIGIT_K_1 = (93, 589, 103, 606)
ELIM_SECOND_DIGIT_K = (95, 589, 105, 606)
DEATH_FIRST_DIGIT_K = (419, 625, 429, 642)
DEATH_SECOND_DIGIT_K = (427, 625, 437, 642)
DEATH_SECOND_DIGIT_K_1 = (426, 625, 436, 642)


def get_death(im):
    '''
    Get death number
    '''
    im = im.resize((1280, 720)).convert('L')
    death_1 = im.crop(DEATH_FIRST_DIGIT)
    death_2 = im.crop(DEATH_SECOND_DIGIT)

    # death_2.show()

    death_1_digit = int(get_digit(death_1))
    death_2_digit = int(get_digit(death_2))

    # print elim_1_digit, elim_2_digit

    # empty only happens in elim2
    assert death_1_digit != 10 , 'Elim First Digit is Empty!'

    if death_2_digit == 10:
        return death_1_digit

    return int(str(death_1_digit) + str(death_2_digit))

def get_death_k(im):
    im = im.resize((1280, 720)).convert('L')

    death_1 = im.crop(DEATH_FIRST_DIGIT_K)
    death_1_digit = int(get_digit(death_1, is_k=True))

    if death_1_digit == 1:
        death_2 = im.crop(DEATH_SECOND_DIGIT_K_1)
    else:
        death_2 = im.crop(DEATH_SECOND_DIGIT_K)

    death_2_digit = int(get_digit(death_2, is_k=True))

    assert death_1_digit != 10, 'Death First Digit is Empty'

    if death_2_digit == 10:
        return death_1_digit

    return int(str(death_1_digit) + str(death_2_digit))

def get_elim(im):
    '''
    Get elim number
    '''
    im = im.resize((1280, 720)).convert('L')
    elim_1 = im.crop(ELIM_FIRST_DIGIT)
    elim_2 = im.crop(ELIM_SECOND_DIGIT)

    # elim_1.show()

    elim_1_digit = int(get_digit(elim_1))
    elim_2_digit = int(get_digit(elim_2))

    # print elim_1_digit, elim_2_digit

    # empty only happens in elim2
    assert elim_1_digit != 10 , 'Elim First Digit is Empty!'

    if elim_2_digit == 10:
        return elim_1_digit

    return int(str(elim_1_digit) + str(elim_2_digit))

def get_elim_k(im):
    im = im.resize((1280, 720)).convert('L')

    elim_1 = im.crop(ELIM_FIRST_DIGIT_K)
    elim_1_digit = int(get_digit(elim_1, is_k=True))

    if elim_1_digit == 1:
        elim_2 = im.crop(ELIM_SECOND_DIGIT_K_1)
    else:
        elim_2 = im.crop(ELIM_SECOND_DIGIT_K)

    elim_2_digit = int(get_digit(elim_2, is_k=True))

    assert elim_1_digit != 10, 'Elim First Digit is Empty'

    if elim_2_digit == 10:
        return elim_1_digit

    return int(str(elim_1_digit) + str(elim_2_digit))


def get_digit(input_img, is_k=False):
    '''
    input an croppred grayscale image with single digit value, return single digit string, 10 if empty
    image should be 10 * 17
    '''

    img_data = np.asarray(input_img, dtype=np.float32)

    img_data[:,0] = 5.
    img_data[:,9] = 5.

    img_data = img_data.reshape((1, 170))

    res = []
    for _ in range(20):
        if is_k:
            m = MnistClassifier(is_k=True)
        else:
            m = MnistClassifier()
        m.train()
        res.append(m.predict(img_data)[0])

    counts = np.bincount(np.array(res))
    return np.argmax(counts)


# def get_hero(input_img):
