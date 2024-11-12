# APIHandler.py
import requests
import numpy as np
import cv2

class APIHandler:
    BASE_URL = "http://_path_to_my_docker_/v1/vision/face"

    @staticmethod
    def post_request(endpoint, image=None, additional_data=None):
        url = f"{APIHandler.BASE_URL}{endpoint}"
        try:
            if image is not None:
                _, encoded_image = cv2.imencode('.jpg', image)
                files = {"image": encoded_image.tobytes()}
                response = requests.post(url, files=files, data=additional_data)
            else:
                response = requests.post(url, data=additional_data)

            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Request Error: {e}")
            return None



    @staticmethod
    def get_bbox_list(image , min_confidence=0.2):
        return APIHandler.post_request("/detect", image=image ,additional_data={"min_confidence": min_confidence})

    @staticmethod
    def face_recognition(image , min_confidence=0.4):
        return APIHandler.post_request("/recognize", image=image ,additional_data={"min_confidence": min_confidence})

    @staticmethod
    def register_face(image_data, userid):
        return APIHandler.post_request("/register", image=image_data, additional_data={"userid": userid})

    #return true if the face was deleted else false
    @staticmethod
    def delete_face(userid):
        #return requests.post(f"{APIHandler.BASE_URL}/delete", data={"userid": userid}).json().get('success', False)
        return APIHandler.post_request("/delete", additional_data={"userid": userid}).get('success', False)


    @staticmethod
    def get_registered_faces_list():
        return APIHandler.post_request("/list")
