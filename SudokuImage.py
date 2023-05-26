import cv2
import numpy as np
from keras.models import load_model
import imutils
from Solver import *


classes = np.arange(0, 10)
model = load_model('model-OCR.h5')
input_size = 48


def get_perspective(img, location, height = 900, width = 900):
    """transforms the detected sudoku in an image into a flat plain"""
    pts1 = np.float32([location[0], location[3], location[1], location[2]])
    pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])

    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    result = cv2.warpPerspective(img, matrix, (width, height))
    return result


def find_board(img):
    """finds the sudoku in a provided image using openCV to detect rectangular boxes"""
    # convert to grey scale then use bilateralFilter to reduce noise
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bfilter = cv2.bilateralFilter(gray, 13, 20, 20)
    # detect edges in image
    edged = cv2.Canny(bfilter, 30, 180)
    # find the contours (sides/continuous lines) in the image
    keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(keypoints)

    # draw image showing contours
    newimg = cv2.drawContours(img.copy(), contours, -1, (0, 255, 0), 3)
    # cv2.imshow("Contour", newimg)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]
    location = None

    # Finds rectangular contour
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 15, True)
        if len(approx) == 4:
            location = approx
            break
    result = get_perspective(img, location)
    return result, location


def split_boxes(board):
    """splits detected rectangles into individual cells for each of the 81 cells in a sudoku"""
    rows = np.vsplit(board,9)
    boxes = []
    for r in rows:
        cols = np.hsplit(r,9)
        for box in cols:
            box = cv2.resize(box, (input_size, input_size))/255.0
            # shows each box in image
            # cv2.imshow("Splitted block", box)
            # cv2.waitKey(100)
            boxes.append(box)
    # cv2.destroyAllWindows()
    return boxes


def display_numbers(img, numbers, color=(0, 0, 255)):
    """Displays 81 numbers in an image at the same position of each cell of the board"""
    W = int(img.shape[1]/9)
    H = int(img.shape[0]/9)
    for i in range (9):
        for j in range (9):
            if numbers[(j*9)+i] !=0:
                cv2.putText(img, str(numbers[(j*9)+i]), (i*W+int(W/2)-int((W/4)), int((j+0.7)*H)), cv2.FONT_HERSHEY_DUPLEX, 2, color, 2, cv2.LINE_AA)
    return img


if __name__ == '__main__':
    # input image
    img = cv2.imread('sudoku2.jpg')

    board, location = find_board(img)

    gray = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
    rois = split_boxes(gray)
    rois = np.array(rois).reshape(-1, input_size, input_size, 1)

    # get prediction
    prediction = model.predict(rois)
    # print(prediction)
    predicted_numbers = []
    # get classes from prediction
    for i in prediction:
        index = (np.argmax(i))
        predicted_number = classes[index]
        predicted_numbers.append(predicted_number)
    #  print(predicted_numbers)
    board_num = np.array(predicted_numbers).astype('uint8').reshape(9, 9)

    try:
        # solves board using Solver.py
        solved_board_nums = get_board(board_num)

        # create a binary array of the predicted numbers. 0 means unsolved numbers of sudoku and 1 means given number.
        # as if reading board like a book from left to right
        binArr = np.where(np.array(predicted_numbers) > 0, 0, 1)
        # print(binArr)
        # get only solved numbers for the solved board
        flat_solved_board_nums = solved_board_nums.flatten() * binArr
        # displays solved numbers in the mask in the same position where board numbers are empty
        solved_board_mask = display_numbers(board, flat_solved_board_nums)
        cv2.imshow("Solved board", solved_board_mask)


    except:
        print("Solution doesn't exist. Model misread digits.")

    # initial unedited image
    cv2.imshow("Input image", img)
    # image corrected to show just the sudoku
    # cv2.imshow("Board", board)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
