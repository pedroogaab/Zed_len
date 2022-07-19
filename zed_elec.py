#!../ZedVenv/bin/python

import os

import cv2
import matplotlib.pyplot as plt
import pyzed.sl as sl
import numpy as np


class ZedDetector:
    def electronic_detect():
        # ========================================================================================================
        # -----------------------------------------------------------
        # Criando um objeto da câmera e configurando alguns parâmetros
        # iniciais.
        camera = sl.Camera()
        init_paremeters = sl.InitParameters(
            camera_fps=30,
            camera_resolution=sl.RESOLUTION.HD1080,
            depth_mode=sl.DEPTH_MODE.ULTRA,
            sdk_verbose=True,
            coordinate_units=sl.UNIT.CENTIMETER,
            depth_minimum_distance=20.0,
            depth_maximum_distance=350.0,
        )
        status = camera.open(init_paremeters)
        if status != sl.ERROR_CODE.SUCCESS:
            print("\033[1;31mERROR:\033[m {}".format(status))
            exit(1)
        # -----------------------------------------------------------
        # Criando um objeto com o módulo de detecção de objetos
        # e configurando alguns parâmetros iniciais.
        detect_parameters = sl.ObjectDetectionParameters(
            detection_model=sl.DETECTION_MODEL.MULTI_CLASS_BOX,
            enable_tracking=True,
            image_sync=True
        )
        # Habilitando o positional tracking na câmera
        # e configurando o chão como origem.
        if detect_parameters.enable_tracking:
            tracking_parameters = sl.PositionalTrackingParameters()
            tracking_parameters.set_floor_as_origin = True
            camera.enable_positional_tracking(tracking_parameters)

        status = camera.enable_object_detection(detect_parameters)
        if status != sl.ERROR_CODE.SUCCESS:
            print("\033[1;31mERROR:\033[m {}".format(status))
            exit(1)
        # -----------------------------------------------------------
        # Configurando a precisão da detecção para 60%.
        runtime_detect_parameters = sl.ObjectDetectionRuntimeParameters(
            detection_confidence_threshold=60,
            object_class_filter = [sl.OBJECT_CLASS.ELECTRONICS]
        )
        # -----------------------------------------------------------
        # Criando os módulos para rodar a câmera, coletar os
        # dados do objeto detectado e a imagem pega pela
        # câmera.
        runtime = sl.RuntimeParameters()
        objects = sl.Objects()
        image_camera = sl.Mat()
        depth_map = sl.Mat()

        key = None

        colors = [(225,64,101),(0,145,242),(76,220,105),(34,34,252),(186,85,159),(26,78,118),(207,45,239),(107,107,107),(109,212,212),(232,220,116)]

        # Dicionário aonde será armazenado os tempos de entrada
        # e saida de cada objeto.
        obj_id = {}

        # ========================================================================================================
        
        while True:

            status = camera.grab(runtime)
            if status != sl.ERROR_CODE.SUCCESS:
                print("\033[1;31mERROR:\033[m {}".format(status))
                exit(1)

            # Coletando a imagem e os objetos vistos pela câmera esquerda.
            camera.retrieve_image(image_camera, sl.VIEW.LEFT)
            camera.retrieve_objects(objects, runtime_detect_parameters)

            camera.retrieve_measure(depth_map, sl.MEASURE.DEPTH)

            # Armazenando os dados da imagem.
            frame = image_camera.get_data()

            obj_list = objects.object_list

            if len(obj_list):
                for i, obj in enumerate(obj_list):

                    obj_id = obj.id
                    objects.get_object_data_from_id(obj, obj_id)
                    coordinates = obj.bounding_box_2d

                    start_points = (int(coordinates[0][0]), int(coordinates[0][1]))
                    end_points = (int(coordinates[2][0]), int(coordinates[2][1]))


                    cord_top = int((coordinates[0][0]+coordinates[1][0])/2)
                    cord_bot = int((coordinates[3][0]+coordinates[2][0])/2)
                    ponto_m = int((coordinates[0][1]+coordinates[3][1])/2)



                    info_points_x = (
                        int(coordinates[0][0]) - 4,
                        int(coordinates[0][1]) - 100,
                    )
                    info_points_y = (
                        int(coordinates[1][0]) + 4,
                        int(coordinates[1][1])
                    )
                    # -----------------------------------------------------------
                    color_text = (255,255,255)
                    font_text = cv2.FONT_HERSHEY_DUPLEX
                    thickness_text = 2
                    thickness = 8
                    text_id = "ID: {}".format(i)

                    cv2.rectangle(frame, start_points, end_points, colors[i], thickness)
                    cv2.rectangle(frame, info_points_x, info_points_y, colors[i], -1)
                    cv2.rectangle(frame, (int(coordinates[0][0]),int(coordinates[2][1])),(int(coordinates[0][0])+185,int(coordinates[2][1])),colors[i],-1)
                    cv2.putText(frame, "Len: ", (int(coordinates[0][0]+10),int(coordinates[0][1]-7)), font_text, 1, color_text, thickness_text)
                    cv2.putText(
                        frame,
                        text_id,
                        (int(coordinates[0][0]+10), int(coordinates[0][1]) - 40),
                        font_text,
                        1,
                        color_text,
                        thickness_text,
                        cv2.LINE_AA,
                    )

                    ponto_top = (cord_top, int(coordinates[0][1]))
                    ponto_mid = (cord_bot,ponto_m)
                    ponto_bot = (cord_bot, int(coordinates[2][1]))

                    
                    dist_top = depth_map.get_value(ponto_top[0], ponto_top[1])[1]
                    dist_mid = depth_map.get_value(ponto_mid[0], ponto_mid[1])[1]
                    dist_bot = depth_map.get_value(ponto_bot[0], ponto_bot[1])[1]


                    cv2.circle(frame, ponto_top, 7,(50,255,0),-1)
                    cv2.circle(frame, ponto_bot, 7,(50,255,0),-1)


                    try:
                        h1 = (dist_top**2-dist_mid**2)**(1/2)
                        h2 = (dist_bot**2-dist_mid**2)**(1/2)
                        altura = (h1+h2)
                        num = str(altura)

                        if len(num) <= 20:
                            cv2.putText(frame,f'{altura:.1f}',(int(coordinates[0][0])+85,int(coordinates[0][1]-7)), font_text, 1, color_text, thickness_text)
                        else:
                            cv2.putText(frame,num[1:3] + " " + num[4:6],(int(coordinates[0][0])+85,int(coordinates[0][1]-7)), font_text, 1, color_text, thickness_text)
                    except:
                        cv2.putText(frame,' ',(int(coordinates[0][0])+85,int(coordinates[0][1]-7)), font_text, 1, color_text, thickness_text)

            cv2.imshow("Screen", frame)
            # -----------------------------------------------------------

            key = cv2.waitKey(1)
            if key == ord("q"):
                break

        # ========================================================================================================
        camera.disable_object_detection()
        camera.disable_positional_tracking()
        camera.close()
        # -----------------------------------------------------------
        return obj_id

if __name__ == "__main__":
    data = ZedDetector.electronic_detect()
    os.system("clear")
