import numpy as np
import cv2
import random
import math

# NEED TO ADD THE REST OF THE CARDINAL DIRECTION TRANSFORMATIONS
NORTH = cv2.getRotationMatrix2D((300/2,300/2),0,1)
NORTH_EAST = cv2.getRotationMatrix2D((300/2,300/2),-45,1)
#cardinalDirections = [NORTH,NORTH_EAST,EAST,SOUTH_EAST,SOUTH,SOUTH_WEST,WEST,NORTH_WEST]

def drawRectangle(img):
    # point1 = (int(10*random.random()), int(10*random.random()))
    # point2 = (int(90 + 10*random.random()), int(90 + 10*random.random()))
    # NOTE: POINT: (x,y)
    point1 = (20,20)
    point2 = (280,280)
    white_color = (255,255,255)
    # NOTE: Draws a rectangle
    cv2.rectangle(img, point1, point2, white_color, -1);

def drawCircle(img):
    white_color = (255,255,255)
    cv2.circle(img,(150,150),100,white_color,-1)

def drawSemiCircleConcaveUp(img):
    white_color = (255,255,255)
    center = (150,90)
    axes = (125,125)
    angle=0;
    startAngle=0;
    endAngle=180;
    cv2.ellipse(img,center,axes,angle,startAngle,endAngle, white_color,-1);


def drawSemiCircleConcaveDown(img):
    center = (150,210)
    white_color = (255,255,255)
    axes = (125,125)
    angle = 0
    startAngle = 180
    endAngle = 360
    cv2.ellipse(img,center,axes,angle,startAngle,endAngle,white_color,-1)

def padCharImg(data):
    padded_data = np.zeros((300,300,3),np.uint8)
    padded_data[100:200,100:200,0:3] = data
    return padded_data

def pixelDistFromBlack(pixel1):
    BLACK_RGB = [0,0,0]
    r_diff = (pixel1[0]-BLACK_RGB[0])*(pixel1[0]-BLACK_RGB[0])
    g_diff = (pixel1[1]-BLACK_RGB[1])*(pixel1[1]-BLACK_RGB[1])
    b_diff = (pixel1[2]-BLACK_RGB[2])*(pixel1[2]-BLACK_RGB[2])
    return math.sqrt(r_diff+g_diff+b_diff)

# Function is passed a blank white shape img + a black-on-white alphanum img
# NOTE: this function can pass an img background with black color (which wouldn't contrast with the already black background
#       surrounding the shape)
def colorShapeIMG(img,new_dst):
    WHITE_RGB = [255,255,255]
    # White, Black, Gray, Red, Blue, Green, Yellow, Purple, Brown, Orange
    colors = [(255,255,255),(0,0,0),(128,128,128),(255,0,0),(0,0,255),(0,128,0),(255,255,0),(128,0,128),(131,92,59),(255,165,0)]
    random_background_color = colors[int(random.random()*10)]
    random_alphanum_color = colors[int(random.random()*10)]
    # Makes sure the alpanum color and the background color are different
    while(random_background_color == random_alphanum_color):
        random_alphanum_color = colors[int(random.random()*10)]

    for i in range(0,len(img)):
        for x in range(0,len(img[i])):
            if np.all(img[i][x]==WHITE_RGB):
                if pixelDistFromBlack(new_dst[i][x]) < 200:
                    img[i][x] = random_alphanum_color
                else:
                    img[i][x] = random_background_color
    return img


def overlayChar(data, img):
    WHITE_RGB = [255,255,255]
    # Inverts the color
    data = 255-data;

    num = int(data.shape[0]*random.random())
    # NOTE: OpenCV resize transformation (handwritten character is slighly smaller than the background img)
    dst = cv2.resize(data[num],(100,100),interpolation=cv2.INTER_NEAREST)



    new_dst = (dst, dst, dst)
    new_dst = np.stack(new_dst, axis=2);
    # places the smaller dst character image in a larger dst that matches the background img size, height+width
    new_dst = padCharImg(new_dst)

    # PREVIOUSLY: This is subtracted in order to convert the new_dst white (255,255,255) rgb values to black values (0,0,0)
    # return img-new_dst

    new_dst = 255-new_dst
    # Returns a random background / alphanumeric combination
    img = colorShapeIMG(img,new_dst)
    return img

def genImage(overlay_img):
    big_img = cv2.imread("background.png");
    # Randomly selected top left corner of the new generated image
    top_left = [int(random.random() * 100), int(random.random() * 100)];
    # the bottom right corner
    bottom_right = [top_left[0] + 300, top_left[1] + 300];
    # new random image square is cropped out
    cropped_img = big_img[top_left[0]:bottom_right[0], top_left[1]:bottom_right[1]];


    roi = cropped_img[0:300, 0:300]
    #create mask
    img2gray = cv2.cvtColor(overlay_img,cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)
    img1_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)
    img2_fg = cv2.bitwise_and(overlay_img,overlay_img,mask = mask)
    dst = cv2.add(img1_bg,img2_fg)
    cropped_img[0:300, 0:300] = dst
    return cropped_img;

# Creates the alphanumeric "text" image array
data = np.load("alphanum-hasy-data-X.npy")
#  Creates a black image array (height,width,rgb)
img = np.zeros((300, 300, 3), np.uint8);
# Draws a white shape on the black image
drawSemiCircleConcaveDown(img);
# Overlays the "text" image over the image
dst = overlayChar(data, img);

# APPLIES A CARDINAL ORIENTATION TRANSFORMATION
dst = cv2.warpAffine(img, NORTH_EAST, (300,300))

# Overlays the shape + character image on the background image
dst = genImage(dst);

# APPLIES a gaussian blur effect
gaussian_blur = cv2.GaussianBlur(dst,(15,15),0);

cv2.namedWindow("Test",cv2.WINDOW_NORMAL)
cv2.imshow("Test", gaussian_blur);
cv2.waitKey(0);
