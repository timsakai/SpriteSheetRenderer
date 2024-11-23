from PIL import Image
import sys

def combine_images(image_paths, output_path):
    images = [Image.open(x) for x in image_paths]
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)
    new_im = Image.new('RGBA', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    new_im.save(output_path)

if __name__ == '__main__':
    image_paths = sys.argv[1:-1]  # 最初と最後の引数を除くすべての引数が画像パス
    output_path = sys.argv[-1]  # 最後の引数が出力パス
    combine_images(image_paths, output_path)
    print(image_paths)