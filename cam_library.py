import platform
from ctypes import *
from threading import local
from type_definition import *

CALLBACK_FUNC_TYPE = None
_sdk = None


def _Init():
    global _sdk
    global CALLBACK_FUNC_TYPE

    is_win = (platform.system() == "Windows")
    is_x86 = (platform.architecture()[0] == '32bit')

    if is_win:
        _sdk = windll.MVCAMSDK if is_x86 else windll.MVCAMSDK_X64
        CALLBACK_FUNC_TYPE = WINFUNCTYPE
    else:
        _sdk = cdll.LoadLibrary("libMVSDK.so")
        CALLBACK_FUNC_TYPE = CFUNCTYPE


_Init()


class CameraException(Exception):
    def __init__(self, error_code):
        super(CameraException, self).__init__()
        self.error_code = error_code
        self.message = CameraGetErrorString(error_code)

    def __str__(self):
        return 'error_code:{} message:{}'.format(self.error_code, self.message)


class MvStructure(Structure):
    def __str__(self):
        strs = []
        for field in self._fields_:
            name = field[0]
            value = getattr(self, name)
            if isinstance(value, type(b'')):
                value = _string_buffer_to_str(value)
            strs.append("{}:{}".format(name, value))
        return '\n'.join(strs)

    def __repr__(self):
        return self.__str__()

    def clone(self):
        obj = type(self)()
        memmove(byref(obj), byref(self), sizeof(self))
        return obj


class tSdkCameraDevInfo(MvStructure):
    _fields_ = [("acProductSeries", c_char * 32),  # Product series
                ("acProductName", c_char * 32),  # Product name
                ("acFriendlyName", c_char * 32),  # Product nickname
                ("acLinkName", c_char * 32),  # Kernel symbolic connection name, used internally
                ("acDriverVersion", c_char * 32),  # Driver version
                ("acSensorType", c_char * 32),  # sensor type
                ("acPortType", c_char * 32),  # Interface type
                ("acSn", c_char * 32),  # Product unique serial number
                ("uInstance", c_uint)]  # Instance index number of the camera

    def GetProductSeries(self):
        return _string_buffer_to_str(self.acProductSeries)

    def GetProductName(self):
        return _string_buffer_to_str(self.acProductName)

    def GetFriendlyName(self):
        return _string_buffer_to_str(self.acFriendlyName)

    def GetLinkName(self):
        return _string_buffer_to_str(self.acLinkName)

    def GetDriverVersion(self):
        return _string_buffer_to_str(self.acDriverVersion)

    def GetSensorType(self):
        return _string_buffer_to_str(self.acSensorType)

    def GetPortType(self):
        return _string_buffer_to_str(self.acPortType)

    def GetSn(self):
        return _string_buffer_to_str(self.acSn)


class tSdkResolutionRange(MvStructure):
    _fields_ = [("iHeightMax", c_int),  # Maximum image height
                ("iHeightMin", c_int),  # Minimum image height
                ("iWidthMax", c_int),  # Maximum image width
                ("iWidthMin", c_int),  # Minimum image width
                ("uSkipModeMask", c_uint),
                ("uBinSumModeMask", c_uint),
                ("uBinAverageModeMask", c_uint),
                ("uResampleMask", c_uint)]  # Mask for hardware resampling


class tSdkImageResolution(MvStructure):
    _fields_ = [
        ("iIndex", c_int),
        ("acDescription", c_char * 32),
        ("uBinSumMode", c_uint),
        ("uBinAverageMode", c_uint),
        ("uSkipMode", c_uint),
        ("uResampleMask", c_uint),
        ("iHOffsetFOV", c_int),
        ("iVOffsetFOV", c_int),
        ("iWidthFOV", c_int),
        ("iHeightFOV", c_int),
        ("iWidth", c_int),
        ("iHeight", c_int),
        ("iWidthZoomHd", c_int),
        ("iHeightZoomHd", c_int),
        ("iWidthZoomSw", c_int),
        ("iHeightZoomSw", c_int),
    ]

    def GetDescription(self):
        return _string_buffer_to_str(self.acDescription)


class tSdkColorTemperatureDes(MvStructure):
    _fields_ = [
        ("iIndex", c_int),  # Pattern index number
        ("acDescription", c_char * 32),  # Description information
    ]

    def GetDescription(self):
        return _string_buffer_to_str(self.acDescription)


class tSdkFrameSpeed(MvStructure):
    _fields_ = [
        ("iIndex", c_int),  # Frame rate index number
        ("acDescription", c_char * 32),  # Description information
    ]

    def GetDescription(self):
        return _string_buffer_to_str(self.acDescription)


class tSdkExpose(MvStructure):
    _fields_ = [
        ("uiTargetMin", c_uint),
        ("uiTargetMax", c_uint),
        ("uiAnalogGainMin", c_uint),
        ("uiAnalogGainMax", c_uint),
        ("fAnalogGainStep", c_float),
        ("uiExposeTimeMin", c_uint),
        ("uiExposeTimeMax", c_uint),
    ]


class tSdkTrigger(MvStructure):
    _fields_ = [
        ("iIndex", c_int),  # Pattern index number
        ("acDescription", c_char * 32),  # Description information
    ]

    def GetDescription(self):
        return _string_buffer_to_str(self.acDescription)


class tSdkPackLength(MvStructure):
    _fields_ = [
        ("iIndex", c_int),  # Frame rate index number
        ("acDescription", c_char * 32),  # Description information
        ("iPackSize", c_uint),
    ]

    def GetDescription(self):
        return _string_buffer_to_str(self.acDescription)


class tSdkPresetLut(MvStructure):
    _fields_ = [
        ("iIndex", c_int),  # Number
        ("acDescription", c_char * 32),  # Description information
    ]

    def GetDescription(self):
        return _string_buffer_to_str(self.acDescription)


class tSdkAeAlgorithm(MvStructure):
    _fields_ = [
        ("iIndex", c_int),  # Number
        ("acDescription", c_char * 32),  # Description information
    ]

    def GetDescription(self):
        return _string_buffer_to_str(self.acDescription)


class tSdkBayerDecodeAlgorithm(MvStructure):
    _fields_ = [
        ("iIndex", c_int),  # Number
        ("acDescription", c_char * 32),  # Description information
    ]

    def GetDescription(self):
        return _string_buffer_to_str(self.acDescription)


class tSdkFrameStatistic(MvStructure):
    _fields_ = [
        ("iTotal", c_int),  # Total number of frames currently collected (including error frames)
        ("iCapture", c_int),  # Number of valid frames currently collected
        ("iLost", c_int),  # Current number of frames lost
    ]


class tSdkMediaType(MvStructure):
    _fields_ = [
        ("iIndex", c_int),  # Format type number
        ("acDescription", c_char * 32),  # Description information
        ("iMediaType", c_uint),  # Сorresponding image format encoding
    ]

    def GetDescription(self):
        return _string_buffer_to_str(self.acDescription)


class tGammaRange(MvStructure):
    _fields_ = [
        ("iMin", c_int),
        ("iMax", c_int),
    ]


class tContrastRange(MvStructure):
    _fields_ = [
        ("iMin", c_int),
        ("iMax", c_int),
    ]


class tRgbGainRange(MvStructure):
    _fields_ = [
        ("iRGainMin", c_int),
        ("iRGainMax", c_int),
        ("iGGainMin", c_int),
        ("iGGainMax", c_int),
        ("iBGainMin", c_int),
        ("iBGainMax", c_int),
    ]


class tSaturationRange(MvStructure):
    _fields_ = [
        ("iMin", c_int),
        ("iMax", c_int),
    ]


class tSharpnessRange(MvStructure):
    _fields_ = [
        ("iMin", c_int),
        ("iMax", c_int),
    ]


class tSdkIspCapacity(MvStructure):
    _fields_ = [
        ("bMonoSensor", c_int),
        ("bWbOnce", c_int),
        ("bAutoWb", c_int),
        ("bAutoExposure", c_int),
        ("bManualExposure", c_int),
        ("bAntiFlick", c_int),
        ("bDeviceIsp", c_int),
        ("bForceUseDeviceIsp", c_int),
        ("bZoomHD", c_int),
    ]


class tSdkCameraCapbility(MvStructure):
    _fields_ = [
        ("pTriggerDesc", POINTER(tSdkTrigger)),
        ("iTriggerDesc", c_int),
        ("pImageSizeDesc", POINTER(tSdkImageResolution)),
        ("iImageSizeDesc", c_int),
        ("pClrTempDesc", POINTER(tSdkColorTemperatureDes)),
        ("iClrTempDesc", c_int),
        ("pMediaTypeDesc", POINTER(tSdkMediaType)),
        ("iMediaTypeDesc", c_int),
        ("pFrameSpeedDesc", POINTER(tSdkFrameSpeed)),
        ("iFrameSpeedDesc", c_int),
        ("pPackLenDesc", POINTER(tSdkPackLength)),
        ("iPackLenDesc", c_int),
        ("iOutputIoCounts", c_int),
        ("iInputIoCounts", c_int),
        ("pPresetLutDesc", POINTER(tSdkPresetLut)),
        ("iPresetLut", c_int),
        ("iUserDataMaxLen", c_int),
        ("bParamInDevice", c_int),
        ("pAeAlmSwDesc", POINTER(tSdkAeAlgorithm)),
        ("iAeAlmSwDesc", c_int),
        ("pAeAlmHdDesc", POINTER(tSdkAeAlgorithm)),
        ("iAeAlmHdDesc", c_int),
        ("pBayerDecAlmSwDesc", POINTER(tSdkBayerDecodeAlgorithm)),
        ("iBayerDecAlmSwDesc", c_int),
        ("pBayerDecAlmHdDesc", POINTER(tSdkBayerDecodeAlgorithm)),
        ("iBayerDecAlmHdDesc", c_int),
        ("sExposeDesc", tSdkExpose),
        ("sResolutionRange", tSdkResolutionRange),
        ("sRgbGainRange", tRgbGainRange),
        ("sSaturationRange", tSaturationRange),
        ("sGammaRange", tGammaRange),
        ("sContrastRange", tContrastRange),
        ("sSharpnessRange", tSharpnessRange),
        ("sIspCapacity", tSdkIspCapacity),
    ]


class tSdkFrameHead(MvStructure):
    _fields_ = [
        ("uiMediaType", c_uint),
        ("uBytes", c_uint),
        ("iWidth", c_int),
        ("iHeight", c_int),
        ("iWidthZoomSw", c_int),
        ("iHeightZoomSw", c_int),
        ("bIsTrigger", c_int),
        ("uiTimeStamp", c_uint),
        ("uiExpTime", c_uint),
        ("fAnalogGain", c_float),
        ("iGamma", c_int),
        ("iContrast", c_int),
        ("iSaturation", c_int),
        ("fRgain", c_float),
        ("fGgain", c_float),
        ("fBgain", c_float),
    ]


class tSdkGrabberStat(MvStructure):
    _fields_ = [
        ("Width", c_int),
        ("Height", c_int),
        ("Disp", c_int),
        ("Capture", c_int),
        ("Lost", c_int),
        ("Error", c_int),
        ("DispFps", c_float),
        ("CapFps", c_float),
    ]


class method(object):
    def __init__(self, FuncType):
        super(method, self).__init__()
        self.FuncType = FuncType
        self.cache = {}

    def __call__(self, cb):
        self.cb = cb
        return self

    def __get__(self, obj, objtype):
        try:
            return self.cache[obj]
        except KeyError as e:
            def cl(*args):
                return self.cb(obj, *args)

            r = self.cache[obj] = self.FuncType(cl)
            return r


CAMERA_SNAP_PROC = CALLBACK_FUNC_TYPE(None, c_int, c_void_p, POINTER(tSdkFrameHead), c_void_p)
CAMERA_CONNECTION_STATUS_CALLBACK = CALLBACK_FUNC_TYPE(None, c_int, c_uint, c_uint, c_void_p)

pfnCameraGrabberSaveImageComplete = CALLBACK_FUNC_TYPE(None, c_void_p, c_void_p, c_int, c_void_p)
pfnCameraGrabberFrameListener = CALLBACK_FUNC_TYPE(c_int, c_void_p, c_int, c_void_p, POINTER(tSdkFrameHead), c_void_p)
pfnCameraGrabberFrameCallback = CALLBACK_FUNC_TYPE(None, c_void_p, c_void_p, POINTER(tSdkFrameHead), c_void_p)


_tls = local()


def GetLastError():
    try:
        return _tls.last_error
    except AttributeError as e:
        _tls.last_error = 0
        return 0


def SetLastError(err_code):
    _tls.last_error = err_code


def _string_buffer_to_str(buf):
    s = buf if isinstance(buf, type(b'')) else buf.value

    for codec in ('gbk', 'utf-8'):
        try:
            s = s.decode(codec)
            break
        except UnicodeDecodeError as e:
            continue

    if isinstance(s, str):
        return s
    else:
        return s.encode('utf-8')


def _str_to_string_buffer(str):
    if type(str) is type(u''):
        s = str.encode('gbk')
    else:
        s = str.decode('utf-8').encode('gbk')
    return create_string_buffer(s)


def CameraSdkInit(iLanguageSel):
    err_code = _sdk.CameraSdkInit(iLanguageSel)
    SetLastError(err_code)
    return err_code


def CameraSetSysOption(optionName, value):
    err_code = _sdk.CameraSetSysOption(_str_to_string_buffer(
        optionName), _str_to_string_buffer(str(value)))
    SetLastError(err_code)
    return err_code


def CameraEnumerateDevice(MaxCount=32):
    Nums = c_int(MaxCount)
    pCameraList = (tSdkCameraDevInfo * Nums.value)()
    err_code = _sdk.CameraEnumerateDevice(pCameraList, byref(Nums))
    SetLastError(err_code)
    return pCameraList[0:Nums.value]


def CameraEnumerateDeviceEx():
    return _sdk.CameraEnumerateDeviceEx()


def CameraIsOpened(pCameraInfo):
    pOpened = c_int()
    err_code = _sdk.CameraIsOpened(byref(pCameraInfo), byref(pOpened))
    SetLastError(err_code)
    return pOpened.value != 0


def CameraInit(pCameraInfo, emParamLoadMode=-1, emTeam=-1):
    pCameraHandle = c_int()
    err_code = _sdk.CameraInit(
        byref(pCameraInfo), emParamLoadMode, emTeam, byref(pCameraHandle))
    SetLastError(err_code)
    if err_code != 0:
        raise CameraException(err_code)
    return pCameraHandle.value


def CameraInitEx(iDeviceIndex, emParamLoadMode=-1, emTeam=-1):
    pCameraHandle = c_int()
    err_code = _sdk.CameraInitEx(
        iDeviceIndex, emParamLoadMode, emTeam, byref(pCameraHandle))
    SetLastError(err_code)
    if err_code != 0:
        raise CameraException(err_code)
    return pCameraHandle.value


def CameraInitEx2(CameraName):
    pCameraHandle = c_int()
    err_code = _sdk.CameraInitEx2(
        _str_to_string_buffer(CameraName), byref(pCameraHandle))
    SetLastError(err_code)
    if err_code != 0:
        raise CameraException(err_code)
    return pCameraHandle.value


def CameraSetCallbackFunction(hCamera, pCallBack, pContext=0):
    err_code = _sdk.CameraSetCallbackFunction(
        hCamera, pCallBack, c_void_p(pContext), None)
    SetLastError(err_code)
    return err_code


def CameraUnInit(hCamera):
    err_code = _sdk.CameraUnInit(hCamera)
    SetLastError(err_code)
    return err_code


def CameraGetInformation(hCamera):
    pbuffer = c_char_p()
    err_code = _sdk.CameraGetInformation(hCamera, byref(pbuffer))
    SetLastError(err_code)
    if err_code == 0 and pbuffer.value is not None:
        return _string_buffer_to_str(pbuffer)
    return ''


def CameraImageProcess(hCamera, pbyIn, pbyOut, pFrInfo):
    err_code = _sdk.CameraImageProcess(
        hCamera, c_void_p(pbyIn), c_void_p(pbyOut), byref(pFrInfo))
    SetLastError(err_code)
    return err_code


def CameraImageProcessEx(hCamera, pbyIn, pbyOut, pFrInfo, uOutFormat, uReserved):
    err_code = _sdk.CameraImageProcessEx(hCamera, c_void_p(pbyIn), c_void_p(pbyOut), byref(pFrInfo), uOutFormat,
                                         uReserved)
    SetLastError(err_code)
    return err_code


def CameraDisplayInit(hCamera, hWndDisplay):
    err_code = _sdk.CameraDisplayInit(hCamera, hWndDisplay)
    SetLastError(err_code)
    return err_code


def CameraDisplayRGB24(hCamera, pFrameBuffer, pFrInfo):
    err_code = _sdk.CameraDisplayRGB24(
        hCamera, c_void_p(pFrameBuffer), byref(pFrInfo))
    SetLastError(err_code)
    return err_code


def CameraSetDisplayMode(hCamera, iMode):
    err_code = _sdk.CameraSetDisplayMode(hCamera, iMode)
    SetLastError(err_code)
    return err_code


def CameraSetDisplayOffset(hCamera, iOffsetX, iOffsetY):
    err_code = _sdk.CameraSetDisplayOffset(hCamera, iOffsetX, iOffsetY)
    SetLastError(err_code)
    return err_code


def CameraSetDisplaySize(hCamera, iWidth, iHeight):
    err_code = _sdk.CameraSetDisplaySize(hCamera, iWidth, iHeight)
    SetLastError(err_code)
    return err_code


def CameraGetImageBuffer(hCamera, wTimes):
    pbyBuffer = c_void_p()
    pFrameInfo = tSdkFrameHead()
    err_code = _sdk.CameraGetImageBuffer(
        hCamera, byref(pFrameInfo), byref(pbyBuffer), wTimes)
    SetLastError(err_code)
    if err_code != 0:
        raise CameraException(err_code)
    return (pbyBuffer.value, pFrameInfo)


def CameraGetImageBufferEx(hCamera, wTimes):
    _sdk.CameraGetImageBufferEx.restype = c_void_p
    piWidth = c_int()
    piHeight = c_int()
    pFrameBuffer = _sdk.CameraGetImageBufferEx(
        hCamera, byref(piWidth), byref(piHeight), wTimes)
    err_code = CAMERA_STATUS_SUCCESS if pFrameBuffer else CAMERA_STATUS_TIME_OUT
    SetLastError(err_code)
    if pFrameBuffer:
        return (pFrameBuffer, piWidth.value, piHeight.value)
    else:
        raise CameraException(err_code)


def CameraSnapToBuffer(hCamera, wTimes):
    pbyBuffer = c_void_p()
    pFrameInfo = tSdkFrameHead()
    err_code = _sdk.CameraSnapToBuffer(
        hCamera, byref(pFrameInfo), byref(pbyBuffer), wTimes)
    SetLastError(err_code)
    if err_code != 0:
        raise CameraException(err_code)
    return (pbyBuffer.value, pFrameInfo)


def CameraReleaseImageBuffer(hCamera, pbyBuffer):
    err_code = _sdk.CameraReleaseImageBuffer(hCamera, c_void_p(pbyBuffer))
    SetLastError(err_code)
    return err_code


def CameraPlay(hCamera):
    err_code = _sdk.CameraPlay(hCamera)
    SetLastError(err_code)
    return err_code


def CameraPause(hCamera):
    err_code = _sdk.CameraPause(hCamera)
    SetLastError(err_code)
    return err_code


def CameraStop(hCamera):
    err_code = _sdk.CameraStop(hCamera)
    SetLastError(err_code)
    return err_code


def CameraInitRecord(hCamera, iFormat, pcSavePath, b2GLimit, dwQuality, iFrameRate):
    err_code = _sdk.CameraInitRecord(hCamera, iFormat, _str_to_string_buffer(pcSavePath), b2GLimit, dwQuality,
                                     iFrameRate)
    SetLastError(err_code)
    return err_code


def CameraStopRecord(hCamera):
    err_code = _sdk.CameraStopRecord(hCamera)
    SetLastError(err_code)
    return err_code


def CameraPushFrame(hCamera, pbyImageBuffer, pFrInfo):
    err_code = _sdk.CameraPushFrame(
        hCamera, c_void_p(pbyImageBuffer), byref(pFrInfo))
    SetLastError(err_code)
    return err_code


def CameraSaveImage(hCamera, lpszFileName, pbyImageBuffer, pFrInfo, byFileType, byQuality):
    err_code = _sdk.CameraSaveImage(hCamera, _str_to_string_buffer(lpszFileName), c_void_p(pbyImageBuffer),
                                    byref(pFrInfo), byFileType, byQuality)
    SetLastError(err_code)
    return err_code


def CameraSaveImageEx(hCamera, lpszFileName, pbyImageBuffer, uImageFormat, iWidth, iHeight, byFileType, byQuality):
    err_code = _sdk.CameraSaveImageEx(hCamera, _str_to_string_buffer(lpszFileName), c_void_p(pbyImageBuffer),
                                      uImageFormat, iWidth, iHeight, byFileType, byQuality)
    SetLastError(err_code)
    return err_code


def CameraGetImageResolution(hCamera):
    psCurVideoSize = tSdkImageResolution()
    err_code = _sdk.CameraGetImageResolution(hCamera, byref(psCurVideoSize))
    SetLastError(err_code)
    return psCurVideoSize


def CameraSetImageResolution(hCamera, pImageResolution):
    err_code = _sdk.CameraSetImageResolution(hCamera, byref(pImageResolution))
    SetLastError(err_code)
    return err_code


def CameraSetImageResolutionEx(hCamera, iIndex, Mode, ModeSize, x, y, width, height, ZoomWidth, ZoomHeight):
    err_code = _sdk.CameraSetImageResolutionEx(hCamera, iIndex, Mode, ModeSize, x, y, width, height, ZoomWidth,
                                               ZoomHeight)
    SetLastError(err_code)
    return err_code


def CameraGetMediaType(hCamera):
    piMediaType = c_int()
    err_code = _sdk.CameraGetMediaType(hCamera, byref(piMediaType))
    SetLastError(err_code)
    return piMediaType.value


def CameraSetMediaType(hCamera, iMediaType):
    err_code = _sdk.CameraSetMediaType(hCamera, iMediaType)
    SetLastError(err_code)
    return err_code


def CameraSetAeState(hCamera, bAeState):
    err_code = _sdk.CameraSetAeState(hCamera, bAeState)
    SetLastError(err_code)
    return err_code


def CameraGetAeState(hCamera):
    pAeState = c_int()
    err_code = _sdk.CameraGetAeState(hCamera, byref(pAeState))
    SetLastError(err_code)
    return pAeState.value


def CameraSetSharpness(hCamera, iSharpness):
    err_code = _sdk.CameraSetSharpness(hCamera, iSharpness)
    SetLastError(err_code)
    return err_code


def CameraGetSharpness(hCamera):
    piSharpness = c_int()
    err_code = _sdk.CameraGetSharpness(hCamera, byref(piSharpness))
    SetLastError(err_code)
    return piSharpness.value


def CameraSetLutMode(hCamera, emLutMode):
    err_code = _sdk.CameraSetLutMode(hCamera, emLutMode)
    SetLastError(err_code)
    return err_code


def CameraGetLutMode(hCamera):
    pemLutMode = c_int()
    err_code = _sdk.CameraGetLutMode(hCamera, byref(pemLutMode))
    SetLastError(err_code)
    return pemLutMode.value


def CameraSelectLutPreset(hCamera, iSel):
    err_code = _sdk.CameraSelectLutPreset(hCamera, iSel)
    SetLastError(err_code)
    return err_code


def CameraGetLutPresetSel(hCamera):
    piSel = c_int()
    err_code = _sdk.CameraGetLutPresetSel(hCamera, byref(piSel))
    SetLastError(err_code)
    return piSel.value


def CameraSetCustomLut(hCamera, iChannel, pLut):
    pLutNative = (c_ushort * 4096)(*pLut)
    err_code = _sdk.CameraSetCustomLut(hCamera, iChannel, pLutNative)
    SetLastError(err_code)
    return err_code


def CameraGetCustomLut(hCamera, iChannel):
    pLutNative = (c_ushort * 4096)()
    err_code = _sdk.CameraGetCustomLut(hCamera, iChannel, pLutNative)
    SetLastError(err_code)
    return pLutNative[:]


def CameraGetCurrentLut(hCamera, iChannel):
    pLutNative = (c_ushort * 4096)()
    err_code = _sdk.CameraGetCurrentLut(hCamera, iChannel, pLutNative)
    SetLastError(err_code)
    return pLutNative[:]


def CameraSetWbMode(hCamera, bAuto):
    err_code = _sdk.CameraSetWbMode(hCamera, bAuto)
    SetLastError(err_code)
    return err_code


def CameraGetWbMode(hCamera):
    pbAuto = c_int()
    err_code = _sdk.CameraGetWbMode(hCamera, byref(pbAuto))
    SetLastError(err_code)
    return pbAuto.value


def CameraSetPresetClrTemp(hCamera, iSel):
    err_code = _sdk.CameraSetPresetClrTemp(hCamera, iSel)
    SetLastError(err_code)
    return err_code


def CameraGetPresetClrTemp(hCamera):
    piSel = c_int()
    err_code = _sdk.CameraGetPresetClrTemp(hCamera, byref(piSel))
    SetLastError(err_code)
    return piSel.value


def CameraSetUserClrTempGain(hCamera, iRgain, iGgain, iBgain):
    err_code = _sdk.CameraSetUserClrTempGain(hCamera, iRgain, iGgain, iBgain)
    SetLastError(err_code)
    return err_code


def CameraGetUserClrTempGain(hCamera):
    piRgain = c_int()
    piGgain = c_int()
    piBgain = c_int()
    err_code = _sdk.CameraGetUserClrTempGain(
        hCamera, byref(piRgain), byref(piGgain), byref(piBgain))
    SetLastError(err_code)
    return (piRgain.value, piGgain.value, piBgain.value)


def CameraSetUserClrTempMatrix(hCamera, pMatrix):
    pMatrixNative = (c_float * 9)(*pMatrix)
    err_code = _sdk.CameraSetUserClrTempMatrix(hCamera, pMatrixNative)
    SetLastError(err_code)
    return err_code


def CameraGetUserClrTempMatrix(hCamera):
    pMatrixNative = (c_float * 9)()
    err_code = _sdk.CameraGetUserClrTempMatrix(hCamera, pMatrixNative)
    SetLastError(err_code)
    return pMatrixNative[:]


def CameraSetClrTempMode(hCamera, iMode):
    err_code = _sdk.CameraSetClrTempMode(hCamera, iMode)
    SetLastError(err_code)
    return err_code


def CameraGetClrTempMode(hCamera):
    piMode = c_int()
    err_code = _sdk.CameraGetClrTempMode(hCamera, byref(piMode))
    SetLastError(err_code)
    return piMode.value


def CameraSetOnceWB(hCamera):
    err_code = _sdk.CameraSetOnceWB(hCamera)
    SetLastError(err_code)
    return err_code


def CameraSetOnceBB(hCamera):
    err_code = _sdk.CameraSetOnceBB(hCamera)
    SetLastError(err_code)
    return err_code


def CameraSetAeTarget(hCamera, iAeTarget):
    err_code = _sdk.CameraSetAeTarget(hCamera, iAeTarget)
    SetLastError(err_code)
    return err_code


def CameraGetAeTarget(hCamera):
    piAeTarget = c_int()
    err_code = _sdk.CameraGetAeTarget(hCamera, byref(piAeTarget))
    SetLastError(err_code)
    return piAeTarget.value


def CameraSetAeExposureRange(hCamera, fMinExposureTime, fMaxExposureTime):
    err_code = _sdk.CameraSetAeExposureRange(
        hCamera, c_double(fMinExposureTime), c_double(fMaxExposureTime))
    SetLastError(err_code)
    return err_code


def CameraGetAeExposureRange(hCamera):
    fMinExposureTime = c_double()
    fMaxExposureTime = c_double()
    err_code = _sdk.CameraGetAeExposureRange(
        hCamera, byref(fMinExposureTime), byref(fMaxExposureTime))
    SetLastError(err_code)
    return (fMinExposureTime.value, fMaxExposureTime.value)


def CameraSetAeAnalogGainRange(hCamera, iMinAnalogGain, iMaxAnalogGain):
    err_code = _sdk.CameraSetAeAnalogGainRange(
        hCamera, iMinAnalogGain, iMaxAnalogGain)
    SetLastError(err_code)
    return err_code


def CameraGetAeAnalogGainRange(hCamera):
    iMinAnalogGain = c_int()
    iMaxAnalogGain = c_int()
    err_code = _sdk.CameraGetAeAnalogGainRange(
        hCamera, byref(iMinAnalogGain), byref(iMaxAnalogGain))
    SetLastError(err_code)
    return (iMinAnalogGain.value, iMaxAnalogGain.value)


def CameraSetAeThreshold(hCamera, iThreshold):
    err_code = _sdk.CameraSetAeThreshold(hCamera, iThreshold)
    SetLastError(err_code)
    return err_code


def CameraGetAeThreshold(hCamera):
    iThreshold = c_int()
    err_code = _sdk.CameraGetAeThreshold(hCamera, byref(iThreshold))
    SetLastError(err_code)
    return iThreshold.value


def CameraSetExposureTime(hCamera, fExposureTime):
    err_code = _sdk.CameraSetExposureTime(hCamera, c_double(fExposureTime))
    SetLastError(err_code)
    return err_code


def CameraGetExposureLineTime(hCamera):
    pfLineTime = c_double()
    err_code = _sdk.CameraGetExposureLineTime(hCamera, byref(pfLineTime))
    SetLastError(err_code)
    return pfLineTime.value


def CameraGetExposureTime(hCamera):
    pfExposureTime = c_double()
    err_code = _sdk.CameraGetExposureTime(hCamera, byref(pfExposureTime))
    SetLastError(err_code)
    return pfExposureTime.value


def CameraGetExposureTimeRange(hCamera):
    pfMin = c_double()
    pfMax = c_double()
    pfStep = c_double()
    err_code = _sdk.CameraGetExposureTimeRange(
        hCamera, byref(pfMin), byref(pfMax), byref(pfStep))
    SetLastError(err_code)
    return (pfMin.value, pfMax.value, pfStep.value)


def CameraSetAnalogGain(hCamera, iAnalogGain):
    err_code = _sdk.CameraSetAnalogGain(hCamera, iAnalogGain)
    SetLastError(err_code)
    return err_code


def CameraGetAnalogGain(hCamera):
    piAnalogGain = c_int()
    err_code = _sdk.CameraGetAnalogGain(hCamera, byref(piAnalogGain))
    SetLastError(err_code)
    return piAnalogGain.value


def CameraSetAnalogGainX(hCamera, fGain):
    err_code = _sdk.CameraSetAnalogGainX(hCamera, c_float(fGain))
    SetLastError(err_code)
    return err_code


def CameraGetAnalogGainX(hCamera):
    fGain = c_float()
    err_code = _sdk.CameraGetAnalogGainX(hCamera, byref(fGain))
    SetLastError(err_code)
    return fGain.value


def CameraGetAnalogGainXRange(hCamera):
    pfMin = c_float()
    pfMax = c_float()
    pfStep = c_float()
    err_code = _sdk.CameraGetAnalogGainXRange(
        hCamera, byref(pfMin), byref(pfMax), byref(pfStep))
    SetLastError(err_code)
    return (pfMin.value, pfMax.value, pfStep.value)


def CameraSetGain(hCamera, iRGain, iGGain, iBGain):
    err_code = _sdk.CameraSetGain(hCamera, c_float(
        iRGain), c_float(iGGain), c_float(iBGain))
    SetLastError(err_code)
    return err_code


def CameraGetGain(hCamera):
    piRGain = c_int()
    piGGain = c_int()
    piBGain = c_int()
    err_code = _sdk.CameraGetGain(hCamera, byref(
        piRGain), byref(piGGain), byref(piBGain))
    SetLastError(err_code)
    return (piRGain.value, piGGain.value, piBGain.value)


def CameraSetGamma(hCamera, iGamma):
    err_code = _sdk.CameraSetGamma(hCamera, iGamma)
    SetLastError(err_code)
    return err_code


def CameraGetGamma(hCamera):
    piGamma = c_int()
    err_code = _sdk.CameraGetGamma(hCamera, byref(piGamma))
    SetLastError(err_code)
    return piGamma.value


def CameraSetContrast(hCamera, iContrast):
    err_code = _sdk.CameraSetContrast(hCamera, iContrast)
    SetLastError(err_code)
    return err_code


def CameraGetContrast(hCamera):
    piContrast = c_int()
    err_code = _sdk.CameraGetContrast(hCamera, byref(piContrast))
    SetLastError(err_code)
    return piContrast.value


def CameraSetSaturation(hCamera, iSaturation):
    err_code = _sdk.CameraSetSaturation(hCamera, iSaturation)
    SetLastError(err_code)
    return err_code


def CameraGetSaturation(hCamera):
    piSaturation = c_int()
    err_code = _sdk.CameraGetSaturation(hCamera, byref(piSaturation))
    SetLastError(err_code)
    return piSaturation.value


def CameraSetMonochrome(hCamera, bEnable):
    err_code = _sdk.CameraSetMonochrome(hCamera, bEnable)
    SetLastError(err_code)
    return err_code


def CameraGetMonochrome(hCamera):
    pbEnable = c_int()
    err_code = _sdk.CameraGetMonochrome(hCamera, byref(pbEnable))
    SetLastError(err_code)
    return pbEnable.value


def CameraSetInverse(hCamera, bEnable):
    err_code = _sdk.CameraSetInverse(hCamera, bEnable)
    SetLastError(err_code)
    return err_code


def CameraGetInverse(hCamera):
    pbEnable = c_int()
    err_code = _sdk.CameraGetInverse(hCamera, byref(pbEnable))
    SetLastError(err_code)
    return pbEnable.value


def CameraSetAntiFlick(hCamera, bEnable):
    err_code = _sdk.CameraSetAntiFlick(hCamera, bEnable)
    SetLastError(err_code)
    return err_code


def CameraGetAntiFlick(hCamera):
    pbEnable = c_int()
    err_code = _sdk.CameraGetAntiFlick(hCamera, byref(pbEnable))
    SetLastError(err_code)
    return pbEnable.value


def CameraGetLightFrequency(hCamera):
    piFrequencySel = c_int()
    err_code = _sdk.CameraGetLightFrequency(hCamera, byref(piFrequencySel))
    SetLastError(err_code)
    return piFrequencySel.value


def CameraSetLightFrequency(hCamera, iFrequencySel):
    err_code = _sdk.CameraSetLightFrequency(hCamera, iFrequencySel)
    SetLastError(err_code)
    return err_code


def CameraSetFrameSpeed(hCamera, iFrameSpeed):
    err_code = _sdk.CameraSetFrameSpeed(hCamera, iFrameSpeed)
    SetLastError(err_code)
    return err_code


def CameraGetFrameSpeed(hCamera):
    piFrameSpeed = c_int()
    err_code = _sdk.CameraGetFrameSpeed(hCamera, byref(piFrameSpeed))
    SetLastError(err_code)
    return piFrameSpeed.value


def CameraSetParameterMode(hCamera, iMode):
    err_code = _sdk.CameraSetParameterMode(hCamera, iMode)
    SetLastError(err_code)
    return err_code


def CameraGetParameterMode(hCamera):
    piTarget = c_int()
    err_code = _sdk.CameraGetParameterMode(hCamera, byref(piTarget))
    SetLastError(err_code)
    return piTarget.value


def CameraSetParameterMask(hCamera, uMask):
    err_code = _sdk.CameraSetParameterMask(hCamera, uMask)
    SetLastError(err_code)
    return err_code


def CameraSaveParameter(hCamera, iTeam):
    err_code = _sdk.CameraSaveParameter(hCamera, iTeam)
    SetLastError(err_code)
    return err_code


def CameraSaveParameterToFile(hCamera, sFileName):
    err_code = _sdk.CameraSaveParameterToFile(
        hCamera, _str_to_string_buffer(sFileName))
    SetLastError(err_code)
    return err_code


def CameraReadParameterFromFile(hCamera, sFileName):
    err_code = _sdk.CameraReadParameterFromFile(
        hCamera, _str_to_string_buffer(sFileName))
    SetLastError(err_code)
    return err_code


def CameraLoadParameter(hCamera, iTeam):
    err_code = _sdk.CameraLoadParameter(hCamera, iTeam)
    SetLastError(err_code)
    return err_code


def CameraGetCurrentParameterGroup(hCamera):
    piTeam = c_int()
    err_code = _sdk.CameraGetCurrentParameterGroup(hCamera, byref(piTeam))
    SetLastError(err_code)
    return piTeam.value


def CameraSetTransPackLen(hCamera, iPackSel):
    err_code = _sdk.CameraSetTransPackLen(hCamera, iPackSel)
    SetLastError(err_code)
    return err_code


def CameraGetTransPackLen(hCamera):
    piPackSel = c_int()
    err_code = _sdk.CameraGetTransPackLen(hCamera, byref(piPackSel))
    SetLastError(err_code)
    return piPackSel.value


def CameraIsAeWinVisible(hCamera):
    pbIsVisible = c_int()
    err_code = _sdk.CameraIsAeWinVisible(hCamera, byref(pbIsVisible))
    SetLastError(err_code)
    return pbIsVisible.value


def CameraSetAeWinVisible(hCamera, bIsVisible):
    err_code = _sdk.CameraSetAeWinVisible(hCamera, bIsVisible)
    SetLastError(err_code)
    return err_code


def CameraGetAeWindow(hCamera):
    piHOff = c_int()
    piVOff = c_int()
    piWidth = c_int()
    piHeight = c_int()
    err_code = _sdk.CameraGetAeWindow(hCamera, byref(
        piHOff), byref(piVOff), byref(piWidth), byref(piHeight))
    SetLastError(err_code)
    return (piHOff.value, piVOff.value, piWidth.value, piHeight.value)


def CameraSetAeWindow(hCamera, iHOff, iVOff, iWidth, iHeight):
    err_code = _sdk.CameraSetAeWindow(hCamera, iHOff, iVOff, iWidth, iHeight)
    SetLastError(err_code)
    return err_code


def CameraSetMirror(hCamera, iDir, bEnable):
    err_code = _sdk.CameraSetMirror(hCamera, iDir, bEnable)
    SetLastError(err_code)
    return err_code


def CameraGetMirror(hCamera, iDir):
    pbEnable = c_int()
    err_code = _sdk.CameraGetMirror(hCamera, iDir, byref(pbEnable))
    SetLastError(err_code)
    return pbEnable.value


def CameraSetRotate(hCamera, iRot):
    err_code = _sdk.CameraSetRotate(hCamera, iRot)
    SetLastError(err_code)
    return err_code


def CameraGetRotate(hCamera):
    iRot = c_int()
    err_code = _sdk.CameraGetRotate(hCamera, byref(iRot))
    SetLastError(err_code)
    return iRot.value


def CameraGetWbWindow(hCamera):
    PiHOff = c_int()
    PiVOff = c_int()
    PiWidth = c_int()
    PiHeight = c_int()
    err_code = _sdk.CameraGetWbWindow(hCamera, byref(
        PiHOff), byref(PiVOff), byref(PiWidth), byref(PiHeight))
    SetLastError(err_code)
    return (PiHOff.value, PiVOff.value, PiWidth.value, PiHeight.value)


def CameraSetWbWindow(hCamera, iHOff, iVOff, iWidth, iHeight):
    err_code = _sdk.CameraSetWbWindow(hCamera, iHOff, iVOff, iWidth, iHeight)
    SetLastError(err_code)
    return err_code


def CameraIsWbWinVisible(hCamera):
    pbShow = c_int()
    err_code = _sdk.CameraIsWbWinVisible(hCamera, byref(pbShow))
    SetLastError(err_code)
    return pbShow.value


def CameraSetWbWinVisible(hCamera, bShow):
    err_code = _sdk.CameraSetWbWinVisible(hCamera, bShow)
    SetLastError(err_code)
    return err_code


def CameraImageOverlay(hCamera, pRgbBuffer, pFrInfo):
    err_code = _sdk.CameraImageOverlay(
        hCamera, c_void_p(pRgbBuffer), byref(pFrInfo))
    SetLastError(err_code)
    return err_code


def CameraSetCrossLine(hCamera, iLine, x, y, uColor, bVisible):
    err_code = _sdk.CameraSetCrossLine(hCamera, iLine, x, y, uColor, bVisible)
    SetLastError(err_code)
    return err_code


def CameraGetCrossLine(hCamera, iLine):
    px = c_int()
    py = c_int()
    pcolor = c_uint()
    pbVisible = c_int()
    err_code = _sdk.CameraGetCrossLine(hCamera, iLine, byref(
        px), byref(py), byref(pcolor), byref(pbVisible))
    SetLastError(err_code)
    return (px.value, py.value, pcolor.value, pbVisible.value)


def CameraGetCapability(hCamera):
    pCameraInfo = tSdkCameraCapbility()
    err_code = _sdk.CameraGetCapability(hCamera, byref(pCameraInfo))
    SetLastError(err_code)
    return pCameraInfo


def CameraWriteSN(hCamera, pbySN, iLevel):
    err_code = _sdk.CameraWriteSN(
        hCamera, _str_to_string_buffer(pbySN), iLevel)
    SetLastError(err_code)
    return err_code


def CameraReadSN(hCamera, iLevel):
    pbySN = create_string_buffer(64)
    err_code = _sdk.CameraReadSN(hCamera, pbySN, iLevel)
    SetLastError(err_code)
    return _string_buffer_to_str(pbySN)


def CameraSetTriggerDelayTime(hCamera, uDelayTimeUs):
    err_code = _sdk.CameraSetTriggerDelayTime(hCamera, uDelayTimeUs)
    SetLastError(err_code)
    return err_code


def CameraGetTriggerDelayTime(hCamera):
    puDelayTimeUs = c_uint()
    err_code = _sdk.CameraGetTriggerDelayTime(hCamera, byref(puDelayTimeUs))
    SetLastError(err_code)
    return puDelayTimeUs.value


def CameraSetTriggerCount(hCamera, iCount):
    err_code = _sdk.CameraSetTriggerCount(hCamera, iCount)
    SetLastError(err_code)
    return err_code


def CameraGetTriggerCount(hCamera):
    piCount = c_int()
    err_code = _sdk.CameraGetTriggerCount(hCamera, byref(piCount))
    SetLastError(err_code)
    return piCount.value


def CameraSoftTrigger(hCamera):
    err_code = _sdk.CameraSoftTrigger(hCamera)
    SetLastError(err_code)
    return err_code


def CameraSetTriggerMode(hCamera, iModeSel):
    err_code = _sdk.CameraSetTriggerMode(hCamera, iModeSel)
    SetLastError(err_code)
    return err_code


def CameraGetTriggerMode(hCamera):
    piModeSel = c_int()
    err_code = _sdk.CameraGetTriggerMode(hCamera, byref(piModeSel))
    SetLastError(err_code)
    return piModeSel.value


def CameraSetStrobeMode(hCamera, iMode):
    err_code = _sdk.CameraSetStrobeMode(hCamera, iMode)
    SetLastError(err_code)
    return err_code


def CameraGetStrobeMode(hCamera):
    piMode = c_int()
    err_code = _sdk.CameraGetStrobeMode(hCamera, byref(piMode))
    SetLastError(err_code)
    return piMode.value


def CameraSetStrobeDelayTime(hCamera, uDelayTimeUs):
    err_code = _sdk.CameraSetStrobeDelayTime(hCamera, uDelayTimeUs)
    SetLastError(err_code)
    return err_code


def CameraGetStrobeDelayTime(hCamera):
    upDelayTimeUs = c_uint()
    err_code = _sdk.CameraGetStrobeDelayTime(hCamera, byref(upDelayTimeUs))
    SetLastError(err_code)
    return upDelayTimeUs.value


def CameraSetStrobePulseWidth(hCamera, uTimeUs):
    err_code = _sdk.CameraSetStrobePulseWidth(hCamera, uTimeUs)
    SetLastError(err_code)
    return err_code


def CameraGetStrobePulseWidth(hCamera):
    upTimeUs = c_uint()
    err_code = _sdk.CameraGetStrobePulseWidth(hCamera, byref(upTimeUs))
    SetLastError(err_code)
    return upTimeUs.value


def CameraSetStrobePolarity(hCamera, uPolarity):
    err_code = _sdk.CameraSetStrobePolarity(hCamera, uPolarity)
    SetLastError(err_code)
    return err_code


def CameraGetStrobePolarity(hCamera):
    upPolarity = c_uint()
    err_code = _sdk.CameraGetStrobePolarity(hCamera, byref(upPolarity))
    SetLastError(err_code)
    return upPolarity.value


def CameraSetExtTrigSignalType(hCamera, iType):
    err_code = _sdk.CameraSetExtTrigSignalType(hCamera, iType)
    SetLastError(err_code)
    return err_code


def CameraGetExtTrigSignalType(hCamera):
    ipType = c_int()
    err_code = _sdk.CameraGetExtTrigSignalType(hCamera, byref(ipType))
    SetLastError(err_code)
    return ipType.value


def CameraSetExtTrigShutterType(hCamera, iType):
    err_code = _sdk.CameraSetExtTrigShutterType(hCamera, iType)
    SetLastError(err_code)
    return err_code


def CameraGetExtTrigShutterType(hCamera):
    ipType = c_int()
    err_code = _sdk.CameraGetExtTrigShutterType(hCamera, byref(ipType))
    SetLastError(err_code)
    return ipType.value


def CameraSetExtTrigDelayTime(hCamera, uDelayTimeUs):
    err_code = _sdk.CameraSetExtTrigDelayTime(hCamera, uDelayTimeUs)
    SetLastError(err_code)
    return err_code


def CameraGetExtTrigDelayTime(hCamera):
    upDelayTimeUs = c_uint()
    err_code = _sdk.CameraGetExtTrigDelayTime(hCamera, byref(upDelayTimeUs))
    SetLastError(err_code)
    return upDelayTimeUs.value


def CameraSetExtTrigJitterTime(hCamera, uTimeUs):
    err_code = _sdk.CameraSetExtTrigJitterTime(hCamera, uTimeUs)
    SetLastError(err_code)
    return err_code


def CameraGetExtTrigJitterTime(hCamera):
    upTimeUs = c_uint()
    err_code = _sdk.CameraGetExtTrigJitterTime(hCamera, byref(upTimeUs))
    SetLastError(err_code)
    return upTimeUs.value


def CameraGetExtTrigCapability(hCamera):
    puCapabilityMask = c_uint()
    err_code = _sdk.CameraGetExtTrigCapability(
        hCamera, byref(puCapabilityMask))
    SetLastError(err_code)
    return puCapabilityMask.value


def CameraPauseLevelTrigger(hCamera):
    err_code = _sdk.CameraPauseLevelTrigger(hCamera)
    SetLastError(err_code)
    return err_code


def CameraGetResolutionForSnap(hCamera):
    pImageResolution = tSdkImageResolution()
    err_code = _sdk.CameraGetResolutionForSnap(
        hCamera, byref(pImageResolution))
    SetLastError(err_code)
    return pImageResolution


def CameraSetResolutionForSnap(hCamera, pImageResolution):
    err_code = _sdk.CameraSetResolutionForSnap(
        hCamera, byref(pImageResolution))
    SetLastError(err_code)
    return err_code


def CameraCustomizeResolution(hCamera):
    pImageCustom = tSdkImageResolution()
    err_code = _sdk.CameraCustomizeResolution(hCamera, byref(pImageCustom))
    SetLastError(err_code)
    return pImageCustom


def CameraCustomizeReferWin(hCamera, iWinType, hParent):
    piHOff = c_int()
    piVOff = c_int()
    piWidth = c_int()
    piHeight = c_int()
    err_code = _sdk.CameraCustomizeReferWin(hCamera, iWinType, hParent, byref(piHOff), byref(piVOff), byref(piWidth),
                                            byref(piHeight))
    SetLastError(err_code)
    return (piHOff.value, piVOff.value, piWidth.value, piHeight.value)


def CameraShowSettingPage(hCamera, bShow):
    err_code = _sdk.CameraShowSettingPage(hCamera, bShow)
    SetLastError(err_code)
    return err_code


def CameraCreateSettingPage(hCamera, hParent, pWinText, pCallbackFunc=None, pCallbackCtx=0, uReserved=0):
    err_code = _sdk.CameraCreateSettingPage(hCamera, hParent, _str_to_string_buffer(pWinText), pCallbackFunc,
                                            c_void_p(pCallbackCtx), uReserved)
    SetLastError(err_code)
    return err_code


def CameraCreateSettingPageEx(hCamera):
    err_code = _sdk.CameraCreateSettingPageEx(hCamera)
    SetLastError(err_code)
    return err_code


def CameraSetActiveSettingSubPage(hCamera, index):
    err_code = _sdk.CameraSetActiveSettingSubPage(hCamera, index)
    SetLastError(err_code)
    return err_code


def CameraSetSettingPageParent(hCamera, hParentWnd, Flags):
    err_code = _sdk.CameraSetSettingPageParent(hCamera, hParentWnd, Flags)
    SetLastError(err_code)
    return err_code


def CameraGetSettingPageHWnd(hCamera):
    hWnd = c_void_p()
    err_code = _sdk.CameraGetSettingPageHWnd(hCamera, byref(hWnd))
    SetLastError(err_code)
    return hWnd.value


def CameraSpecialControl(hCamera, dwCtrlCode, dwParam, lpData):
    err_code = _sdk.CameraSpecialControl(
        hCamera, dwCtrlCode, dwParam, c_void_p(lpData))
    SetLastError(err_code)
    return err_code


def CameraGetFrameStatistic(hCamera):
    psFrameStatistic = tSdkFrameStatistic()
    err_code = _sdk.CameraGetFrameStatistic(hCamera, byref(psFrameStatistic))
    SetLastError(err_code)
    return psFrameStatistic


def CameraSetNoiseFilter(hCamera, bEnable):
    err_code = _sdk.CameraSetNoiseFilter(hCamera, bEnable)
    SetLastError(err_code)
    return err_code


def CameraGetNoiseFilterState(hCamera):
    pEnable = c_int()
    err_code = _sdk.CameraGetNoiseFilterState(hCamera, byref(pEnable))
    SetLastError(err_code)
    return pEnable.value


def CameraRstTimeStamp(hCamera):
    err_code = _sdk.CameraRstTimeStamp(hCamera)
    SetLastError(err_code)
    return err_code


def CameraSaveUserData(hCamera, uStartAddr, pbData):
    err_code = _sdk.CameraSaveUserData(
        hCamera, uStartAddr, pbData, len(pbData))
    SetLastError(err_code)
    return err_code


def CameraLoadUserData(hCamera, uStartAddr, ilen):
    pbData = create_string_buffer(ilen)
    err_code = _sdk.CameraLoadUserData(hCamera, uStartAddr, pbData, ilen)
    SetLastError(err_code)
    return pbData[:]


def CameraGetFriendlyName(hCamera):
    pName = create_string_buffer(64)
    err_code = _sdk.CameraGetFriendlyName(hCamera, pName)
    SetLastError(err_code)
    return _string_buffer_to_str(pName)


def CameraSetFriendlyName(hCamera, pName):
    pNameBuf = _str_to_string_buffer(pName)
    resize(pNameBuf, 64)
    err_code = _sdk.CameraSetFriendlyName(hCamera, pNameBuf)
    SetLastError(err_code)
    return err_code


def CameraSdkGetVersionString():
    pVersionString = create_string_buffer(64)
    err_code = _sdk.CameraSdkGetVersionString(pVersionString)
    SetLastError(err_code)
    return _string_buffer_to_str(pVersionString)


def CameraCheckFwUpdate(hCamera):
    pNeedUpdate = c_int()
    err_code = _sdk.CameraCheckFwUpdate(hCamera, byref(pNeedUpdate))
    SetLastError(err_code)
    return pNeedUpdate.value


def CameraGetFirmwareVersion(hCamera):
    pVersion = create_string_buffer(64)
    err_code = _sdk.CameraGetFirmwareVersion(hCamera, pVersion)
    SetLastError(err_code)
    return _string_buffer_to_str(pVersion)


def CameraGetEnumInfo(hCamera):
    pCameraInfo = tSdkCameraDevInfo()
    err_code = _sdk.CameraGetEnumInfo(hCamera, byref(pCameraInfo))
    SetLastError(err_code)
    return pCameraInfo


def CameraGetInerfaceVersion(hCamera):
    pVersion = create_string_buffer(64)
    err_code = _sdk.CameraGetInerfaceVersion(hCamera, pVersion)
    SetLastError(err_code)
    return _string_buffer_to_str(pVersion)


def CameraSetIOState(hCamera, iOutputIOIndex, uState):
    err_code = _sdk.CameraSetIOState(hCamera, iOutputIOIndex, uState)
    SetLastError(err_code)
    return err_code


def CameraSetIOStateEx(hCamera, iOutputIOIndex, uState):
    err_code = _sdk.CameraSetIOStateEx(hCamera, iOutputIOIndex, uState)
    SetLastError(err_code)
    return err_code


def CameraGetOutPutIOState(hCamera, iOutputIOIndex):
    puState = c_int()
    err_code = _sdk.CameraGetOutPutIOState(
        hCamera, iOutputIOIndex, byref(puState))
    SetLastError(err_code)
    return puState.value


def CameraGetOutPutIOStateEx(hCamera, iOutputIOIndex):
    puState = c_int()
    err_code = _sdk.CameraGetOutPutIOStateEx(
        hCamera, iOutputIOIndex, byref(puState))
    SetLastError(err_code)
    return puState.value


def CameraGetIOState(hCamera, iInputIOIndex):
    puState = c_int()
    err_code = _sdk.CameraGetIOState(hCamera, iInputIOIndex, byref(puState))
    SetLastError(err_code)
    return puState.value


def CameraGetIOStateEx(hCamera, iInputIOIndex):
    puState = c_int()
    err_code = _sdk.CameraGetIOStateEx(hCamera, iInputIOIndex, byref(puState))
    SetLastError(err_code)
    return puState.value


def CameraSetInPutIOMode(hCamera, iInputIOIndex, iMode):
    err_code = _sdk.CameraSetInPutIOMode(hCamera, iInputIOIndex, iMode)
    SetLastError(err_code)
    return err_code


def CameraSetOutPutIOMode(hCamera, iOutputIOIndex, iMode):
    err_code = _sdk.CameraSetOutPutIOMode(hCamera, iOutputIOIndex, iMode)
    SetLastError(err_code)
    return err_code


def CameraSetOutPutPWM(hCamera, iOutputIOIndex, iCycle, uDuty):
    err_code = _sdk.CameraSetOutPutPWM(hCamera, iOutputIOIndex, iCycle, uDuty)
    SetLastError(err_code)
    return err_code


def CameraSetAeAlgorithm(hCamera, iIspProcessor, iAeAlgorithmSel):
    err_code = _sdk.CameraSetAeAlgorithm(
        hCamera, iIspProcessor, iAeAlgorithmSel)
    SetLastError(err_code)
    return err_code


def CameraGetAeAlgorithm(hCamera, iIspProcessor):
    piAlgorithmSel = c_int()
    err_code = _sdk.CameraGetAeAlgorithm(
        hCamera, iIspProcessor, byref(piAlgorithmSel))
    SetLastError(err_code)
    return piAlgorithmSel.value


def CameraSetBayerDecAlgorithm(hCamera, iIspProcessor, iAlgorithmSel):
    err_code = _sdk.CameraSetBayerDecAlgorithm(
        hCamera, iIspProcessor, iAlgorithmSel)
    SetLastError(err_code)
    return err_code


def CameraGetBayerDecAlgorithm(hCamera, iIspProcessor):
    piAlgorithmSel = c_int()
    err_code = _sdk.CameraGetBayerDecAlgorithm(
        hCamera, iIspProcessor, byref(piAlgorithmSel))
    SetLastError(err_code)
    return piAlgorithmSel.value


def CameraSetIspProcessor(hCamera, iIspProcessor):
    err_code = _sdk.CameraSetIspProcessor(hCamera, iIspProcessor)
    SetLastError(err_code)
    return err_code


def CameraGetIspProcessor(hCamera):
    piIspProcessor = c_int()
    err_code = _sdk.CameraGetIspProcessor(hCamera, byref(piIspProcessor))
    SetLastError(err_code)
    return piIspProcessor.value


def CameraSetBlackLevel(hCamera, iBlackLevel):
    err_code = _sdk.CameraSetBlackLevel(hCamera, iBlackLevel)
    SetLastError(err_code)
    return err_code


def CameraGetBlackLevel(hCamera):
    piBlackLevel = c_int()
    err_code = _sdk.CameraGetBlackLevel(hCamera, byref(piBlackLevel))
    SetLastError(err_code)
    return piBlackLevel.value


def CameraSetWhiteLevel(hCamera, iWhiteLevel):
    err_code = _sdk.CameraSetWhiteLevel(hCamera, iWhiteLevel)
    SetLastError(err_code)
    return err_code


def CameraGetWhiteLevel(hCamera):
    piWhiteLevel = c_int()
    err_code = _sdk.CameraGetWhiteLevel(hCamera, byref(piWhiteLevel))
    SetLastError(err_code)
    return piWhiteLevel.value


def CameraSetIspOutFormat(hCamera, uFormat):
    err_code = _sdk.CameraSetIspOutFormat(hCamera, uFormat)
    SetLastError(err_code)
    return err_code


def CameraGetIspOutFormat(hCamera):
    puFormat = c_int()
    err_code = _sdk.CameraGetIspOutFormat(hCamera, byref(puFormat))
    SetLastError(err_code)
    return puFormat.value


def CameraGetErrorString(iStatusCode):
    _sdk.CameraGetErrorString.restype = c_char_p
    msg = _sdk.CameraGetErrorString(iStatusCode)
    if msg:
        return _string_buffer_to_str(msg)
    else:
        return ''


def CameraGetImageBufferEx2(hCamera, pImageData, uOutFormat, wTimes):
    piWidth = c_int()
    piHeight = c_int()
    err_code = _sdk.CameraGetImageBufferEx2(hCamera, c_void_p(pImageData), uOutFormat, byref(piWidth), byref(piHeight),
                                            wTimes)
    SetLastError(err_code)
    if err_code != 0:
        raise CameraException(err_code)
    return (piWidth.value, piHeight.value)


def CameraGetImageBufferEx3(hCamera, pImageData, uOutFormat, wTimes):
    piWidth = c_int()
    piHeight = c_int()
    puTimeStamp = c_int()
    err_code = _sdk.CameraGetImageBufferEx3(hCamera, c_void_p(pImageData), uOutFormat, byref(piWidth), byref(piHeight),
                                            byref(puTimeStamp), wTimes)
    SetLastError(err_code)
    if err_code != 0:
        raise CameraException(err_code)
    return (piWidth.value, piHeight.value, puTimeStamp.value)


def CameraGetCapabilityEx2(hCamera):
    pMaxWidth = c_int()
    pMaxHeight = c_int()
    pbColorCamera = c_int()
    err_code = _sdk.CameraGetCapabilityEx2(hCamera, byref(
        pMaxWidth), byref(pMaxHeight), byref(pbColorCamera))
    SetLastError(err_code)
    return (pMaxWidth.value, pMaxHeight.value, pbColorCamera.value)


def CameraReConnect(hCamera):
    err_code = _sdk.CameraReConnect(hCamera)
    SetLastError(err_code)
    return err_code


def CameraConnectTest(hCamera):
    err_code = _sdk.CameraConnectTest(hCamera)
    SetLastError(err_code)
    return err_code


def CameraSetLedEnable(hCamera, index, enable):
    err_code = _sdk.CameraSetLedEnable(hCamera, index, enable)
    SetLastError(err_code)
    return err_code


def CameraGetLedEnable(hCamera, index):
    enable = c_int()
    err_code = _sdk.CameraGetLedEnable(hCamera, index, byref(enable))
    SetLastError(err_code)
    return enable.value


def CameraSetLedOnOff(hCamera, index, onoff):
    err_code = _sdk.CameraSetLedOnOff(hCamera, index, onoff)
    SetLastError(err_code)
    return err_code


def CameraGetLedOnOff(hCamera, index):
    onoff = c_int()
    err_code = _sdk.CameraGetLedOnOff(hCamera, index, byref(onoff))
    SetLastError(err_code)
    return onoff.value


def CameraSetLedDuration(hCamera, index, duration):
    err_code = _sdk.CameraSetLedDuration(hCamera, index, duration)
    SetLastError(err_code)
    return err_code


def CameraGetLedDuration(hCamera, index):
    duration = c_uint()
    err_code = _sdk.CameraGetLedDuration(hCamera, index, byref(duration))
    SetLastError(err_code)
    return duration.value


def CameraSetLedBrightness(hCamera, index, uBrightness):
    err_code = _sdk.CameraSetLedBrightness(hCamera, index, uBrightness)
    SetLastError(err_code)
    return err_code


def CameraGetLedBrightness(hCamera, index):
    uBrightness = c_uint()
    err_code = _sdk.CameraGetLedBrightness(hCamera, index, byref(uBrightness))
    SetLastError(err_code)
    return uBrightness.value


def CameraEnableTransferRoi(hCamera, uEnableMask):
    err_code = _sdk.CameraEnableTransferRoi(hCamera, uEnableMask)
    SetLastError(err_code)
    return err_code


def CameraSetTransferRoi(hCamera, index, X1, Y1, X2, Y2):
    err_code = _sdk.CameraSetTransferRoi(hCamera, index, X1, Y1, X2, Y2)
    SetLastError(err_code)
    return err_code


def CameraGetTransferRoi(hCamera, index):
    pX1 = c_uint()
    pY1 = c_uint()
    pX2 = c_uint()
    pY2 = c_uint()
    err_code = _sdk.CameraGetTransferRoi(
        hCamera, index, byref(pX1), byref(pY1), byref(pX2), byref(pY2))
    SetLastError(err_code)
    return (pX1.value, pY1.value, pX2.value, pY2.value)


def CameraAlignMalloc(size, align=16):
    _sdk.CameraAlignMalloc.restype = c_void_p
    r = _sdk.CameraAlignMalloc(size, align)
    return r


def CameraAlignFree(membuffer):
    _sdk.CameraAlignFree(c_void_p(membuffer))


def CameraSetAutoConnect(hCamera, bEnable):
    err_code = _sdk.CameraSetAutoConnect(hCamera, bEnable)
    SetLastError(err_code)
    return err_code


def CameraGetAutoConnect(hCamera):
    pbEnable = c_int()
    err_code = _sdk.CameraGetAutoConnect(hCamera, byref(pbEnable))
    SetLastError(err_code)
    return pbEnable.value


def CameraGetReConnectCounts(hCamera):
    puCounts = c_int()
    err_code = _sdk.CameraGetReConnectCounts(hCamera, byref(puCounts))
    SetLastError(err_code)
    return puCounts.value


def CameraSetSingleGrabMode(hCamera, bEnable):
    err_code = _sdk.CameraSetSingleGrabMode(hCamera, bEnable)
    SetLastError(err_code)
    return err_code


def CameraGetSingleGrabMode(hCamera):
    pbEnable = c_int()
    err_code = _sdk.CameraGetSingleGrabMode(hCamera, byref(pbEnable))
    SetLastError(err_code)
    return pbEnable.value


def CameraRestartGrab(hCamera):
    err_code = _sdk.CameraRestartGrab(hCamera)
    SetLastError(err_code)
    return err_code


def CameraEvaluateImageDefinition(hCamera, iAlgorithSel, pbyIn, pFrInfo):
    DefinitionValue = c_double()
    err_code = _sdk.CameraEvaluateImageDefinition(hCamera, iAlgorithSel, c_void_p(pbyIn), byref(pFrInfo),
                                                  byref(DefinitionValue))
    SetLastError(err_code)
    return DefinitionValue.value


def CameraDrawText(pRgbBuffer, pFrInfo, pFontFileName, FontWidth, FontHeight, pText, Left, Top, Width, Height,
                   TextColor, uFlags):
    err_code = _sdk.CameraDrawText(c_void_p(pRgbBuffer), byref(pFrInfo), _str_to_string_buffer(pFontFileName),
                                   FontWidth, FontHeight, _str_to_string_buffer(
                                       pText), Left, Top, Width, Height,
                                   TextColor, uFlags)
    SetLastError(err_code)
    return err_code


def CameraGigeEnumerateDevice(ipList, MaxCount=32):
    if type(ipList) in (list, tuple):
        ipList = map(lambda x: _str_to_string_buffer(x), ipList)
    else:
        ipList = (_str_to_string_buffer(ipList),)
    numIP = len(ipList)
    ppIpList = (c_void_p * numIP)(*map(lambda x: addressof(x), ipList))
    Nums = c_int(MaxCount)
    pCameraList = (tSdkCameraDevInfo * Nums.value)()
    err_code = _sdk.CameraGigeEnumerateDevice(
        ppIpList, numIP, pCameraList, byref(Nums))
    SetLastError(err_code)
    return pCameraList[0:Nums.value]


def CameraGigeGetIp(pCameraInfo):
    CamIp = create_string_buffer(32)
    CamMask = create_string_buffer(32)
    CamGateWay = create_string_buffer(32)
    EtIp = create_string_buffer(32)
    EtMask = create_string_buffer(32)
    EtGateWay = create_string_buffer(32)
    err_code = _sdk.CameraGigeGetIp(
        byref(pCameraInfo), CamIp, CamMask, CamGateWay, EtIp, EtMask, EtGateWay)
    SetLastError(err_code)
    return (_string_buffer_to_str(CamIp), _string_buffer_to_str(CamMask), _string_buffer_to_str(CamGateWay),
            _string_buffer_to_str(EtIp), _string_buffer_to_str(EtMask), _string_buffer_to_str(EtGateWay))


def CameraGigeSetIp(pCameraInfo, Ip, SubMask, GateWay, bPersistent):
    err_code = _sdk.CameraGigeSetIp(byref(pCameraInfo),
                                    _str_to_string_buffer(
                                        Ip), _str_to_string_buffer(SubMask),
                                    _str_to_string_buffer(GateWay), bPersistent)
    SetLastError(err_code)
    return err_code


def CameraGigeGetMac(pCameraInfo):
    CamMac = create_string_buffer(32)
    EtMac = create_string_buffer(32)
    err_code = _sdk.CameraGigeGetMac(byref(pCameraInfo), CamMac, EtMac)
    SetLastError(err_code)
    return (_string_buffer_to_str(CamMac), _string_buffer_to_str(EtMac))


def CameraEnableFastResponse(hCamera):
    err_code = _sdk.CameraEnableFastResponse(hCamera)
    SetLastError(err_code)
    return err_code


def CameraSetCorrectDeadPixel(hCamera, bEnable):
    err_code = _sdk.CameraSetCorrectDeadPixel(hCamera, bEnable)
    SetLastError(err_code)
    return err_code


def CameraGetCorrectDeadPixel(hCamera):
    pbEnable = c_int()
    err_code = _sdk.CameraGetCorrectDeadPixel(hCamera, byref(pbEnable))
    SetLastError(err_code)
    return pbEnable.value


def CameraFlatFieldingCorrectSetEnable(hCamera, bEnable):
    err_code = _sdk.CameraFlatFieldingCorrectSetEnable(hCamera, bEnable)
    SetLastError(err_code)
    return err_code


def CameraFlatFieldingCorrectGetEnable(hCamera):
    pbEnable = c_int()
    err_code = _sdk.CameraFlatFieldingCorrectGetEnable(
        hCamera, byref(pbEnable))
    SetLastError(err_code)
    return pbEnable.value


def CameraFlatFieldingCorrectSetParameter(hCamera, pDarkFieldingImage, pDarkFieldingFrInfo, pLightFieldingImage,
                                          pLightFieldingFrInfo):
    err_code = _sdk.CameraFlatFieldingCorrectSetParameter(hCamera, c_void_p(pDarkFieldingImage),
                                                          byref(pDarkFieldingFrInfo), c_void_p(
                                                              pLightFieldingImage),
                                                          byref(pLightFieldingFrInfo))
    SetLastError(err_code)
    return err_code


def CameraFlatFieldingCorrectGetParameterState(hCamera):
    pbValid = c_int()
    pFilePath = create_string_buffer(1024)
    err_code = _sdk.CameraFlatFieldingCorrectGetParameterState(
        hCamera, byref(pbValid), pFilePath)
    SetLastError(err_code)
    return (pbValid.value, _string_buffer_to_str(pFilePath))


def CameraFlatFieldingCorrectSaveParameterToFile(hCamera, pszFileName):
    err_code = _sdk.CameraFlatFieldingCorrectSaveParameterToFile(
        hCamera, _str_to_string_buffer(pszFileName))
    SetLastError(err_code)
    return err_code


def CameraFlatFieldingCorrectLoadParameterFromFile(hCamera, pszFileName):
    err_code = _sdk.CameraFlatFieldingCorrectLoadParameterFromFile(
        hCamera, _str_to_string_buffer(pszFileName))
    SetLastError(err_code)
    return err_code


def CameraCommonCall(hCamera, pszCall, uResultBufSize):
    pszResult = create_string_buffer(
        uResultBufSize) if uResultBufSize > 0 else None
    err_code = _sdk.CameraCommonCall(
        hCamera, _str_to_string_buffer(pszCall), pszResult, uResultBufSize)
    SetLastError(err_code)
    return _string_buffer_to_str(pszResult) if pszResult else ''


def CameraSetDenoise3DParams(hCamera, bEnable, nCount, Weights):
    assert (nCount >= 2 and nCount <= 8)
    if Weights:
        assert (len(Weights) == nCount)
        WeightsNative = (c_float * nCount)(*Weights)
    else:
        WeightsNative = None
    err_code = _sdk.CameraSetDenoise3DParams(
        hCamera, bEnable, nCount, WeightsNative)
    SetLastError(err_code)
    return err_code


def CameraGetDenoise3DParams(hCamera):
    bEnable = c_int()
    nCount = c_int()
    bUseWeight = c_int()
    Weights = (c_float * 8)()
    err_code = _sdk.CameraGetDenoise3DParams(hCamera, byref(
        bEnable), byref(nCount), byref(bUseWeight), Weights)
    SetLastError(err_code)
    bEnable, nCount, bUseWeight = bEnable.value, nCount.value, bUseWeight.value
    if bUseWeight:
        Weights = Weights[:nCount]
    else:
        Weights = None
    return (bEnable, nCount, bUseWeight, Weights)


def CameraManualDenoise3D(InFramesHead, InFramesData, nCount, Weights, OutFrameHead, OutFrameData):
    assert (nCount > 0)
    assert (len(InFramesData) == nCount)
    assert (Weights is None or len(Weights) == nCount)
    InFramesDataNative = (c_void_p * nCount)(*InFramesData)
    WeightsNative = (c_float * nCount)(*Weights) if Weights else None
    err_code = _sdk.CameraManualDenoise3D(byref(InFramesHead), InFramesDataNative, nCount, WeightsNative,
                                          byref(OutFrameHead), c_void_p(OutFrameData))
    SetLastError(err_code)
    return err_code


def CameraCustomizeDeadPixels(hCamera, hParent):
    err_code = _sdk.CameraCustomizeDeadPixels(hCamera, hParent)
    SetLastError(err_code)
    return err_code


def CameraReadDeadPixels(hCamera):
    pNumPixel = c_int()
    err_code = _sdk.CameraReadDeadPixels(hCamera, None, None, byref(pNumPixel))
    SetLastError(err_code)
    if pNumPixel.value < 1:
        return None
    UShortArray = c_ushort * pNumPixel.value
    pRows = UShortArray()
    pCols = UShortArray()
    err_code = _sdk.CameraReadDeadPixels(
        hCamera, pRows, pCols, byref(pNumPixel))
    SetLastError(err_code)
    if err_code == 0:
        pNumPixel = pNumPixel.value
    else:
        pNumPixel = 0
    return (pRows[:pNumPixel], pCols[:pNumPixel])


def CameraAddDeadPixels(hCamera, pRows, pCols, NumPixel):
    UShortArray = c_ushort * NumPixel
    pRowsNative = UShortArray(*pRows)
    pColsNative = UShortArray(*pCols)
    err_code = _sdk.CameraAddDeadPixels(
        hCamera, pRowsNative, pColsNative, NumPixel)
    SetLastError(err_code)
    return err_code


def CameraRemoveDeadPixels(hCamera, pRows, pCols, NumPixel):
    UShortArray = c_ushort * NumPixel
    pRowsNative = UShortArray(*pRows)
    pColsNative = UShortArray(*pCols)
    err_code = _sdk.CameraRemoveDeadPixels(
        hCamera, pRowsNative, pColsNative, NumPixel)
    SetLastError(err_code)
    return err_code


def CameraRemoveAllDeadPixels(hCamera):
    err_code = _sdk.CameraRemoveAllDeadPixels(hCamera)
    SetLastError(err_code)
    return err_code


def CameraSaveDeadPixels(hCamera):
    err_code = _sdk.CameraSaveDeadPixels(hCamera)
    SetLastError(err_code)
    return err_code


def CameraSaveDeadPixelsToFile(hCamera, sFileName):
    err_code = _sdk.CameraSaveDeadPixelsToFile(
        hCamera, _str_to_string_buffer(sFileName))
    SetLastError(err_code)
    return err_code


def CameraLoadDeadPixelsFromFile(hCamera, sFileName):
    err_code = _sdk.CameraLoadDeadPixelsFromFile(
        hCamera, _str_to_string_buffer(sFileName))
    SetLastError(err_code)
    return err_code


def CameraGetImageBufferPriority(hCamera, wTimes, Priority):
    pFrameInfo = tSdkFrameHead()
    pbyBuffer = c_void_p()
    err_code = _sdk.CameraGetImageBufferPriority(
        hCamera, byref(pFrameInfo), byref(pbyBuffer), wTimes, Priority)
    SetLastError(err_code)
    if err_code != 0:
        raise CameraException(err_code)
    return (pbyBuffer.value, pFrameInfo)


def CameraGetImageBufferPriorityEx(hCamera, wTimes, Priority):
    _sdk.CameraGetImageBufferPriorityEx.restype = c_void_p
    piWidth = c_int()
    piHeight = c_int()
    pFrameBuffer = _sdk.CameraGetImageBufferPriorityEx(
        hCamera, byref(piWidth), byref(piHeight), wTimes, Priority)
    err_code = CAMERA_STATUS_SUCCESS if pFrameBuffer else CAMERA_STATUS_TIME_OUT
    SetLastError(err_code)
    if pFrameBuffer:
        return (pFrameBuffer, piWidth.value, piHeight.value)
    else:
        raise CameraException(err_code)


def CameraGetImageBufferPriorityEx2(hCamera, pImageData, uOutFormat, wTimes, Priority):
    piWidth = c_int()
    piHeight = c_int()
    err_code = _sdk.CameraGetImageBufferPriorityEx2(hCamera, c_void_p(pImageData), uOutFormat, byref(piWidth),
                                                    byref(piHeight), wTimes, Priority)
    SetLastError(err_code)
    if err_code != 0:
        raise CameraException(err_code)
    return (piWidth.value, piHeight.value)


def CameraGetImageBufferPriorityEx3(hCamera, pImageData, uOutFormat, wTimes, Priority):
    piWidth = c_int()
    piHeight = c_int()
    puTimeStamp = c_uint()
    err_code = _sdk.CameraGetImageBufferPriorityEx3(hCamera, c_void_p(pImageData), uOutFormat, byref(piWidth),
                                                    byref(piHeight), byref(puTimeStamp), wTimes, Priority)
    SetLastError(err_code)
    if err_code != 0:
        raise CameraException(err_code)
    return (piWidth.value, piHeight.value, puTimeStamp.value)


def CameraClearBuffer(hCamera):
    err_code = _sdk.CameraClearBuffer(hCamera)
    SetLastError(err_code)
    return err_code


def CameraSoftTriggerEx(hCamera, uFlags):
    err_code = _sdk.CameraSoftTriggerEx(hCamera, uFlags)
    SetLastError(err_code)
    return err_code


def CameraSetHDR(hCamera, value):
    err_code = _sdk.CameraSetHDR(hCamera, value)
    SetLastError(err_code)
    return err_code


def CameraGetHDR(hCamera):
    value = c_int()
    err_code = _sdk.CameraGetHDR(hCamera, byref(value))
    SetLastError(err_code)
    return value.value


def CameraGetFrameID(hCamera):
    FrameID = c_uint()
    err_code = _sdk.CameraGetFrameID(hCamera, byref(FrameID))
    SetLastError(err_code)
    return FrameID.value


def CameraGetFrameTimeStamp(hCamera):
    TimeStamp = c_uint64()
    TimeStampL = c_uint32.from_buffer(TimeStamp)
    TimeStampH = c_uint32.from_buffer(TimeStamp, 4)
    err_code = _sdk.CameraGetFrameTimeStamp(
        hCamera, byref(TimeStampL), byref(TimeStampH))
    SetLastError(err_code)
    return TimeStamp.value


def CameraSetHDRGainMode(hCamera, value):
    err_code = _sdk.CameraSetHDRGainMode(hCamera, value)
    SetLastError(err_code)
    return err_code


def CameraGetHDRGainMode(hCamera):
    value = c_int()
    err_code = _sdk.CameraGetHDRGainMode(hCamera, byref(value))
    SetLastError(err_code)
    return value.value


def CameraCreateDIBitmap(hDC, pFrameBuffer, pFrameHead):
    outBitmap = c_void_p()
    err_code = _sdk.CameraCreateDIBitmap(hDC, c_void_p(
        pFrameBuffer), byref(pFrameHead), byref(outBitmap))
    SetLastError(err_code)
    return outBitmap.value


def CameraDrawFrameBuffer(pFrameBuffer, pFrameHead, hWnd, Algorithm, Mode):
    err_code = _sdk.CameraDrawFrameBuffer(c_void_p(pFrameBuffer), byref(
        pFrameHead), c_void_p(hWnd), Algorithm, Mode)
    SetLastError(err_code)
    return err_code


def CameraFlipFrameBuffer(pFrameBuffer, pFrameHead, Flags):
    err_code = _sdk.CameraFlipFrameBuffer(
        c_void_p(pFrameBuffer), byref(pFrameHead), Flags)
    SetLastError(err_code)
    return err_code


def CameraConvertFrameBufferFormat(hCamera, pInFrameBuffer, pOutFrameBuffer, outWidth, outHeight, outMediaType,
                                   pFrameHead):
    err_code = _sdk.CameraConvertFrameBufferFormat(hCamera, c_void_p(pInFrameBuffer), c_void_p(pOutFrameBuffer),
                                                   outWidth, outHeight, outMediaType, byref(pFrameHead))
    SetLastError(err_code)
    return err_code


def CameraSetConnectionStatusCallback(hCamera, pCallBack, pContext=0):
    err_code = _sdk.CameraSetConnectionStatusCallback(
        hCamera, pCallBack, c_void_p(pContext))
    SetLastError(err_code)
    return err_code


def CameraSetLightingControllerMode(hCamera, index, mode):
    err_code = _sdk.CameraSetLightingControllerMode(hCamera, index, mode)
    SetLastError(err_code)
    return err_code


def CameraSetLightingControllerState(hCamera, index, state):
    err_code = _sdk.CameraSetLightingControllerState(hCamera, index, state)
    SetLastError(err_code)
    return err_code


def CameraSetFrameResendCount(hCamera, count):
    err_code = _sdk.CameraSetFrameResendCount(hCamera, count)
    SetLastError(err_code)
    return err_code


def CameraSetUndistortParams(hCamera, width, height, cameraMatrix, distCoeffs):
    assert (len(cameraMatrix) == 4)
    assert (len(distCoeffs) == 5)
    cameraMatrixNative = (c_double * len(cameraMatrix))(*cameraMatrix)
    distCoeffsNative = (c_double * len(distCoeffs))(*distCoeffs)
    err_code = _sdk.CameraSetUndistortParams(
        hCamera, width, height, cameraMatrixNative, distCoeffsNative)
    SetLastError(err_code)
    return err_code


def CameraGetUndistortParams(hCamera):
    width = c_int()
    height = c_int()
    cameraMatrix = (c_double * 4)()
    distCoeffs = (c_double * 5)()
    err_code = _sdk.CameraGetUndistortParams(hCamera, byref(
        width), byref(height), cameraMatrix, distCoeffs)
    SetLastError(err_code)
    width, height = width.value, height.value
    cameraMatrix = cameraMatrix[:]
    distCoeffs = distCoeffs[:]
    return (width, height, cameraMatrix, distCoeffs)


def CameraSetUndistortEnable(hCamera, bEnable):
    err_code = _sdk.CameraSetUndistortEnable(hCamera, bEnable)
    SetLastError(err_code)
    return err_code


def CameraGetUndistortEnable(hCamera):
    value = c_int()
    err_code = _sdk.CameraGetUndistortEnable(hCamera, byref(value))
    SetLastError(err_code)
    return value.value


def CameraCustomizeUndistort(hCamera, hParent):
    err_code = _sdk.CameraCustomizeUndistort(hCamera, hParent)
    SetLastError(err_code)
    return err_code


def CameraGetEyeCount(hCamera):
    EyeCount = c_int()
    err_code = _sdk.CameraGetEyeCount(hCamera, byref(EyeCount))
    SetLastError(err_code)
    return EyeCount.value


def CameraMultiEyeImageProcess(hCamera, iEyeIndex, pbyIn, pInFrInfo, pbyOut, pOutFrInfo, uOutFormat, uReserved):
    err_code = _sdk.CameraMultiEyeImageProcess(hCamera, iEyeIndex, c_void_p(pbyIn), byref(pInFrInfo), c_void_p(pbyOut),
                                               byref(pOutFrInfo), uOutFormat, uReserved)
    SetLastError(err_code)
    return err_code


def CameraGrabber_CreateFromDevicePage():
    Grabber = c_void_p()
    err_code = _sdk.CameraGrabber_CreateFromDevicePage(byref(Grabber))
    SetLastError(err_code)
    if err_code != 0:
        raise CameraException(err_code)
    return Grabber.value


def CameraGrabber_CreateByIndex(Index):
    Grabber = c_void_p()
    err_code = _sdk.CameraGrabber_CreateByIndex(byref(Grabber), Index)
    SetLastError(err_code)
    if err_code != 0:
        raise CameraException(err_code)
    return Grabber.value


def CameraGrabber_CreateByName(Name):
    Grabber = c_void_p()
    err_code = _sdk.CameraGrabber_CreateByName(
        byref(Grabber), _str_to_string_buffer(Name))
    SetLastError(err_code)
    if err_code != 0:
        raise CameraException(err_code)
    return Grabber.value


def CameraGrabber_Create(pDevInfo):
    Grabber = c_void_p()
    err_code = _sdk.CameraGrabber_Create(byref(Grabber), byref(pDevInfo))
    SetLastError(err_code)
    if err_code != 0:
        raise CameraException(err_code)
    return Grabber.value


def CameraGrabber_Destroy(Grabber):
    err_code = _sdk.CameraGrabber_Destroy(c_void_p(Grabber))
    SetLastError(err_code)
    return err_code


def CameraGrabber_SetHWnd(Grabber, hWnd):
    err_code = _sdk.CameraGrabber_SetHWnd(c_void_p(Grabber), c_void_p(hWnd))
    SetLastError(err_code)
    return err_code


def CameraGrabber_SetPriority(Grabber, Priority):
    err_code = _sdk.CameraGrabber_SetPriority(c_void_p(Grabber), Priority)
    SetLastError(err_code)
    return err_code


def CameraGrabber_StartLive(Grabber):
    err_code = _sdk.CameraGrabber_StartLive(c_void_p(Grabber))
    SetLastError(err_code)
    return err_code


def CameraGrabber_StopLive(Grabber):
    err_code = _sdk.CameraGrabber_StopLive(c_void_p(Grabber))
    SetLastError(err_code)
    return err_code


def CameraGrabber_SaveImage(Grabber, TimeOut):
    Image = c_void_p()
    err_code = _sdk.CameraGrabber_SaveImage(
        c_void_p(Grabber), byref(Image), TimeOut)
    SetLastError(err_code)
    if err_code != 0:
        raise CameraException(err_code)
    return Image.value


def CameraGrabber_SaveImageAsync(Grabber):
    err_code = _sdk.CameraGrabber_SaveImageAsync(c_void_p(Grabber))
    SetLastError(err_code)
    return err_code


def CameraGrabber_SaveImageAsyncEx(Grabber, UserData):
    err_code = _sdk.CameraGrabber_SaveImageAsyncEx(
        c_void_p(Grabber), c_void_p(UserData))
    SetLastError(err_code)
    return err_code


def CameraGrabber_SetSaveImageCompleteCallback(Grabber, Callback, Context=0):
    err_code = _sdk.CameraGrabber_SetSaveImageCompleteCallback(
        c_void_p(Grabber), Callback, c_void_p(Context))
    SetLastError(err_code)
    return err_code


def CameraGrabber_SetFrameListener(Grabber, Listener, Context=0):
    err_code = _sdk.CameraGrabber_SetFrameListener(
        c_void_p(Grabber), Listener, c_void_p(Context))
    SetLastError(err_code)
    return err_code


def CameraGrabber_SetRawCallback(Grabber, Callback, Context=0):
    err_code = _sdk.CameraGrabber_SetRawCallback(
        c_void_p(Grabber), Callback, c_void_p(Context))
    SetLastError(err_code)
    return err_code


def CameraGrabber_SetRGBCallback(Grabber, Callback, Context=0):
    err_code = _sdk.CameraGrabber_SetRGBCallback(
        c_void_p(Grabber), Callback, c_void_p(Context))
    SetLastError(err_code)
    return err_code


def CameraGrabber_GetCameraHandle(Grabber):
    hCamera = c_int()
    err_code = _sdk.CameraGrabber_GetCameraHandle(
        c_void_p(Grabber), byref(hCamera))
    SetLastError(err_code)
    return hCamera.value


def CameraGrabber_GetStat(Grabber):
    stat = tSdkGrabberStat()
    err_code = _sdk.CameraGrabber_GetStat(c_void_p(Grabber), byref(stat))
    SetLastError(err_code)
    return stat


def CameraGrabber_GetCameraDevInfo(Grabber):
    DevInfo = tSdkCameraDevInfo()
    err_code = _sdk.CameraGrabber_GetCameraDevInfo(
        c_void_p(Grabber), byref(DevInfo))
    SetLastError(err_code)
    return DevInfo


def CameraImage_Create(pFrameBuffer, pFrameHead, bCopy):
    Image = c_void_p()
    err_code = _sdk.CameraImage_Create(
        byref(Image), c_void_p(pFrameBuffer), byref(pFrameHead), bCopy)
    SetLastError(err_code)
    return Image.value


def CameraImage_CreateEmpty():
    Image = c_void_p()
    err_code = _sdk.CameraImage_CreateEmpty(byref(Image))
    SetLastError(err_code)
    return Image.value


def CameraImage_Destroy(Image):
    err_code = _sdk.CameraImage_Destroy(c_void_p(Image))
    SetLastError(err_code)
    return err_code


def CameraImage_GetData(Image):
    DataBuffer = c_void_p()
    HeadPtr = c_void_p()
    err_code = _sdk.CameraImage_GetData(
        c_void_p(Image), byref(DataBuffer), byref(HeadPtr))
    SetLastError(err_code)
    if err_code == 0:
        return (DataBuffer.value, tSdkFrameHead.from_address(HeadPtr.value))
    else:
        return (0, None)


def CameraImage_GetUserData(Image):
    UserData = c_void_p()
    err_code = _sdk.CameraImage_GetUserData(c_void_p(Image), byref(UserData))
    SetLastError(err_code)
    return UserData.value


def CameraImage_SetUserData(Image, UserData):
    err_code = _sdk.CameraImage_SetUserData(
        c_void_p(Image), c_void_p(UserData))
    SetLastError(err_code)
    return err_code


def CameraImage_IsEmpty(Image):
    IsEmpty = c_int()
    err_code = _sdk.CameraImage_IsEmpty(c_void_p(Image), byref(IsEmpty))
    SetLastError(err_code)
    return IsEmpty.value


def CameraImage_Draw(Image, hWnd, Algorithm):
    err_code = _sdk.CameraImage_Draw(
        c_void_p(Image), c_void_p(hWnd), Algorithm)
    SetLastError(err_code)
    return err_code


def CameraImage_DrawFit(Image, hWnd, Algorithm):
    err_code = _sdk.CameraImage_DrawFit(
        c_void_p(Image), c_void_p(hWnd), Algorithm)
    SetLastError(err_code)
    return err_code


def CameraImage_DrawToDC(Image, hDC, Algorithm, xDst, yDst, cxDst, cyDst):
    err_code = _sdk.CameraImage_DrawToDC(
        c_void_p(Image), c_void_p(hDC), Algorithm, xDst, yDst, cxDst, cyDst)
    SetLastError(err_code)
    return err_code


def CameraImage_DrawToDCFit(Image, hDC, Algorithm, xDst, yDst, cxDst, cyDst):
    err_code = _sdk.CameraImage_DrawToDCFit(
        c_void_p(Image), c_void_p(hDC), Algorithm, xDst, yDst, cxDst, cyDst)
    SetLastError(err_code)
    return err_code


def CameraImage_BitBlt(Image, hWnd, xDst, yDst, cxDst, cyDst, xSrc, ySrc):
    err_code = _sdk.CameraImage_BitBlt(c_void_p(Image), c_void_p(
        hWnd), xDst, yDst, cxDst, cyDst, xSrc, ySrc)
    SetLastError(err_code)
    return err_code


def CameraImage_BitBltToDC(Image, hDC, xDst, yDst, cxDst, cyDst, xSrc, ySrc):
    err_code = _sdk.CameraImage_BitBltToDC(
        c_void_p(Image), c_void_p(hDC), xDst, yDst, cxDst, cyDst, xSrc, ySrc)
    SetLastError(err_code)
    return err_code


def CameraImage_SaveAsBmp(Image, FileName):
    err_code = _sdk.CameraImage_SaveAsBmp(
        c_void_p(Image), _str_to_string_buffer(FileName))
    SetLastError(err_code)
    return err_code


def CameraImage_SaveAsJpeg(Image, FileName, Quality):
    err_code = _sdk.CameraImage_SaveAsJpeg(
        c_void_p(Image), _str_to_string_buffer(FileName), Quality)
    SetLastError(err_code)
    return err_code


def CameraImage_SaveAsPng(Image, FileName):
    err_code = _sdk.CameraImage_SaveAsPng(
        c_void_p(Image), _str_to_string_buffer(FileName))
    SetLastError(err_code)
    return err_code


def CameraImage_SaveAsRaw(Image, FileName, Format):
    err_code = _sdk.CameraImage_SaveAsRaw(
        c_void_p(Image), _str_to_string_buffer(FileName), Format)
    SetLastError(err_code)
    return err_code


def CameraImage_IPicture(Image):
    NewPic = c_void_p()
    err_code = _sdk.CameraImage_IPicture(c_void_p(Image), byref(NewPic))
    SetLastError(err_code)
    return NewPic.value
