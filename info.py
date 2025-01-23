#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports the Adafruit implementation of the
# GPIO ports and SPI protocol. This code has been
# simplified to support the Raspberry Pi only.
# https://github.com/adafruit/Adafruit_Python_GPIO
import GPIO as GPIO
import SPI as SPI

# Imports the implementation of the ST7789 LCD screen with 7 pins.
# https://github.com/solinnovay/Python_ST7789 
import ST7789 as TFT

# Classic Python libraries
import datetime
import sys
import psutil

from time import sleep

from PIL import Image, ImageDraw, ImageFont

# Raspberry Pi pin configuration:
RST = 22
DC  = 17
BLK = 27
SPI_PORT = 0
SPI_DEVICE = 0
SPI_MODE = 0b11
SPI_SPEED_HZ = 40000000

disp = TFT.ST7789(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=SPI_SPEED_HZ), 
       mode=SPI_MODE, rst=RST, dc=DC, led=BLK)

# Initialize display.
disp.begin()

# Clear display.
disp.clear()

# Analogue clock setting
width = 240
height = 240

# font setting
font = ImageFont.load_default()
fontJ = ImageFont.truetype('DejaVuSans.ttf', 24, encoding='unic')

def get_cpu_temp():
    tempFile = open("/sys/class/thermal/thermal_zone0/temp")
    cpu_temp = tempFile.read()
    tempFile.close()
    return round(float(cpu_temp)/1000, 1)

def draw_rotated_text(image, text, position, angle, font, fill=(255, 255, 255)):
    #print position
    position = position[0], position[1]
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    # Bounding box size.
    bbox = draw.textbbox((0, 0), text, font=font)
    width, height = bbox[2] - bbox[0], bbox[3]
    textimage = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0, 0), text, font=font, fill=fill)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)

try:
    last_time = ""
    time = datetime.datetime.now().time().strftime("%H:%M:%S")
    displayValue = 0
    iter = 0
    maxIter = 0
    #read MaxIter from the command line
    if len(sys.argv) == 1:
            print("Usage: python info.py <maxIter>")
            sys.exit(1)  
    if len(sys.argv) > 1:
        try:
            maxIter = int(sys.argv[1])
            if maxIter < 100:
                maxIter = 100
                print("MaxIter was set to 100")
        except:
            print("Usage: python info.py <maxIter>")
            sys.exit(1)

    while 1:
        # Create blank image for drawing.
        image1 = Image.new("RGB", (disp.width, disp.height), "BLACK")
        draw = ImageDraw.Draw(image1)

        while time == last_time:
            sleep(0.1)
            time = datetime.datetime.now().time().strftime("%H:%M:%S")
        last_time = time
        H = int(time[0:2])
        M = int(time[3:5])
        S = int(time[6:8])

        # Digital clock
        draw.rectangle((0, 184, 239, 239), outline=(0, 0, 0), fill=(0, 0, 0))
        now = datetime.datetime.now()
        date = now.date().strftime("%Y/%m/%d")
        time = now.time().strftime("%H:%M:%S")
        draw_rotated_text(image1, date, (200, 0), 270, font=fontJ, fill=(0, 0, 255) )
        draw_rotated_text(image1, time, (170, 0), 270, font=fontJ, fill=(0, 0, 255) )

        # CPU load
        draw_rotated_text(image1, "CPU Load", (130, 0), 270, font=fontJ, fill=(255, 255, 0) )
        cpu = psutil.cpu_percent(interval=1)
        draw_rotated_text(image1, str(cpu) + "%", (130, 150), 270, font=fontJ, fill=(255, 255, 0) )

        # CPU temperature
        draw_rotated_text(image1, "CPU Temp", (104, 0), 270, font=fontJ, fill=(255, 255, 0) )
        temp = get_cpu_temp()
        draw_rotated_text(image1, str(temp) + "°", (108, 150), 270, font=fontJ, fill=(255, 255, 0) )

        # RAM
        ram = psutil.virtual_memory()
        ram_total = round(ram.total / 2**30, 1) # GiB.
        ram_used = round(ram.used / 2**30, 1)
        ram_free = round(ram.free / 2**30, 1)
        ram_percent_used = ram.percent
        # 4 cases based on the displayValue
        if displayValue == 0:
            draw_rotated_text(image1, "RAM (tot.)", (86, 0), 270, font=fontJ, fill=(255, 255, 0) )
            draw_rotated_text(image1, str(ram_total) + " G", (86, 150), 270, font=fontJ, fill=(255, 255, 0) )
        elif displayValue == 1:
            draw_rotated_text(image1, "RAM (use)", (86, 0), 270, font=fontJ, fill=(255, 255, 0) )
            draw_rotated_text(image1, str(ram_used) + " G", (86, 150), 270, font=fontJ, fill=(255, 255, 0) )
        elif displayValue == 2:
            draw_rotated_text(image1, "RAM (free)", (86, 0), 270, font=fontJ, fill=(255, 255, 0) )
            draw_rotated_text(image1, str(ram_free) + " G", (86, 150), 270, font=fontJ, fill=(255, 255, 0) )
        elif displayValue == 3:
            draw_rotated_text(image1, "RAM", (89, 0), 270, font=fontJ, fill=(255, 255, 0) )
            draw_rotated_text(image1, str(ram_percent_used) + "%", (86, 150), 270, font=fontJ, fill=(255, 255, 0) )
        
        # Disk
        disk = psutil.disk_usage('/')
        disk_total = round(disk.total / 2**30, 0)     # GiB.
        disk_used = round(disk.used / 2**30, 0)
        disk_free = round(disk.free / 2**30, 0)
        disk_percent_used = round(disk.percent, 0)
        # 4 cases based on the displayValue
        if displayValue == 0:
            draw_rotated_text(image1, "Disk (tot.)", (64, 0), 270, font=fontJ, fill=(255, 255, 0) )
            draw_rotated_text(image1, str(disk_total) + " G", (64, 150), 270, font=fontJ, fill=(255, 255, 0) )
        elif displayValue == 1:
            draw_rotated_text(image1, "Disk (use)", (64, 0), 270, font=fontJ, fill=(255, 255, 0) )
            draw_rotated_text(image1, str(disk_used) + " G", (64, 150), 270, font=fontJ, fill=(255, 255, 0) )
        elif displayValue == 2:
            draw_rotated_text(image1, "Disk (free)", (64, 0), 270, font=fontJ, fill=(255, 255, 0) )
            draw_rotated_text(image1, str(disk_free) + " G", (64, 150), 270, font=fontJ, fill=(255, 255, 0) )
        elif displayValue == 3:
            draw_rotated_text(image1, "Disk", (67, 0), 270, font=fontJ, fill=(255, 255, 0) )
            draw_rotated_text(image1, str(disk_percent_used) + "%", (64, 150), 270, font=fontJ, fill=(255, 255, 0) )

        disp.display(image1)
        displayValue += 1
        if displayValue > 3:
            displayValue = 0
        
        iter += 1
        if iter > maxIter:
            break

except KeyboardInterrupt:
    pass

finally:
    disp.clear()
    image1 = Image.new("RGB", (disp.width, disp.height), "BLACK")
    draw = ImageDraw.Draw(image1)
    disp.display(image1)

