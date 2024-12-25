import numpy as np
import multiprocessing as mp
import cv2
import time
import keyboard as kb
import cam_library
import info


def set_exposure(cam):
    cam_library.CameraSetAeState(cam, 0)
    cam_library.CameraSetExposureTime(cam, (0.5 * 1000))
    cam_library.CameraSetAnalogGainX(cam, 150)
    # cam_library.CameraSetSaturation(cam, 120)
    # cam_library.CameraSetGain(cam, iRGain=2.5, iGGain=3.0, iBGain=1.8)
    # cam_library.CameraSetContrast(cam, 150)
    cam_library.CameraSetSharpness(cam, 50)


# Process 1 – frames grabbing and putting to queue
def frames_grabbing(queue, grab_stop_event):
    start_time = time.time()  # time flag
    k = 0
    k_empty = 0
    counter1, counter2, counter3 = 0, 0, 0  # counters per seconds (1st, 2nd, 3rd)

    # camera initializing
    try:
        camera_info = info.camera_info()
        hCamera = cam_library.CameraInit(camera_info, -1, -1)
    except cam_library.CameraException as e:
        print("CameraInit Failed({}): {}".format(e.error_code, e.message))
        return
    cap = cam_library.CameraGetCapability(hCamera)
    cam_library.CameraSetIspOutFormat(hCamera, cam_library.CAMERA_MEDIA_TYPE_BGR8)
    cam_library.CameraSetTriggerMode(hCamera, 0)  # continuous trigger mode
    set_exposure(hCamera)
    cam_library.CameraPlay(hCamera)

    # buffer initializing
    width_max, height_max = cap.sResolutionRange.iWidthMax, cap.sResolutionRange.iHeightMax
    FrameBufferSize = width_max * height_max * 3
    pFrameBuffer = cam_library.CameraAlignMalloc(FrameBufferSize, 8)

    # grabbing
    while not grab_stop_event.is_set():  # stop event checking
        try:
            pRawData, FrameHead = cam_library.CameraGetImageBuffer(hCamera, 200)
            cam_library.CameraImageProcess(
                hCamera, pRawData, pFrameBuffer, FrameHead)
            cam_library.CameraReleaseImageBuffer(hCamera, pRawData)
            cam_library.CameraFlipFrameBuffer(pFrameBuffer, FrameHead, 1)

            # pFrameBuffer to OpenCV img
            frame_data = (cam_library.c_ubyte *
                          FrameHead.uBytes).from_address(pFrameBuffer)
            frame = np.frombuffer(frame_data, dtype=np.uint8)
            frame = frame.reshape((FrameHead.iHeight, FrameHead.iWidth, 3))

            k += 1
            if frame is None or len(frame) == 0:
                k_empty += 1

            # frames counters in 3 first seconds
            if (time.time() - start_time) <= 1:
                counter1 += 1
            elif (time.time() - start_time) <= 2: 
                counter2 += 1
            elif (time.time() - start_time) <= 3: counter3 += 1

            # putting frame into queue
            queue.put(dict({k: frame}))

            if time.time() - start_time >= 3:  # stop condition
                grab_stop_event.set()
                print('Stop grabbing…')
                break

        except cam_library.CameraException as e:  # exceptions checking
            if e.error_code != cam_library.CAMERA_STATUS_TIME_OUT:
                grab_stop_event.set()
                print(f'CameraGetImageBuffer failed({e.error_code}): {e.message}')
                break
    
    queue.put(None)  # termination token
    print('Termination token is in queue.')
    print(f'Frames: 1s: {counter1}, 2s: {counter2}, 3s: {counter3}; in queue in Process 1: {k}')
    print(f'Empty or None frames: {k_empty}')
    
    # camera turning off & cache clearing
    cam_library.CameraUnInit(hCamera)
    cam_library.CameraAlignFree(pFrameBuffer)

    print('Grabbing operations done.')

# Process 2 – frames getting and stitching
def frames_stitching(queue, stitch_event):
    time.sleep(0.8)
    stitched_frame = None
    count = 1
    shapes_none_counter, shapes_counter = 0, 0
    frames_get_counter = 0

    while not stitch_event.is_set():
        try:
            while not queue.empty():
                frame = queue.get_nowait()
                frames_get_counter += 1


                if stitched_frame is None:
                    stitched_frame = frame[count]
                    count += 1
                    shapes_none_counter += 1
                else:
                    stitched_frame = np.concatenate((stitched_frame, frame[count]), axis=0)
                    count += 1
                    shapes_counter += 1
            
                # cv2.imshow('frame', stitched_frame[:, 3300:4892, :])

            if stitched_frame is None:
                print('Frame is none…')
                stitch_event.clear()
                break
            else:
                print(f'Frames uploaded in Process 2: {frames_get_counter}')
                print(f'Frame shape: {stitched_frame.shape}')
                cv2.imwrite('./result.jpg', stitched_frame[:, 3300:4892, :])
                cv2.destroyAllWindows()
                print('Stitching operations done.')
                print(queue.empty(), queue.qsize())
                stitch_event.clear()
                break
        
        except Exception as e:
            print(f'Image processing failed: {e}')
            stitch_event.clear()
            break


# control unit
def main():
    queue = mp.Queue()  # queue
    grab_stop_event = mp.Event()  # grabbing stop event
    stitch_event = mp.Event()  # stitching stop event

    grabbing = mp.Process(target=frames_grabbing, args=(queue, grab_stop_event))
    stitching = mp.Process(target=frames_stitching, args=(queue, stitch_event))
    grabbing.start()
    stitching.start()
    

    if kb.read_key(' '):
        grabbing.terminate()
        grabbing.join()

        stitching.terminate()
        stitching.join()
    
        print('Processes Terminated.')

if __name__ == '__main__':
    main()