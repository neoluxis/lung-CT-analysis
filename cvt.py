import importlib.util
import subprocess
import sys


# 检查模块是否已安装
def check_and_install(package, import_name=None):
    spec = importlib.util.find_spec(package if import_name == None else import_name)
    if spec is None:
        print(f"{package} is not installed. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


check_and_install("SimpleITK")
check_and_install("matplotlib")
check_and_install("opencv-python", "cv2")

import SimpleITK as sitk
import matplotlib.pyplot as plt
import argparse
from PIL import Image
import cv2 as cv
import os

# 创建一个 ArgumentParser 对象
parser = argparse.ArgumentParser(
    # description="Read .mhd images, display slices, and save as grayscale JPG."
    description="读取 .mhd 文件, 展示切片, 并转换图像为 JPEG"
)

# 添加参数：-if 和 -od，为-if设置nargs='+'，为-od设置默认值'outputs'
parser.add_argument(
    "-if",
    "--input_files",
    type=str,
    default="",
    nargs="+",
    help="输入的 .mhd 文件, 或者含有 .mhd 文件的文件夹",
)
parser.add_argument(
    "-od",
    "--output_dir",
    type=str,
    default="outputs",
    help="转换出JPEG文件存放的文件夹",
)
parser.add_argument(
    "-sg",
    "--show_gray",
    action="store_true",
    help="以灰阶图像展示图片",
)
parser.add_argument(
    "-sc", "--show_color", action="store_true", help="以彩色模式展示图象"
)
parser.add_argument(
    "-l",
    "--layers",
    type=int,
    default=[100],
    nargs="+",
    help="要转换出的层, -1 表示全部转换",
)

# 解析命令行参数
args = parser.parse_args()

# 确保输出文件夹存在
output_dir = args.output_dir
os.makedirs(output_dir, exist_ok=True)
# os.makedirs(f"{output_dir}/gray", exist_ok=True)


def convert(
    infile: str,
    layers=-1,
    show_gray: bool = False,
    show_color: bool = False,
):
    img = sitk.ReadImage(infile)
    gray = sitk.GetArrayFromImage(img)
    if layers == [-1]:
        layers = [x for x in range(len(gray))]
        print("Convert all layers...")
    for layer in layers:
        if show_gray or show_color:
            plt.figure(1)
            if show_gray:
                plt.imshow(gray[layer, :, :], cmap="gray")
            else:
                plt.imshow(gray[layer, :, :])
            plt.title(os.path.basename(infile))
            plt.show()

        gray_image = Image.fromarray(
            gray[layer, :, :].astype("uint8"), "L"
        )  # 'L' mode for grayscale
        gray_save = os.path.join(output_dir, os.path.basename(infile))
        gray_image.save(gray_save.replace(".mhd", f"_{layer}.jpg"))
        print(f"{infile} export saved as {gray_save.replace('.mhd', f'_{layer}.jpg')}'")


# 遍历所有输入文件
for input_file in args.input_files:
    # 确保输入文件存在
    if not os.path.exists(input_file):
        print(f"{input_file} does not exist.")
        continue

    # 判断是否为文件夹
    if os.path.isdir(input_file):
        for root, _, files in os.walk(input_file):
            for file in files:
                if file.endswith(".mhd"):
                    convert(
                        os.path.join(root, file),
                        layers=args.layers,
                        show_gray=args.show_gray,
                        show_color=args.show_color,
                    )
    else:
        convert(
            input_file,
            layers=args.layers,
            show_gray=args.show_gray,
            show_color=args.show_color,
        )
