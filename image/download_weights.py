import transformers
from transformers import AutoImageProcessor, AutoModelForObjectDetection

# import bentoml
#
# model_name = "Kaludi/food-category-classification-v2.0"
model_name = "hustvl/yolos-tiny"
# task = "classification"
# processor = transformers.AutoProcessor.from_pretrained(model_name)
processor = AutoImageProcessor.from_pretrained(model_name)
# model = transformers.AutoModelForImageClassification.from_pretrained(model_name)
model = AutoModelForObjectDetection.from_pretrained(model_name)
#
# with bentoml.models.create(
#         name=model_name.split('/')[-1],  # Name of the model in the Model Store
# ) as model_ref:
#     # model_ref.pack("processor", processor)
#     # model_ref.pack("model", model)
#     # model_ref.save('/opt/model')
processor.save_pretrained('/opt/model')
model.save_pretrained('/opt/model')
print("Downloaded weights successfully")
