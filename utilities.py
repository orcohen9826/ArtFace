import os
import cv2
import json
from show_to_screen import *
"""

"""
OFFSET = 120
IMAGE_HIGHT = 600
IMAGE_WIDTH = 800
bbox_confidence_limit = 0.2


############ file handling ############
def read_users_from_file():
    with open("users.json", "r") as file:
       return json.load(file)
def write_users_to_file(users):
    with open("users.json", "w") as file:
        json.dump(users, file, indent=4)  # Pretty print the JSON
def delete_data_file():
    if os.path.exists("users.json"):
        os.remove("users.json")


###### resize images ######
def resize_images(images, target_size):
    resized_images = []

    for image in images:
        # Resize the image
        resized_image = cv2.resize(image, target_size)
        resized_images.append(resized_image)

    return resized_images


###### load images from folder ######
def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img_path = os.path.join(folder, filename)
        if os.path.isfile(img_path):
            img = cv2.imread(img_path)
            if img is not None:
                images.append(img)
    images = resize_images(images, (640, 480))

    return images



def crop_bbox_with_offset(bbox , img):
    #check if its an image or image path
    if img is None:
        print("Could not open or find the image")
        return
    if isinstance(img, str):
        img = cv2.imread(img)
    #copy the image
    image = img.copy()
    image_hight = image.shape[0]
    image_width = image.shape[1]
    x_min = max(0, bbox['x_min'] - OFFSET)
    x_max = min(image_width, bbox['x_max'] + OFFSET)
    y_min = max(0, bbox['y_min'] - OFFSET)
    y_max = min(image_hight, bbox['y_max'] + OFFSET)
    return image[y_min:y_max, x_min:x_max]


def get_image_name(image_path):
    return image_path.split("/")[-1].split(".")[0]

#TODO: add function to utils.py
def show_image(image_path,):
    image = cv2.imread(image_path)
    #resize image to fit screen
    image = cv2.resize(image, (IMAGE_WIDTH, IMAGE_HIGHT))
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()







#function that check if the face is valid by checking if the face is in the detected_faces_list
def validated_face(recognized_face, detected_faces_list):
    #check if the face is in the detected_faces_list it will check it with offset 
    models_offset = 100 #TODO: need to calibrate the offset
    #TODO: add debug mode for draw bboxs  on image for calibrate the offset
    recognized_bbox  = recognized_face['x_min'], recognized_face['y_min'], recognized_face['x_max'], recognized_face['y_max']
    for detected_face in detected_faces_list['predictions']:
        detected_bbox = detected_face['x_min'], detected_face['y_min'], detected_face['x_max'], detected_face['y_max']
        #check the absulute value of the diffrence between the bboxs
        if (abs(detected_bbox[0] - recognized_bbox[0]) < models_offset and abs(detected_bbox[1] - recognized_bbox[1]) < models_offset and abs(detected_bbox[2] - recognized_bbox[2]) < models_offset and abs(detected_bbox[3] - recognized_bbox[3]) < models_offset):
            debug_print(2, "validated_face: True")
            return True
    debug_print(2, "validated_face: False")
    return False




#### function to save image to folder ####
def save_image(image, image_name, folder_path = "images/users_faces/"):
    if image is None:
        print("Could not open or find the image")
        return
    cv2.imwrite(folder_path + image_name + ".jpg", image)

### function to write all userids face_images from user dict to folder ###
    #self.users[new_userid]['face_coords'] = face_cords , image_path
def save_users_faces_to_folder(users):
    for userid, user in users.items():
        image_path, face_coords = next(iter(users[userid]['face_data'].items()))
        face_image = crop_bbox_with_offset(face_coords , image_path)
        if face_image is  None:
            print("face image is  none here 0")   
        face_image = write_name_on_image(face_image, userid, (50, 50))  
        if face_image is  None:
            print("face image is none here 1")   
        if face_image is  None:
            print("face image is none here")      
        save_image(face_image, userid)


def write_name_on_image(image, name, position):
    # Check if image is loaded
    if image is None:
        print("Could not open or find the image")
        return

    # Set font type and font scale
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = (255, 0, 0)  # Blue color in BGR
    thickness = 2  # Line thickness of 2 px

    # Put the text on the image
    cv2.putText(image, name, position, font, font_scale, color, thickness, cv2.LINE_AA)

    # Wait for a key press and close all windows
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return image    





#function to delete images from user faces folder
def delete_users_faces_folder():
    folder = "images/users_faces/"
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

