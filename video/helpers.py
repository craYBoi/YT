from PIL import Image
import os
import cv2
import numpy as np
# from pytesseract import image_to_string

import main

ELIM_FIRST_DIGIT = (86, 595, 96, 612)
ELIM_SECOND_DIGIT = (95, 595, 105, 612)
DEATH_FIRST_DIGIT = (419, 636, 429, 653)
DEATH_SECOND_DIGIT = (428, 636, 438, 653)


NUMBERS_PATH = 'ytow/static/template/numbers'


def get_stats2(im, is_k=False):
    if is_k:
        elim = main.get_elim_k(im)
        death = main.get_death_k(im)
    else:

        elim = main.get_elim(im)
        death = main.get_death(im)
    return (elim, death)
    # return (int(elim), int(death))


def get_stats(im):

    im = im.resize((1280, 720))
    first_digit_elim = np.asarray(im.crop(ELIM_FIRST_DIGIT))
    second_digit_elim = np.asarray(im.crop(ELIM_SECOND_DIGIT))

    first_digit_death = np.asarray(im.crop(DEATH_FIRST_DIGIT))
    second_digit_death = np.asarray(im.crop(DEATH_SECOND_DIGIT))

    numbers = os.listdir(NUMBERS_PATH)
    nums = []

    for n in numbers:

        path = os.path.join(NUMBERS_PATH, n)
        num_im = Image.open(path)

        nums.append((n.replace('.png', ''), num_im))



    best_prob_first_digit_elim = 0.20
    best_prob_second_digit_elim = 0.20
    best_num_first_digit_elim = ''
    best_num_second_digit_elim = ''

    best_prob_first_digit_death = 0.20
    best_prob_second_digit_death = 0.20
    best_num_first_digit_death = ''
    best_num_second_digit_death = ''

    for n in nums:
        number_str = n[0]
        number_data = np.asarray(n[1])

        # elim
        res_first_elim = cv2.matchTemplate(first_digit_elim, number_data, cv2.TM_CCOEFF_NORMED)

        if res_first_elim > best_prob_first_digit_elim:
            best_prob_first_digit_elim = res_first_elim
            best_num_first_digit_elim = number_str

        res_second_elim = cv2.matchTemplate(second_digit_elim, number_data, cv2.TM_CCOEFF_NORMED)
        if res_second_elim > best_prob_second_digit_elim:
            best_prob_second_digit_elim = res_second_elim
            best_num_second_digit_elim = number_str


        # death
        res_first_death = cv2.matchTemplate(first_digit_death, number_data, cv2.TM_CCOEFF_NORMED)
        if res_first_death > best_prob_first_digit_death:
            best_prob_first_digit_death = res_first_death
            best_num_first_digit_death = number_str

        res_second_death = cv2.matchTemplate(second_digit_death, number_data, cv2.TM_CCOEFF_NORMED)
        if res_second_death > best_prob_second_digit_death:
            best_prob_second_digit_death = res_second_death
            best_num_second_digit_death = number_str


    result_elim = best_num_first_digit_elim + best_num_second_digit_elim
    result_death = best_num_first_digit_death + best_num_second_digit_death

    if result_elim and result_death:
        return (int(result_elim), int(result_death))
    else:
        return False
