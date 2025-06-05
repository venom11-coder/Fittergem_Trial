# ready to deploy on backend now!!! 
from flask import Flask
from flask import request
from flask import jsonify
from insightface.app import FaceAnalysis
import cv2
import json

# only imported glob for testing now but remove when deployed it to backend(Railway)



# flutter sends request to us(backend)


# creates a flask server for testing late should be changed to Railway when deployed
app = Flask(__name__)

# loads the model
model = FaceAnalysis()
model.prepare(ctx_id=-1)

# defines a post endpoint and backend is ready to receive the request
@app.route("/predict", methods= ['POST'])

def age_gender_prediction():

# requests image
 image_file=request.files["image"]

 # saves the image locally but should be changed to tmp when deployed into railway
 image_save_path = r"C:\Users\chess\Desktop\Gservices\images\user.jpg"

 # saves the file for the faceanalysis to run and reads it through cv2
 image_file.save(image_save_path)
 img = cv2.imread(image_save_path)




  
  
# gets the image and checks if it exists or not
 face = model.get(img)
 if len(face)==0:
   return jsonify({"no face found!"}),400

# gets the age and gender from the list
 age = int(face[0].age)
 gender = (face[0].gender)

# 0 for female and 1 for male
 if gender==0 :
  gender="female" 
 else : gender = "male"

# dictionary for age and gender
 analysis = {

  "age": age ,
  "gender": gender
 }

# creates json file
 with open("age&gender.json", "w") as json_file:
   json.dump(analysis, json_file, indent=4)

  
 
  
 
   
   # runs 
if __name__ == "__main__":
  app.run(debug=True)