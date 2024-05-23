from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf
from PIL import Image
from pymongo import MongoClient

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection setup
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["cropcare"]
disease_collection = db["3diffcrops"]

# Load the model using TFSMLayer and wrap it in a tf.keras.Model
MODEL = tf.keras.models.load_model("./Versions/3diff.keras")


CLASS_NAMES = ['Aphids_C',
 'Fungi_P',
 'Healthy_P',
 'Phytopthora_P',
 'Powdery Mildew_C',
 'Target spot_C',
 'Target_Spot_T',
 'Tomato_mosaic_virus',
 'healthy_T']

@app.get("/ping")
async def ping():
    return "Hello, I am alive"

def read_file_as_image(data) -> np.ndarray:
    image = np.array(Image.open(BytesIO(data)).rotate(10))
    image = np.array(Image.fromarray(image).resize((256, 256)))
    return image

@app.post("/predict")
async def predict(
    file: UploadFile = File(...)
):
    image = read_file_as_image(await file.read())
    image = image / 255
    img_batch = tf.expand_dims(image, 0)
    
    predictions = MODEL.predict(img_batch)

    predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
    confidence = np.max(predictions[0])

    def get_disease_info(disease_name):
    # Query MongoDB for disease information
        disease_data = disease_collection.find_one({"name": disease_name})
        if disease_data:
            return {
                'CropType': disease_data.get('Crop Type', []),
                'symptoms': disease_data.get('symptoms', []),
                'info': disease_data.get('info', ''),
                'product': disease_data.get('product', '')
            }
        else:
            return {
                'CropType': [],
                'symptoms': [],
                 'info': 'No information available for this disease.'
            }

    # Fetch disease symptoms and related info from MongoDB
    disease_info = get_disease_info(predicted_class)
    return {
        'class': predicted_class,
        'confidence': float(confidence),
        'disease_info': disease_info
    }

    

    

if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)
