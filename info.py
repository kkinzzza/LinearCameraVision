import cam_library as camera


def camera_info():
    DevList = camera.CameraEnumerateDevice()
    nDev = len(DevList)
    if nDev < 1:
        print("Camera not found!")
        return

    for i, DevInfo in enumerate(DevList):
        print("{}: {} {}".format(i, DevInfo.GetFriendlyName(), DevInfo.GetPortType()))
    i = 0 if nDev == 1 else int(input("Select camera: "))
    DevInfo = DevList[i]
    return DevInfo
