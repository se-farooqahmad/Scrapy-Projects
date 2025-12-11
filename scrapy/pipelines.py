import os
from scrapy.pipelines.images import ImagesPipeline
from scrapy.spiders import Request

from PIL import Image, TiffImagePlugin
from PIL.ExifTags import TAGS, GPSTAGS

from datetime import datetime
import calendar 

class CustomImagesPipeline(ImagesPipeline):
    pass
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.scraped_names = {}
    
#     def get_media_requests(self, item, info):
#         yield Request(item['img_url'], meta={'item': item})

#     def file_path(self, request, response=None, info=None, *, item=None):
#         # Truncate and format the prompt to create a safe filename
#         creation_date = datetime.strptime(item['Created'], "%m/%d/%Y %I:%M %p")
#         month_name = calendar.month_name[creation_date.month]
#         os.makedirs(os.path.join(self.store.basedir, month_name), exist_ok=True)
        
#         filename = f"{item['image_name']}.tiff"
#         return os.path.join(month_name, filename)

#     def item_completed(self, results, item, info):
#         image_paths = [x['path'] for ok, x in results if ok]
#         if not image_paths:
#             raise DropItem("Image download failed")
#         print(f'IMAGE DOWNLOADED: {image_paths}')

#         # Convert the downloaded image to TIFF format, embed metadata, and save it
#         for image_path in image_paths:
#             full_image_path = os.path.join(self.store.basedir, image_path)
#             with Image.open(full_image_path) as img:
#                 img = img.convert('RGB')  # Ensure it's in the right mode

#                 # Prepare metadata
#                 exif_data = img.info.get("exif", None)
#                 meta = TiffImagePlugin.ImageFileDirectory_v2()

#                 combined_info = f"Seed: {item['Seed']}, Model: {item['Model']}, Prompt Guidance: {item['Prompt Guidance']}, Sampler: {item['Sampler']}, Created: {item['Created']}"  # UserComment
#                 # Standard TIFF tags
#                 meta[270] = item['Prompt']  # ImageDescription
#                 meta[315] = "ezra boucher"  # Artist
#                 meta[33432] = "None"  # Copyright
#                 meta[269] = f"Seed: {item['Seed']}"  # DocumentName
#                 meta[285] = f"Model: {item['Model']}"  # PageName
#                 meta[305] = combined_info  # Software
#                 meta[306] = item['Created']  # DateTime
#                 meta[37510] = combined_info
#                 # EXIF User Comment tag

#                 # Save the image as TIFF with metadata
#                 tiff_path = full_image_path.replace(".jpg", ".tiff").replace(".png", ".tiff")
#                 img.save(tiff_path, format='TIFF', exif=exif_data, tiffinfo=meta)
#                 # os.remove(full_image_path)  # Remove original JPEG or PNG file

#         return item
