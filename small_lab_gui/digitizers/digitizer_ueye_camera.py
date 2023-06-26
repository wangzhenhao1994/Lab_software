from small_lab_gui.digitizers.digitizer import digitizer

from pyueye import ueye
import numpy as np
import cv2
import sys

from math import floor
from threading import Event


class ueye_camera(digitizer):
    def __init__(self, path='C:\\Users\\Labor\\Documents\\python\\small_lab_gui\\company_dll\\greateyes_sdk\\c\\bin\\x64'):
        self.num_sensors = 1
        self.hCam = ueye.HIDS(0)             #0: first available camera;  1-254: The camera with the specified camera ID
        sInfo = ueye.SENSORINFO()
        self.pcImageMemory = ueye.c_mem_p()
        self.MemID = ueye.int()
        rectAOI = ueye.IS_RECT()
        self.pitch = ueye.INT()
        self.nBitsPerPixel = ueye.INT(8)    #24: bits per pixel for color mode; take 8 bits per pixel for monochrome
        channels = 1                    #3: channels for color mode(RGB); take 1 channel for monochrome
        m_nColorMode = ueye.INT()		# Y8/RGB16/RGB24/REG32
        self.bytes_per_pixel = int(self.nBitsPerPixel / 8)
        # Starts the driver and establishes the connection to the camera
        nRet = ueye.is_InitCamera(self.hCam, None)
        if nRet != ueye.IS_SUCCESS:
            print("is_InitCamera ERROR")
        # You can query additional information about the sensor type used in the camera
        nRet = ueye.is_GetSensorInfo(self.hCam, sInfo)
        if nRet != ueye.IS_SUCCESS:
            print("is_GetSensorInfo ERROR")
        nRet = ueye.is_ResetToDefault(self.hCam)
        if nRet != ueye.IS_SUCCESS:
            print("is_ResetToDefault ERROR")
        # Set display mode to DIB
        nRet = ueye.is_SetDisplayMode(self.hCam, ueye.IS_SET_DM_DIB)
        m_nColorMode = ueye.IS_CM_MONO8
        self.nBitsPerPixel = ueye.INT(8)
        self.bytes_per_pixel = int(self.nBitsPerPixel / 8)
        print("IS_COLORMODE_MONOCHROME: ", )
        print("\tm_nColorMode: \t\t", m_nColorMode)
        print("\tself.nBitsPerPixel: \t\t", self.nBitsPerPixel)
        print("\tself.bytes_per_pixel: \t\t", self.bytes_per_pixel)
        nRet = ueye.is_AOI(self.hCam, ueye.IS_AOI_IMAGE_GET_AOI, rectAOI, ueye.sizeof(rectAOI))
        if nRet != ueye.IS_SUCCESS:
            print("is_AOI ERROR")
        self.width = rectAOI.s32Width
        self.height = rectAOI.s32Height
        # Prints out some information about the camera and the sensor
        print("Camera model:\t\t", sInfo.strSensorName.decode('utf-8'))
        print("Maximum image self.width:\t", self.width)
        print("Maximum image self.height:\t", self.height)
        # Allocates an image memory for an image having its dimensions defined by self.width and self.height and its color depth defined by self.nBitsPerPixel
        nRet = ueye.is_AllocImageMem(self.hCam, self.width, self.height, self.nBitsPerPixel, self.pcImageMemory, self.MemID)
        if nRet != ueye.IS_SUCCESS:
            print("is_AllocImageMem ERROR")
        else:
            # Makes the specified image memory the active memory
            nRet = ueye.is_SetImageMem(self.hCam, self.pcImageMemory, self.MemID)
            if nRet != ueye.IS_SUCCESS:
                print("is_SetImageMem ERROR")
            else:
                # Set the desired color mode
                nRet = ueye.is_SetColorMode(self.hCam, m_nColorMode)


    def setup(self, integration, roi):
        self.integration = integration
        # set roi and bin here somehow
        self.roi = roi
        # apply to camera roi
        # haha keine roi so far

        nRet = ueye.is_SetHardwareGamma(
            self.hCam,
            ueye.IS_SET_HW_GAMMA_OFF)
        print('set gamma')
        print(nRet)

        nRet = ueye.is_SetGainBoost(
            self.hCam,
            ueye.IS_SET_GAINBOOST_OFF)
        print('set gain boost')
        print(nRet)

        nRet = ueye.is_SetHardwareGain(
            self.hCam,
            ueye.IS_GET_MASTER_GAIN,
            ueye.IS_IGNORE_PARAMETER,
            ueye.IS_IGNORE_PARAMETER,
            ueye.IS_IGNORE_PARAMETER)
        print('set gain')
        print(nRet)

        pc = ueye.int()
        fr = ueye.double()
        nRet = ueye.is_SetOptimalCameraTiming(
            self.hCam,
            ueye.IS_BEST_PCLK_RUN_ONCE,
            4000,
            pc,
            fr)
        print('set optimal')
        print(nRet)
        print(pc)
        print(fr)

        nRet = ueye.is_PixelClock(
            self.hCam,
            ueye.IS_PIXELCLOCK_CMD_SET,
            pc,
            ueye.sizeof(pc))
        print('set pixel clock returned')
        print(nRet)

        # put highest possible frame rate
        if fr < 1/(integration/1000):
            param = ueye.double()
            nRet = ueye.is_SetFrameRate(
                self.hCam, fr, param)
            print('set frame rate return')
            print(nRet)
            print(param)

        if fr >= 1/(integration/1000):
            param = ueye.double()
            nRet = ueye.is_SetFrameRate(
                self.hCam, 1/(integration/1000)-0.1, param)
            print('set frame rate return')
            print(nRet)
            print(param)

        param = ueye.double(integration)
        nRet = ueye.is_Exposure(
            self.hCam,
            ueye.IS_EXPOSURE_CMD_SET_EXPOSURE,
            param,
            ueye.sizeof(param))
        print('set exposure returned')
        print(nRet)
        print(param)

        param = ueye.double()
        nRet = ueye.is_Exposure(
            self.hCam,
            ueye.IS_EXPOSURE_CMD_GET_EXPOSURE,
            param,
            ueye.sizeof(param))
        print('get exposure returned')
        print(nRet)
        print(param)

    def frame(self, stop_event=Event(), inp=None, init_output=None):
        while not ueye.IS_SUCCESS == ueye.is_FreezeVideo(self.hCam, 10000):
            pass 
        while not ueye.IS_SUCCESS == ueye.is_InquireImageMem(self.hCam, self.pcImageMemory, self.MemID, self.width, self.height, self.nBitsPerPixel, self.pitch):
            pass
        array = ueye.get_data(self.pcImageMemory, self.width, self.height, self.nBitsPerPixel, self.pitch, copy=False)
        # frame = np.reshape(array,(self.height.value, self.width.value, self.bytes_per_pixel))  # this is for color
        frame = np.reshape(array,(self.height.value, self.width.value))  # this is for color
        return {
            'x': np.linspace(0, 1, self.width.value),
            'y': np.linspace(0, 1, self.height.value),
            'intensity': frame.copy(),
            'source': 'ueye_camera',
            'success': True}

    def stop(self):
        print('stop ueye camera')
        ueye.is_StopLiveVideo(self.hCam, 5)

    def close(self):
        print('closing ueye camera')
        ueye.is_FreeImageMem(self.hCam, self.pcImageMemory, self.MemID)
        ueye.is_ExitCamera(self.hCam)

