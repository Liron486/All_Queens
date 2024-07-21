from PIL import Image, ImageEnhance, ImageOps
import numpy as np

def make_creamy_white(image):
    hsv_image = image.convert('HSV')
    h, s, v = hsv_image.split()
    np_s = np.array(s, dtype=np.uint8)
    np_s = np_s * 0.2  # Reduce saturation
    new_s = Image.fromarray(np_s, 'L')
    enhancer = ImageEnhance.Brightness(image)
    bright_image = enhancer.enhance(1.5)
    hsv_bright_image = bright_image.convert('HSV')
    _, _, new_v = hsv_bright_image.split()
    creamy_white_image = Image.merge('HSV', (h, new_s, new_v))
    return creamy_white_image.convert('RGB')

def make_almost_black(image):
    hsv_image = image.convert('HSV')
    h, s, v = hsv_image.split()
    np_s = np.array(s, dtype=np.uint8)
    np_s = np_s * 1.2  # Increase saturation slightly to keep the color richness
    new_s = Image.fromarray(np_s, 'L')
    np_v = np.array(v, dtype=np.uint8)
    np_v = np_v * 0.2  # Significantly reduce brightness
    new_v = Image.fromarray(np_v, 'L')
    almost_black_image = Image.merge('HSV', (h, new_s, new_v)).convert('RGB')
    
    return almost_black_image

def fill_transparent_background(image, fill_color=(0, 255, 0)):
    if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
        alpha = image.convert('RGBA').split()[-1]
        bg = Image.new("RGBA", image.size, fill_color + (255,))
        bg.paste(image, mask=alpha)
        return bg.convert('RGB')
    else:
        return image

def process_image(input_path, output_path, action):
    image = Image.open(input_path)
    image_with_bg = fill_transparent_background(image)

    if action == "white":
        processed_image = make_creamy_white(image_with_bg)
    elif action == "black":
        processed_image = make_almost_black(image_with_bg)
    else:
        raise ValueError("Unsupported action specified. Use 'white' or 'black'.")
    
    processed_image.save(output_path)
    processed_image.show()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process an image to change its color.")
    parser.add_argument("input_path", type=str, help="Path to the input image file")
    parser.add_argument("output_path", type=str, help="Path to save the processed image file")
    parser.add_argument("action", type=str, choices=["white", "black"], help="Desired action to perform on the image")

    args = parser.parse_args()

    process_image(args.input_path, args.output_path, args.action)
