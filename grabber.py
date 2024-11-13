import cv2
import numpy as np
import cam_library
import info

camera_info = info.camera_info()
resizeWidth, resizeHeight = 640, 480  # for resizing if needed


def set_exposure(cam):
    cam_library.CameraSetAeState(cam, 0)
    cam_library.CameraSetExposureTime(cam, (12 * 1000))
    cam_library.CameraSetAnalogGainX(cam, 8)
    cam_library.CameraSetSaturation(cam, 120)
    cam_library.CameraSetGain(cam, iRGain=2.5, iGGain=3.0, iBGain=1.8)
    cam_library.CameraSetContrast(cam, 150)
    cam_library.CameraSetSharpness(cam, 50)


def grab():
    # turning camera on
    try:
        hCamera = cam_library.CameraInit(camera_info, -1, -1)
    except cam_library.CameraException as e:
        print("CameraInit Failed({}): {}".format(e.error_code, e.message))
        return

    # getting camera characteristics
    cap = cam_library.CameraGetCapability(hCamera)
    cam_library.CameraSetIspOutFormat(hCamera, cam_library.CAMERA_MEDIA_TYPE_BGR8)

    # tracking mode on
    cam_library.CameraSetTriggerMode(hCamera, 0)

    # setting exposure
    set_exposure(cam=hCamera)

    # camera working on
    cam_library.CameraPlay(hCamera)

    # RGB buffer
    FrameBufferSize = cap.sResolutionRange.iWidthMax * cap.sResolutionRange.iHeightMax * 3
    pFrameBuffer = cam_library.CameraAlignMalloc(FrameBufferSize, 16)

    frame_res = np.reshape([0 for i in range(4 * 8192 * 3)], (4, 8192, 3)).astype(np.uint8)
    while (cv2.waitKey(1) & 0xFF) != ord(' '):
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

            # frame = cv2.resize(frame, (resizeWidth, resizeHeight), interpolation=cv2.INTER_LINEAR)
            frame_res = np.concatenate((frame_res, frame)).astype(np.uint8)
            # cv2.imshow('capture', frame_sliced)
            cv2.imshow('capture', np.array([1]).astype(np.uint8))
        except cam_library.CameraException as e:
            if e.error_code != cam_library.CAMERA_STATUS_TIME_OUT:
                print("CameraGetImageBuffer failed({}): {}".format(
                    e.error_code, e.message))

    cv2.imwrite('./result.png', frame_res)
    print(frame_res.shape)
    # camera turning off & cache clearing
    cam_library.CameraUnInit(hCamera)
    cam_library.CameraAlignFree(pFrameBuffer)


def main():
    try:
        grab()
    finally:
        cv2.destroyAllWindows()


main()
