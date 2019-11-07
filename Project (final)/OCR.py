from PIL import Image, ImageDraw, ImageFont
import Info
def Open_Test_Src():
    return Image.open('./Test_Picture/Test.png')
def Open_Src():
    return Image.open('./Picture_Src/Src2.jpg')
def Open_Src_B():
    return Image.open('./Picture_Src/Src4.jpg')
def Open_Example():
    return Image.open('./HTML/0.jpg')
def Save_Img(Img):
    Img.save('./Result_Pic/Res.png')

def Add_Chinese_Font(Img,x,y,ChineseCode,Size):
    font = ImageFont.truetype("./Fonts/simsun.ttc", Size)
    draw = ImageDraw.Draw(Img)
    text = chr(ChineseCode)
    draw.text((x,y), text, font=font, fill=(255,255,255,0))
    return Img
def Add_English_Font(Img,ImgB,x,y,EnglishStr,Size,x0):
    font = ImageFont.truetype("./Fonts/simsunb.ttf",Size)#/usr/share/fonts/truetype/ubuntu/Ubuntu-L.ttf", Size)
    if x0<400:
        Image = Img.copy()
    else:
        Image = ImgB.copy()
    draw = ImageDraw.Draw(Image)
    text = EnglishStr
    draw.text((x,y), text, font=font, fill=(255,255,255,0))
    return Image
def Paste_Picture(Base_Pic,Pic,Base_X,Base_Y,x,y):
    Box=(Base_X,Base_Y,Base_X+x,Base_Y+y)
    Res=Base_Pic.copy()
    Res.paste(Pic,Box)
    return Res
def Mass_Paste_Fonts(EnglishStr,SingleSize,Img,ImgB,Base_Pic,Base_X,Base_Y,x,y,Step):
    Length=len(EnglishStr)
    Cnt=0
    Pic=0
    x0=Base_X
    Posx=2
    Posy=2
    if Length>2:
        while Cnt+2<=Length:
            Pic=Add_English_Font(Img,ImgB,Posx,Posy,EnglishStr[Cnt:Cnt+2],SingleSize,x0)
            Base_Pic=Paste_Picture(Base_Pic, Pic, x0, Base_Y, x, y)
            x0=x0+Step
            Cnt=Cnt+2
        if Cnt+1==Length:
            Pic = Add_English_Font(Img,ImgB, Posx, Posy, EnglishStr[Cnt:]+" ", SingleSize,x0)
            Base_Pic = Paste_Picture(Base_Pic, Pic, x0, Base_Y, x, y)
    else:
        Pic = Add_English_Font(Img, ImgB,Posx, Posy, EnglishStr, SingleSize,x0)
        Base_Pic = Paste_Picture(Base_Pic, Pic, x0, Base_Y, x, y)
    return Base_Pic
if '__main__' == __name__:
    Batch_Size_X = 30
    Batch_Size_Y = 30
    Img=Open_Src()
    Img=Img.resize((Batch_Size_X, Batch_Size_Y),Image.ANTIALIAS)
    ImgB=Open_Src_B()
    ImgB = ImgB.resize((Batch_Size_X, Batch_Size_Y), Image.ANTIALIAS)
    Src=Open_Example()
    Test = Info.Get_Image()
    Client = Info.Create_Client()
    Left, top, width, height, Num, Reswords, TransWords = Info.Recognize_Word(Test, Client)

    Cnt=1
    print(Num)
    if Num>0:
        Size = 30#3*height[0]/4
        Image1 = Mass_Paste_Fonts(TransWords[0], int(Size), Img, ImgB, Src, Left[0], top[0] + 3, Batch_Size_X, Batch_Size_Y, 30)
        #Image1.show()
        while Cnt<Num:
            Size = 30#3*height[Cnt]/4
            Image1 = Mass_Paste_Fonts(TransWords[Cnt], int(Size), Img,ImgB,Image1, Left[Cnt], top[Cnt] + 3, Batch_Size_X, Batch_Size_Y, 30)
            Cnt=Cnt+1
    #Image1.show()
    Image1.save("./Result_Pic/Res.png")
