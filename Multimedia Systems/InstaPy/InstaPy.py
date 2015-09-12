# -*- coding: utf-8 -*-

# ***********************************
#                                   *
#   Code Written by:                *
#                                   *
#   João Paulo                      *
#   Miguel Oliveira                 *
#                                   *
#   Within Multimedia Systems       *
#                                   *
# ***********************************

import cv2, os, sys, glob, threading
import fnmatch, atexit, platform, numpy
import facebook, tweepy, time, webbrowser
import httplib2

from subprocess import call
from Tkinter import *
from PIL import Image, ImageTk
from tkColorChooser import askcolor
from contextlib import contextmanager

# ***********************************
#   App Core Implementation         *
# ***********************************

def main():
    global lmain, root

    initializeVars()

    root = Tk()
    root.bind('<s>', lambda e: root.quit())
    root.wm_title("InstaPy")
    lmain = Label(root)
    lmain.pack()
    Button(root, text="Take Picture", command=TakePicture).pack(fill=X)
    Button(root, text="Black and White", command=lambda: ClickedButton('GrayScale')).pack(fill=X)
    Button(root, text="On Drugs", command=lambda: ClickedButton('Drugs')).pack(fill=X)
    Button(root, text="Reverse Color or whatever", command=lambda: ClickedButton('ReverseColor')).pack(fill=X)
    Button(root, text="No idea what this does, but it looks cool", command=lambda: ClickedButton('NoIdea')).pack(fill=X)
    Button(root, text="Detect Faces", command=lambda: ClickedButton('DetectFaces')).pack(fill=X)
    Button(root, text="Track Color", command=TrackColor).pack(fill=X)
    Button(root, text="Publish to Twitter", command=prepareTwitter).pack(side=RIGHT, fill=Y)
    Button(root, text="Publish to Facebook", command=prepareFacebook).pack(side=RIGHT, fill=Y)
    Button(root, text="Mask Image", command=lambda: TrackColor(maskArg=1)).pack(side=LEFT, fill=Y)
    Button(root, text="Create Mashup", command=CreateMashup).pack(side=LEFT, fill=Y)
    Button(root, text="Record Video", command=lambda: ClickedButton('Record')).pack(side=LEFT, fill=Y)
    Button(root, text="Open Gallery", command=OpenGallery).pack(fill=Y)

def takeTracker():
    cv2.startWindowThread()
    cv2.namedWindow("InstaPy - InstaPhoto Tracker", 1)
    cv2.setMouseCallback("InstaPy - InstaPhoto Tracker", getPixelRGB)
    img.save('InstaPy Album/InstaPhotoTrack.png')
    image = cv2.imread("InstaPy Album/InstaPhotoTrack.png")
    cv2.imshow("InstaPy - InstaPhoto Tracker", image)

def getPixelRGB(event, x, y, flags, param):
    global coords
    if event == cv2.EVENT_LBUTTONDOWN:
        coords = (x,y)
        im = Image.open('InstaPy Album/InstaPhotoTrack.png')
        pix = im.load()
        coords = (pix[x,y][0], pix[x,y][1], pix[x,y][2])
        cv2.destroyWindow("InstaPy - InstaPhoto Tracker")
        os.remove('InstaPy Album/InstaPhotoTrack.png')

def show_frame():
    global frame, colorPicked, img, upper_bound, lower_bound, mask, lower_boundArray, upper_boundArray, firstTrack
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)

    if clickedGrayScale:
        cv2image = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    elif clickedDrugs:
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    elif clickedTrackColor:
        if firstTrack:
            takeTracker()
            firstTrack = False
        while len(coords) < 3: pass

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        if not colorPicked:
            lower_bound = (coords[0],coords[1],coords[2])
            lower_boundArray = numpy.array((lower_bound[0] - 30, lower_bound[1] - 30, lower_bound[2] - 30))
            upper_boundArray = numpy.array((lower_bound[0] + 30, lower_bound[1] + 30, lower_bound[2] + 30))
            colorPicked = True
            for i, rgb in enumerate(lower_boundArray):
                if rgb < 0:
                    lower_boundArray[i] = 0
            for i, rgb in enumerate(upper_boundArray):
                if rgb > 255:
                    upper_boundArray[i] = 255

        mask = cv2.inRange(hsv, lower_boundArray, upper_boundArray)

        res = cv2.bitwise_and(frame, frame, mask=mask)
        if maskGlobal: cv2image = mask
        else: cv2image = res

    elif  clickedReverseColor:
        cv2image = cv2.cvtColor(frame, cv2.COLOR_RGB2HLS)

    elif clickedNoIdea:
        cv2image = cv2.cvtColor(frame, cv2.COLOR_RGB2YUV)

    elif clickedDetectFaces:

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
            )

        for (x, y, w, h) in faces:
            cv2.rectangle(gray, (x, y), (x+w, y+h), (0, 0, 0), 3)
        cv2image = gray

    else:
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

    if clickedRecord:
        video_writer.write(frame)

    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, show_frame)

def byeHandler():
    if platform.system() == 'Linux':
        os.system('clear')
    else:
        os.system('cls')
    print "Obrigado por usares o InstaPy. Ate a proxima :)\n\n"

def initializeVars():
    global clickedDetectFaces, clickedReverseColor, clickedNoIdea, clickedGrayScale, clickedTrackColor
    global clickedDrugs, colorPicked, clickedRecord, nPhotos, database, mashupPressed
    global api_twitter, api_facebook, firstTrack, coords, firstTrack
    global lower_boundArray, upper_boundArray, faceCascade
    global cap, fourcc, video_writer

    cap = cv2.VideoCapture(0)
    fourcc = cv2.cv.CV_FOURCC('M', 'J', 'P', 'G')
    if platform.system() == 'Linux':
        video_writer = cv2.VideoWriter("InstaPy Album/output.avi", fourcc, 10, (640,480))
    else:
        video_writer = cv2.VideoWriter("InstaPy Album/output.avi", fourcc, 25, (640,480))
    faceCascade = cv2.CascadeClassifier('lbpcascade_frontalface.xml')

    clickedRecord = False
    clickedDetectFaces = False
    clickedReverseColor = False
    clickedNoIdea = False
    colorPicked = False
    clickedTrackColor = False
    clickedDrugs = False
    clickedGrayScale = False

    database = None
    api_twitter = None
    api_facebook = None
    mashupPressed = False
    firstTrack = True
    coords = ()
    lower_boundArray = (0,0,0)
    upper_boundArray = (0,0,0)

    try:
        _, _, files = os.walk("InstaPy Album").next()
        nPhotos =  len(files) + 1
        if os.path.isfile("InstaPy Album/output.avi"): nPhotos -= 1
        if os.path.isfile("InstaPy Album/mashup.png"): nPhotos -= 1
        if os.path.isfile("InstaPy Album/InstaPhotoTrack.png"): nPhotos -= 1
    except:
        os.mkdir("InstaPy Album")
        nPhotos = 1

def TakePicture():
    global nPhotos, mashupPressed
    mashupPressed = False
    cv2.startWindowThread()
    cv2.namedWindow("InstaPy - InstaPhoto " + str(nPhotos) ,1)
    img.save('InstaPy Album/InstaPhoto' + str(nPhotos) + '.png')
    image = cv2.imread("InstaPy Album/InstaPhoto" + str(nPhotos) + ".png")
    cv2.imshow("InstaPy - InstaPhoto " + str(nPhotos), image)
    nPhotos += 1

def RemoveAll():
    codes = ['GrayScale', 'Drugs', 'TrackColor', 'ReverseColor', 'NoIdea', 'DetectFaces']
    for var in codes:
        globals()['clicked'+var] = False

def ClickedButton(code):
    global clickedDrugs
    global clickedGrayScale
    global clickedDetectFaces
    global clickedNoIdea
    global clickedReverseColor
    global clickedRecord
    global firstTrack
    temp = globals()['clicked'+code]

    RemoveAll()
    globals()['clicked'+code] = temp
    if code == 'GrayScale':
        clickedGrayScale = not clickedGrayScale
    elif code == 'Drugs':
        clickedDrugs = not clickedDrugs
    elif code == 'ReverseColor':
        clickedReverseColor = not clickedReverseColor
    elif code == 'NoIdea':
        clickedNoIdea = not clickedNoIdea
    elif code == 'DetectFaces':
        clickedDetectFaces = not clickedDetectFaces
    elif code == 'Record':
        clickedRecord = not clickedRecord

    firstTrack = True

def TrackColor(maskArg = 0):
    global maskGlobal
    if maskArg: maskGlobal = 1
    else: maskGlobal = 0
    global clickedTrackColor, colorPicked
    RemoveAll()
    clickedTrackColor = not clickedTrackColor
    colorPicked = not clickedTrackColor

def OpenGallery():
    if platform.system() == 'Linux':
        call(["xdg-open", "InstaPy Album/"])
    else:
        os.startfile("InstaPy Album")

def CreateMashup():
    global mashupPressed
    blank_image = Image.new("RGB", (1290, 970))
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    img = Image.fromarray(cv2image)
    blank_image.paste(img, (0,0))

    cv2image = cv2.cvtColor(frame, cv2.COLOR_RGB2HLS)
    img = Image.fromarray(cv2image)
    blank_image.paste(img, (650,0))

    cv2image = cv2.cvtColor(frame, cv2.COLOR_RGB2YUV)
    img = Image.fromarray(cv2image)
    blank_image.paste(img, (0,490))

    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    img = Image.fromarray(cv2image)
    blank_image.paste(img, (650,490))

    blank_image.save("InstaPy Album/mashup.png")
    mashupPressed = True

    cv2.startWindowThread()
    cv2.namedWindow("Mashup",1)
    image = cv2.imread("InstaPy Album/mashup.png")
    image = cv2.resize(image, (0,0), fx=0.70, fy=0.70)
    cv2.imshow("Mashup", image)

# ***********************************
#   Twitter Implementation          *
# ***********************************

def prepareTwitter():
    if api_twitter == None:
        get_token_twitter = threading.Thread(name='Tokenizer Twitter',target=tokenizerTwitter)
        get_token_twitter.start()

    publisher_twitter = threading.Thread(name='Publisher Twitter', target=publishTwitter)
    publisher_twitter.start()

def tokenizerTwitter():
    global api_twitter

    savout = os.dup(1)
    os.close(1)
    os.open(os.devnull, os.O_RDWR)
    try:
        auth = tweepy.OAuthHandler("0JGivl48mYqCyx7xHJeUkvZ9x",  "aLxMpdwfM57743jfUkN9OtuqVqiJEmJ941BVuwrzY2MjmcGCft")
        try:
            url = auth.get_authorization_url()
        except tweepy.TweepError:
            print 'Error! Failed to get request token.'
        webbrowser.open(url, new = 2)
    finally:
        os.dup2(savout, 1)

    time.sleep(1)

    verifier = raw_input('Codigo de Segurança:')
    raw_input()

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print 'Error! Failed to get access token.'

    api_twitter = tweepy.API(auth)

def publishTwitter():
    while api_twitter == None:
        pass

    if(mashupPressed):
        postImg = r'InstaPy Album/mashup.png'
    else:
        postImg = r'InstaPy Album/InstaPhoto' + str(nPhotos-1) + '.png'

    postStr = raw_input('Introduz o comentario da foto:\n')

    api_twitter.update_with_media(postImg, postStr)

    print "Publicado com Sucesso!"

# ***********************************
#   Facebook Implementation         *
# ***********************************

def prepareFacebook():
    if database == None:
        get_token_facebook = threading.Thread(name='Tokenizer',target=tokenizer)
        get_token_facebook.start()

    publisher_facebook = threading.Thread(name='Publisher', target=publish)
    publisher_facebook.start()

def publish():
    while api_facebook == None :
        pass

    if mashupPressed:
        postImg = open("InstaPy Album/mashup.png", "rb")
    else:
        postImg = open("InstaPy Album/InstaPhoto" + str(nPhotos-1) + ".png", "rb")

    postStr = raw_input('Introduz o comentario da foto:\n')
    postAlbum = raw_input('Prentendes criar um album novo ou adicionar a foto a algum album existente? Basta digitares o nome que prentendes!\n')

    api_facebook.put_photo(postImg, postStr, postAlbum)
    print "Publicado com Sucesso!"

    time.sleep(3)

    if platform.system() == 'Linux':
        os.system('clear')
    else:
        os.system('cls')

def tokenizer():
    global database, api_facebook

    if platform.system() == 'Linux':
        os.system('clear')
    else:
        os.system('cls')

    FACEBOOK_APP_ID = '434307210079524'
    FACEBOOK_APP_SECRET = '66626b9412558a9d545cb23d37dffe12'
    REDIRECT_URI = 'https://www.fc.up.pt/pessoas/up201306220/'

    url = "https://www.facebook.com/dialog/oauth?client_id=" + FACEBOOK_APP_ID + "&redirect_uri=" + REDIRECT_URI

    savout = os.dup(1)
    os.close(1)
    os.open(os.devnull, os.O_RDWR)
    try:
        webbrowser.open(url, new = 2)
    finally:
        os.dup2(savout, 1)

    database = raw_input('Cola aqui o link que te foi fornecido no site: ')
    raw_input()

    token = database.split("=")[1].split("#")[0]

    resp = httplib2.Http().request("https://graph.facebook.com/v2.3/oauth/access_token?client_id="+ FACEBOOK_APP_ID + "&redirect_uri=" + REDIRECT_URI + "&client_secret=" + FACEBOOK_APP_SECRET + "&code=" + token)

    access_token = resp[1].split('":"')[1].split('"')[0]
    api_facebook = facebook.GraphAPI(access_token)

# ***********************************
#   Applications Initial Calls      *
# ***********************************

main()
show_frame()
root.mainloop()
cap.release()
video_writer.release()
cv2.destroyAllWindows()
atexit.register(byeHandler)
