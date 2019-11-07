#!/usr/bin/env python
import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

#设置字体，如果没有，也可以不设置
#font = ImageFont.truetype("/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf",13)

#打开底版图片
imageFile = "./HTML/example1.jpg"
im1=Image.open(imageFile)

# 在图片上添加文字 1
draw = ImageDraw.Draw(im1)
draw.text((256,160),"3",(255,255,0))
draw = ImageDraw.Draw(im1)
# 保存
im1.save("target.png")
im1.show()

print("这是一条测试语句","  432", "  256", " 128"," 145")
print("今天天气很不错","  234", "  112", " 276"," 286")

