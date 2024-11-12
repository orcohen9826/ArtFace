# FaceRecognition.py
import time
from APIHandler import APIHandler
import cv2
import os
import json
import show_to_screen
from utilities import *
from show_to_screen import *

#define ofset for bbox
OFFSET = 100
#debug mode
DEBUG = 2 # 1 - show croped face,


#this confidense send to the api to get recognized faces
confidence_for_face_recognition = 0.6
#confidense for face detection below it will skip the face
#from a first check it around 0.6 - 0.8
confidence_for_face_detection = 0.7 # calibrate the confidense for face detection to avoid blury faces and cat faces
#confidense for add image to train model, above it will add the image to train model
confidence_for_face_registration = 0.9 # calibrate the confidense for face registration to avoid mistakely register faces
#confidense for suspected new user below it will suspect that the user is new user
confidence_for_suspected_new_user = 0.8  # calibrate the confidense for suspected new user to avoid mistakely register faces
#cofidence for unite suspected user above it will unite the suspected user to old user
confidence_for_unite_suspected_user = 0.3 # calibrate the confidense for face re registration to avoid mistakely register faces
class FaceRecognition:
    def __init__(self):
        if not os.path.exists("users.json"):
            self.users = {}
        else:
            self.users = read_users_from_file()
        self.final_tree_hight = 1
        
    def generate_id(self):
        return str(len(self.users)).zfill(5)

    # def face_recognition(self, image_path):
    #     image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    #     if image is None:
    #         print(f"Failed to load image: {image_path}")
    #         return False

    #     bbox_list = APIHandler.get_bbox_list(image)
    #     if not bbox_list or 'predictions' not in bbox_list:
    #         print("bbox_list is empty or no predictions in bbox_list")
    #         return False
    #     if DEBUG == 1:#TODO: add to diffrent function\
    #         #show the image
    #         temp_img = draw_bboxes_on_image(image, bbox_list)
    #         #resize image to fit screen
    #         temp_img = cv2.resize(temp_img, (IMAGE_WIDTH, IMAGE_HIGHT))
    #         cv2.imshow("image",temp_img)
    #         cv2.waitKey(0)
    #         cv2.destroyAllWindows()
    #         print(bbox_list)

    #     for bbox in bbox_list['predictions']:
    #         #if bbox cofidence is less then bbox_confidence_limit continue to next bbox
    #         if bbox['confidence'] < bbox_confidence_limit:
    #             continue

    #         x_min, y_min = max(0, bbox['x_min']), max(0, bbox['y_min'])
    #         x_max, y_max = min(image.shape[1], bbox['x_max']), min(image.shape[0], bbox['y_max'])

    #         face = image[y_min:y_max, x_min:x_max]

    #         recognition_result = APIHandler.face_recognition(face)
    #         print()
    #         print("recognition_result",recognition_result)
    #         print()
    #         if 'predictions' not in recognition_result or len(recognition_result['predictions']) == 0:
    #             continue


    #         if DEBUG == 1:#TODO: add to diffrent function
    #             #print the bbox (x,x,y,y) 
    #             print(bbox['x_min'],bbox['x_max'],bbox['y_min'],bbox['y_max'])
    #             #print the bboxx (x,y,w,h
    #             print(bbox['x_min'],bbox['y_min'],bbox['x_max']-bbox['x_min'],bbox['y_max']-bbox['y_min'])
    #             cv2.imshow("face",face)
    #             cv2.waitKey(0)
    #             cv2.destroyAllWindows()


    #         prediction = recognition_result['predictions'][0]
    #         userid = prediction.get("userid", "unknown")
    #         confidence = round(prediction.get("confidence", 0), 2)

    #         if userid == "unknown":
    #             userid = self.generate_id()
    #             if not APIHandler.register_face(face, userid):
    #                 print("Failed to register face.")
    #                 return False

    #             self.users[userid] = {'images': {self.get_image_name(image_path): confidence},
    #                                   'face_coords': {'x_min': x_min, 'y_min': y_min,
    #                                                   'x_max': x_max, 'y_max': y_max}}
    #         else:
    #             if userid not in self.users:
    #                 print("userif",userid)
    #                 self.users[userid] = {'images': {}, 'face_coords': {}}
    #             self.users[userid]['images'][get_image_name(image_path)] = confidence

    #     return True



    #function recive user id and show image of is face ( by his bbox bounding box)
    def show_user_images(self, userid, confidence =0.4):
        if userid not in self.users:
            print("FROM def show_user_images: userid not in self.users")
            print()
            return
        for image_name, image_confidence in self.users[userid]['images'].items():           
            if image_confidence >= confidence:
                image_path = f"images/{image_name}.jpg"
                show_image(image_path)

    #delet all registered faces
    def delete_all_registered_faces(self):
        #loop until registred_faces is empty
        count = 0
        while True:
            registred_faces = APIHandler.get_registered_faces_list()
            debug_print( 2 , registred_faces)
            if not registred_faces or 'faces' not in registred_faces:
                print("registred_users is empty or no users in registred_users")
                return
            for face in registred_faces['faces']:
                #check if delete face failed
                if not APIHandler.delete_face(face):
                    debug_print( 2 , "Failed to delete face.")
                    print("Failed to delete face.")
            count += 1
            if count > 10:
                debug_print( 2 , "registred_faces is not empty after 10 tries")        
            registred_faces = APIHandler.get_registered_faces_list()

            if len(registred_faces['faces']) == 0:
                print("all registred faces deleted")
                return True

        
            

            
        

    #return userid by image
    def get_userid_by_image(self, image_path):
        #TODO: need to find also a similar faces . optional to campare face with users face
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        res = APIHandler.face_recognition(image)
        if not res or 'predictions' not in res or len(res['predictions']) == 0:
            return None
        return res['predictions'][0].get("userid", None)


    #function that run on all images in images folder and apply face recognition on them
    def run_on_all_images(self, imagelimite):
        #limit the number of images to run on
        count = 0   
        for image_name in os.listdir("images"):
            count += 1
            image_path = f"images/{image_name}"
            if not self.process_image(image_path):
                print("Face recognition failed.")
            if(count > imagelimite):
                break
            #print precetage of images that run on from the imagelimite
            print(str(int((count/imagelimite)*100)) + "%")



#***********************************#
     #       
    def process_image(self, image_path):
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if image is None:
            debug_print( 2 , "Failed to load image: {image_path}") #set debug mode to 2 for printing error msg only
            return False
        ### dedect faces ###
        detected_faces_list = APIHandler.get_bbox_list(image , confidence_for_face_detection) 
        if not detected_faces_list or 'predictions' not in detected_faces_list:
            debug_print( 2 , "detected_faces_list is empty or no predictions in detected_faces_list") #set debug mode to 2 for printing error msg only
            return False
        debug_show_detection_image(4,image_path, detected_faces_list)
        ### face recognition ###
        recognized_faces_list = APIHandler.face_recognition(image ,confidence_for_face_recognition)
        if not recognized_faces_list or 'predictions' not in recognized_faces_list:
            debug_print( 2 , "recognized_faces_list is empty or no predictions in recognized_faces_list")
            return False       
        # itarate over all recognized faces if ut unknoun register it
        debug_show_detection_image(4,image_path, recognized_faces_list)
        for recognized_face in recognized_faces_list['predictions']:
            if validated_face(recognized_face, detected_faces_list) == False:#check if the face is valid by checking if the face is in the detected_faces_list
                debug_print( 2 , "skip face")
                continue
            #face_coords looks like this: ('x_min': x_min, 'y_min': y_min,'x_max': x_max, 'y_max': y_max )

            face_coords = {'x_min': recognized_face['x_min'], 'y_min': recognized_face['y_min'],'x_max': recognized_face['x_max'], 'y_max': recognized_face['y_max'] }
            face_image = crop_bbox_with_offset(face_coords , image)# TODO: need to  handling debug
            if recognized_face['userid'] == "unknown":
                #register face
                userid = self.generate_id()
                if not APIHandler.register_face(face_image, userid):
                    debug_print( 2 , "WARNING!!! Failed to register face.")#TODO: maybe need to update userid ganeartor that this uaerid not taken
                    return False
                self.add_image_to_user(userid, image_path, recognized_face['confidence'], face_coords)  
            # else it will check if the confidence is higher then confidence_for_face_registration and register it
            else: 
                if recognized_face['confidence'] < confidence_for_suspected_new_user:# if we have userid but the confidence is too low
                    # add to suspected new user
                    print("suspected new user")
                    self.add_to_suspected_new_user(recognized_face['userid'], recognized_face['confidence'], image_path, face_coords)
                    continue
                if recognized_face['confidence'] > confidence_for_face_registration:
                    #register face using calculate bbox with offset
                    if not APIHandler.register_face(face_image, recognized_face['userid']):
                        debug_print( 2 , "WARNING!!! Failed to register face.")
                        return False
                    self.add_image_to_user(recognized_face['userid'], image_path, recognized_face['confidence'], face_coords)
                self.add_image_to_user(recognized_face['userid'], image_path, recognized_face['confidence'])

        return True
                
    #function that add suspected new user to the users list                
    def add_to_suspected_new_user(self, userid, confidence , image_path , face_cords):
        """
        here we suspect that the user is new user and we need to add him to suspected new user 
        for now we will register him as new user but we will add to the user data that he is suspected to be a old
        user we will apdate face_image, initial_confidence, suspected_userid , tree_hight
        the tree_hight is the number of "suspected fathers" that this user have
        """
        face_image = crop_bbox_with_offset(face_cords , image_path)
        new_userid = self.generate_id()
        if not APIHandler.register_face(face_image, new_userid):
            debug_print( 2 , "Failed to register face.")
            return False
        self.users[new_userid] = {'images': {}, 'face_data': {}, 'suspected_data': {}}
        self.users[new_userid]['images'][get_image_name(image_path)] = confidence
        self.users[new_userid]['face_data'][image_path] = face_cords 
        self.users[new_userid]['suspected_data']['suspected_userid'] = userid
        self.users[new_userid]['suspected_data']['initial_confidence'] = confidence
        if self.users[userid].get('suspected_data', None) == None:
            tree_hight = 1
        else:
            tree_hight = self.users[userid]['suspected_data']['tree_hight'] + 1
            self.final_tree_hight = max(self.final_tree_hight, tree_hight)
        self.users[new_userid]['suspected_data']['tree_hight'] = tree_hight

    #function that add image to user
    def add_image_to_user(self, userid, image_path, confidence , face_cords = None):
        if userid not in self.users:
            self.users[userid] = {'images': {}, 'face_data': {}}
        self.users[userid]['images'][get_image_name(image_path)] = confidence
        if face_cords != None:
            self.users[userid]['face_data'][image_path]= face_cords 

    #function to get face image from user dict
    def get_face_image(self, userid):
        if userid not in self.users:
            debug_print( 2 , "userid not in self.users")
            return
        image_path, face_coords = next(iter(self.users[userid]['face_data'].items()))#get first item from dict
        face_image = crop_bbox_with_offset(face_coords , image_path)
        return face_image


    def re_evaluate_suspected_users(self):
        #TODO: add proper description
        """
        this function will re evaluate all suspected users
        first itarate all users and check if they have suspected user
        if they have suspected user it will check if the suspected user is still suspected user
        """
        #second itarate all suspected new users
        debug_print( 2 , "initcating process of suspected new users")

        united_users_count = 0
        #TODO: need to think on diffrent approch
        #handeling the tree hight first onliy tree hight  = final_tree_hight then tree hight = final_tree_hight -1 and so on
       # while True:
  
        tree_level = self.final_tree_hight
        userids_to_delete = []
        while tree_level > 0:
            for userid in self.users:
                if self.users[userid].get('suspected_data', None) == None:
                    continue
                if self.users[userid]['suspected_data']['tree_hight'] != tree_level:
                    continue
                temp_userid = str(userid)#userid off current user
                face_image = self.get_face_image(temp_userid)
                suspect_userid = self.users[userid]['suspected_data']['suspected_userid'] #userid off the user "father"
                initial_confidence = self.users[userid]['suspected_data']['initial_confidence']
                #delete userid from server
                if not APIHandler.delete_face(temp_userid):
                    debug_print( 2 , "Failed to delete face.")
                    return False
                #chacke the new confidence higher then the initial_confidence
                new_user_resoult = APIHandler.face_recognition(face_image)
                if not new_user_resoult or 'predictions' not in new_user_resoult or len(new_user_resoult['predictions']) == 0:
                    debug_print( 2 , "new_userid is empty or no predictions in new_userid")
                    return False
                #ig the new userid is unknown register it again and skip to next suspected user
                if new_user_resoult['predictions'][0].get("userid", None) == "unknown":# maybe need to add to condition "or cofidancer lower than somthing "
                    #register face
                    if not APIHandler.register_face(face_image, temp_userid):
                        debug_print( 2 , "Failed to register face.")
                        return False
                    continue #skip to next suspected user
                new_confidence = new_user_resoult['predictions'][0].get("confidence", None)
                #if new_confidence to the suspected user is higher then initial_confidence unite the users
                if new_confidence > initial_confidence and new_confidence > confidence_for_unite_suspected_user:
                    #unite all images from suspected user to old userid
                    united_users_count += 1
                    self.users[suspect_userid]['images'].update(self.users[temp_userid]['images'])
                    #register again but with the name of the old user ( and the face of the current user)
                    #register face
                    if not APIHandler.register_face(face_image, suspect_userid):
                        debug_print( 2 , "Failed to register face.")
                        return False

                    #add to list for future delete suspected user
                    userids_to_delete.append(temp_userid)
                    #del self.users[suspect_userid]
                    #TODO:develop this logic
                
                if new_confidence < initial_confidence:# leave it as new user ( need to consider when it unknown the confidance wiil be zero too)
                    #register face#TODO: need to train again on multiple images
                    if not APIHandler.register_face(face_image, temp_userid):
                        debug_print( 2 , "Failed to register face.")
                        return False
                    continue #skip to next suspected user
                debug_print( 2 , "new_confidence is lower then initial_confidence but higher then confidence_for_unite_suspected_user")
                tree_level -= 1
        for userid in userids_to_delete:
            del self.users[userid]

    
    def save_registered_faces_to_folder(self):
        save_users_faces_to_folder(self.users)


        
    #TODO: need to debug this function 
    #TODO: function to register user by multiple images. each time the function called it will  register the user again with the new image and the old images
    def register_user_by_multImages(self, userid, new_face_image):
        if new_face_image is None:
            print("Could not open or find the image")
            return  
        image_data = [] 
        image_data.append(new_face_image)         
        #itarate over all images in user dict ander 'face_data' key
        for image_path, face_coords in self.users[userid]['face_data'].items():
            image = crop_bbox_with_offset(face_coords , image_path)
            if image is None:
                print("Could not open or find the image")
                return
            image_data.append(image)
        #TODO: add aditional logic to select the best images for registration
        #register face
        if not APIHandler.register_face(image_data, userid):
            print("Failed to register face.")
            return False
        return True
            




            








    #function to test the face detection, the function will check all images in images folder and run face detection on them and print the result
    def test_face_detection(self):
        for image_name in os.listdir("images"):
            image_path = f"images/{image_name}"
            image = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if image is None:
                print(f"Failed to load image: {image_path}")
                continue
            bbox_list = APIHandler.get_bbox_list(image , confidence_for_face_detection)
            if not bbox_list or 'predictions' not in bbox_list:
                print("bbox_list is empty or no predictions in bbox_list")
                continue
            debug_show_detection_image(4,image_path, bbox_list)

    






if __name__ == "__main__":

    print("***********************************")
    print("deleting json file")  
    delete_data_file()
    print("***********************************")
    print ("deleting old face images")
    delete_users_faces_folder()
    print("***********************************")
    print("initcating face recognition")
    face_recognition = FaceRecognition()
    #delete all registered faces
    print("***********************************")
    print("deleting all registered faces")
    face_recognition.delete_all_registered_faces()
    #print registered faces list from api
    print("***********************************")
    print("registered faces list from api:")
    print(APIHandler.get_registered_faces_list())
    print("***********************************")
    print("***********************************")
    print("processing images")
    face_recognition.run_on_all_images(10 )
    print("***********************************")
    print("registering users to file")
    write_users_to_file(face_recognition.users)
    print("***********************************")
    print("re evaluating suspected users")
    face_recognition.re_evaluate_suspected_users()
    print("***********************************")
    print("saving registered faces to folder")
    face_recognition.save_registered_faces_to_folder()
    print("***********************************")



    ##face_recognition.show_user_images("00003",0.3)







    # #process image(820).jpg
    # # image_path = "images/image (22).JPG"
    # # face_recognition.process_image(image_path)
    # #face_recognition.re_evaluate_suspected_users()












    #get user id by image

    #userid = face_recognition.get_userid_by_image(image_path)
    #print(userid)
    #face_recognition.show_user_images(userid,0.7)
##############################################################################################
    ####  test face detection ####
##############################################################################################
    # FaceRecognition = FaceRecognition()
    # FaceRecognition.test_face_detection()
##############################################################################################
    ####  test face recognition ####
##############################################################################################
#TODO: need to add test for face recognition
##############################################################################################
    ####  test reevaluate suspected users ####
##############################################################################################
#TODO: need to add test for reevaluate suspected users




    

