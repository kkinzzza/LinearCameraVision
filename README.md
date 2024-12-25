# Linear Camera Vision Soft
## Introduction

This repo includes a code for linear camera connection and camera image processing.

With using this code you can provide stable continuous connectivity between PC and camera to get "line" images and then stitch them to one image or video sequence.

After getting final image or video (even in real-time mode) you can analyse the result with OpenCV filtering or other ways to detect different objects / kinds of objects and work with them in the way you want.

## Installation

Download repo and install the dependencies using the following commands:

```
git clone https://github.com/kkinzzza/LinearCameraVision.git
cd LinearCameraVision/
pip install -r requirements.txt 
```

## Structure

- File `cam_library.py` is the library file connected with Dynamic Link Library (if you use Windows);
- File `info.py` includes function for getting camera info;
- File `type_definition.py` is the file with camera status codes and their definitions;
- File `img_processing.py` can be used for shots' editing and filtering (can be edited due to your wishes);
- File `grabber.py` is the main file which provides communication with camera and forming result frame.

## Code Usage

After installation run the file `grabber.py` for getting shots:

```
python grabber.py
```

This file's work is continuing until the *Space* button hasn't pushed. When you push it, the result image will be saved into the directory and the shape of final image will be printed in console. You also can change it to forming and saving video capture if you want.

After saving the result as an image you can run *processing file*:

```
python img_processing.py
```

If you're saving the result as a video, edit `img_processing.py` file due to video reading and editing or import it to *grabber* file for using defined functions during grabbing:

```
from img_processing import *
```

## Current Results

The object, chocolate bar, which was tried to grab:

![photo_2024-11-14 02 16 41](https://github.com/user-attachments/assets/4bc4588c-6d97-436c-9c2e-e883af278094)

By empirical selection of exposure parameters this result was got after grabbing:

![result (1)](https://github.com/user-attachments/assets/163a3747-369e-4d29-87e5-5b82969645b4)

In the result image center we can see the object similar to the chocolate bar accurate to the final form.

## Multiprocessing Usage

The file `grabber_multi_test.py` is a zero version of code for grabbing using multiprocessing. The idea is that the 1st Process is getting frames from linear camera and putting them to the queue (only frame or in format `dict({frame_id: frame})` – as you wish), and 2nd Process is uploading frames from the queue and concatenate them with previous ones at the same time.

This method will allow to get up to 1200 fps from linear camera with exposure settings for enough bright image, which will be enough to make images of fast-moving objects.

The result of zero version code is below:

![test_result](https://github.com/user-attachments/assets/8bc34766-bc29-49df-8d77-4a8578ab1588)

