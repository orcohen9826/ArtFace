import cv2
import numpy as np
import os
import inspect


"""
here all the functions that show the image to screen and  function for printing
"""

DEBUG = 4

IMAGE_HIGHT = 920
IMAGE_WIDTH = 1280


###### draw rectangle on image ######
def draw_rectangle(image, x, y, width, height):
    copy =image.copy()
    # Draw the rectangle on the image
    cv2.rectangle(copy, (x, y), (x + width, y + height), (0, 255, 0), 2)

    return copy

###### draw confidane and bboxes on image ######
def draw_bboxes_on_image(img, response):
    """
    Draws bounding boxes on the image and places a background behind the text 
    for better visibility based on the server's response.

    Args:
    - image (numpy.ndarray): The original image.
    - response (dict): The response from the server containing predictions.

    Returns:
    - numpy.ndarray: The image with bounding boxes and text with background.
    """

    #check if its an image or image path
    if img is None:
        print("Could not open or find the image")
        return
    if isinstance(img, str):
        img = cv2.imread(img)
    #copy the image
    image = img.copy()
    if not response.get('success', False):
        print("Server response indicates failure. No boxes drawn.")
        return image

    font_scale = 5
    thickness = 15
    color = (0,255, 0)
    font = cv2.FONT_HERSHEY_SIMPLEX

    for prediction in response.get('predictions', []):
        x_min, y_min = prediction['x_min'], prediction['y_min']
        x_max, y_max = prediction['x_max'], prediction['y_max']
        confidence = prediction['confidence']
        #check if there is userid in the prediction
        if 'userid' in prediction:
            userid = prediction['userid']
            label = f"{confidence:.2f}, {userid}"
        else:
            label = f"{confidence:.2f}"

        # Draw the bounding box
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), color , thickness)

        # Text for confidence score
        #label = f"{confidence:.2f}"

        # Get the size of the text box
        (text_width, text_height), _ = cv2.getTextSize(label, font, fontScale=font_scale, thickness=thickness)

        # Calculate the box coordinates for the background
        box_coords = ((x_min, y_min - text_height - 10), (x_min + text_width, y_min))

        # Draw the background box
        cv2.rectangle(image, box_coords[0], box_coords[1], color, cv2.FILLED)

        # Put the text on the image
        cv2.putText(image, label, (x_min, y_min - 10), font, font_scale, (0, 0, 0), thickness)

    return image









def closeWin():
    # Destroy all windows
    cv2.destroyAllWindows()











######################## DEBUG ########################
# it will handele diffrent debug options
# 1 - show the image with the bbox
#2 - only print error msg with out images
def debug_print(debug_mode, msg ):# print the name off the function that call this function and the msg
    function_name = inspect.stack()[1][3]
    if debug_mode <= DEBUG:
        # check if th msg is more complex than string and if it is print nicely
        if isinstance(msg, dict):
            print("******************************")
            print("FROM def",function_name,":")
            for key, value in msg.items():
                print(key, ":", value)
            print("******************************")
            print()
        elif isinstance(msg, str):
            print("******************************")
            print("FROM def",function_name,":",msg)
            print("******************************")
            print()

    pass

def debug_show_detection_image(debug_mode, image, msg):
    if debug_mode <= DEBUG:
        drawed_image = draw_bboxes_on_image(image, msg)
        drawed_image = cv2.resize(drawed_image, (IMAGE_WIDTH, IMAGE_HIGHT))
        image_name = image.split("/")[-1].split(".")[0]
        cv2.imshow(image_name,drawed_image)
        cv2.moveWindow(image_name, 2000, 100)  # Set the position of the window on your screen
        cv2.waitKey(0)
        cv2.destroyAllWindows()

