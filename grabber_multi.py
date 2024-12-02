import multiprocessing as mp
import numpy as np
import cv2
import cam_library
import info
import time

# Глобальные переменные
camera_info = info.camera_info()


def set_exposure(cam):
    cam_library.CameraSetAeState(cam, 0)
    cam_library.CameraSetExposureTime(cam, (0.05 * 1000))
    cam_library.CameraSetAnalogGainX(cam, 25)
    cam_library.CameraSetSaturation(cam, 100)
    cam_library.CameraSetContrast(cam, 100)
    cam_library.CameraSetSharpness(cam, 50)


# Процесс получения кадров с камеры
def capture_frames(queue, running_event):
    """Функция для захвата кадров в отдельном процессе."""
    try:
        hCamera = cam_library.CameraInit(camera_info, -1, -1)
    except cam_library.CameraException as e:
        print("CameraInit Failed({}): {}".format(e.error_code, e.message))
        return

    cap = cam_library.CameraGetCapability(hCamera)
    cam_library.CameraSetIspOutFormat(hCamera, cam_library.CAMERA_MEDIA_TYPE_BGR8)
    cam_library.CameraSetTriggerMode(hCamera, 0)
    set_exposure(hCamera)
    cam_library.CameraPlay(hCamera)

    FrameBufferSize = cap.sResolutionRange.iWidthMax * cap.sResolutionRange.iHeightMax * 3
    pFrameBuffer = cam_library.CameraAlignMalloc(FrameBufferSize, 16)

    try:
        while running_event.is_set():
            try:
                pRawData, FrameHead = cam_library.CameraGetImageBuffer(hCamera, 200)
                cam_library.CameraImageProcess(hCamera, pRawData, pFrameBuffer, FrameHead)
                cam_library.CameraReleaseImageBuffer(hCamera, pRawData)
                cam_library.CameraFlipFrameBuffer(pFrameBuffer, FrameHead, 1)

                frame_data = (cam_library.c_ubyte * FrameHead.uBytes).from_address(pFrameBuffer)
                frame = np.frombuffer(frame_data, dtype=np.uint8).reshape(
                    (FrameHead.iHeight, FrameHead.iWidth, 3)
                )
                if not queue.full():
                    queue.put(frame)

            except cam_library.CameraException as e:
                if e.error_code != cam_library.CAMERA_STATUS_TIME_OUT:
                    print(f"CameraGetImageBuffer failed({e.error_code}): {e.message}")

            time.sleep(0.01)
    
    finally:
        cam_library.CameraUnInit(hCamera)
        cam_library.CameraAlignFree(pFrameBuffer)


# Процесс добавления кадров в массив
def process_frames(queue1, queue2, running_event):
    """
    Функция обработки кадров.
    Склеивает изображения по горизонтали и отображает их, обрезая до 20 последних кадров.
    """
    stitched_frame = None
    num_frames = 20

    while running_event.is_set():
        try:
            # Получение одного кадра из очереди
            if not queue1.empty():
                frame = queue1.get()
                frame = cv2.resize(frame, (frame.shape[1], frame.shape[0] * 2)) # Растяжение фрейма по высоте

                # Инициализация или добавление кадра в склеенное изображение
                if stitched_frame is None:
                    stitched_frame = frame
                else:
                    # Проверка совместимости размеров
                    if stitched_frame.shape[0] != frame.shape[0]:
                        frame = cv2.resize(frame, (frame.shape[1], stitched_frame.shape[0]))
                    
                    # # Вывод последних 20 кадров
                    # if stitched_frame.shape[0] == num_frames * 8:
                    #     stitched_frame = np.concatenate((stitched_frame, frame), axis=1)
                    #     stitched_frame = stitched_frame[8:]
                    # else:
                    #     stitched_frame = np.concatenate((stitched_frame, frame), axis=1)

                    stitched_frame = np.concatenate((stitched_frame, frame), axis=1)

                # Отображение текущего результата
                cv2.imshow('capture', stitched_frame)

            # Завершаем работу, если нажата клавиша пробела
            if (cv2.waitKey(1) & 0xFF) == ord(' '):
                queue2.put(stitched_frame)

        except Exception as e:
            print(f"Ошибка обработки кадра: {e}")
            break

    cv2.destroyAllWindows()


# Процесс отрисовки изображения
def process_image(queue, running_event):
    """
    Функция отрисовки кадров.
    """
    while running_event.is_set():
        try:
            final_frame = queue.get()
            cv2.imwrite('./result.png', final_frame)
            running_event.clear()

        except Exception as e:
            print(f"Ошибка отрисовки кадра: {e}")
            break   


if __name__ == "__main__":
    capture_queue = mp.Queue(maxsize=30)  # Очередь для передачи кадров
    process_queue = mp.Queue(maxsize=30)
    running_event = mp.Event()
    running_event.set()

    capture_process = mp.Process(target=capture_frames, args=(capture_queue, running_event))
    process_process = mp.Process(target=process_frames, args=(capture_queue, process_queue, running_event))
    img_process_process = mp.Process(target=process_image, args=(process_queue, running_event))

    capture_process.start()
    process_process.start()
    img_process_process.start()

    capture_process.join()
    process_process.join()
    img_process_process.join()