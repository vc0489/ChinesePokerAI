from PIL import Image

def concat_image_h(img1, img2):
  """Assume same height

  Args:
      img1 (Image): [description]
      img2 (Image): [description]
  
  """
  new_image = Image.new('RGBA', (img1.width + img2.width, img1.height), (255, 255, 255, 0))
  new_image.paste(img1, (0, 0))
  new_image.paste(img2, (img1.width, 0))
  
  return new_image


def concat_images_from_file_list(file_list, output=None):
  base_img = Image.open(file_list[0])
  for fileI in range(1,len(file_list)):
    to_concat_img = Image.open(file_list[fileI])
    base_img = concat_image_h(base_img, to_concat_img)
  
  if output is not None:
    base_img.save(output)
  return base_img