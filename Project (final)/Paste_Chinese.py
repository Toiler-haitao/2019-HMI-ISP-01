from PIL import Image, ImageDraw, ImageFont

def Open_Test_Src():
    return Image.open('./Test_Picture/Test.png')
def Open_Src():
    return Image.open('./Picture_Src/Src2.jpg')
def Save_Img(Img):
    Img.save('./Result_Pic/Res.png')

def Add_Font(Img,x,y,ChineseCode,Size,):
    font = ImageFont.truetype("./Fonts/simsun.ttc", Size)
    draw = ImageDraw.Draw(Img)
    text = chr(ChineseCode)
    draw.text((x,y), text, font=font, fill=(255,255,255,0))
    return Img
def Paste_Picture(Base_Pic,Pic,Base_X,Base_Y,x,y):
    Box=(Base_X,Base_Y,Base_X+x,Base_Y+y)
    Base_Pic.paste(Pic,Box)
    return Base_Pic
if '__main__' == __name__:
    Img=Open_Src()
    Img=Img.resize((35, 35),Image.ANTIALIAS)
    Test=Open_Test_Src()
    Res=Add_Font(Img,7,7,0x4E00,30)
    Res=Paste_Picture(Test,Res,305,160,35,35)
    Res.show()