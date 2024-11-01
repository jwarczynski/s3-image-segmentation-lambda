import transformers
from transformers import AutoImageProcessor, AutoModelForObjectDetection

model_name = "hustvl/yolos-tiny"
processor = AutoImageProcessor.from_pretrained(model_name)
model = AutoModelForObjectDetection.from_pretrained(model_name)

processor.save_pretrained('/opt/model')
model.save_pretrained('/opt/model')
