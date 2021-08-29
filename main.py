import os
from flask import Flask, flash, request, redirect, render_template, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import model_final as mdl
import model_final_brandless as mdl_b
import db
from pprint import pprint

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def upload_form():
	return render_template('Mj.html')

@app.route('/result', methods = ['POST']) 
def result(): 
    if request.method == 'POST': 
        brand=(request.form.get('brand'))
        hd=(request.form.get('hd'))
        rating=int(request.form.get('rating'))
        usb=int(request.form.get('usb'))
        size=int(request.form.get('size'))
        hdmi=int(request.form.get('hdmi'))
        speaker=int(request.form.get('speaker'))

        result = model_final.output(brand,rating,speaker,size,hd,hdmi,usb) 
        tv1, tv2, tv3 = db.output(speaker, size, hd, hdmi, usb)
        return render_template("result.html", prediction=result, tv1=tv1 ,tv2=tv2 ,tv3=tv3)

@app.route('/api/menu', methods = ['GET'])
def menu():
    return jsonify(db.menu_options())

@app.route('/api/predict', methods = ['POST'])
def predict():
    pred_with_brand = mdl.pred_with_brand(**request.json)
    pred_without_brand = mdl_b.pred_without_brand(**request.json)
    
    user_pick = db.get_user_pick(**pred_with_brand)
    user_pick["prediction"] = pred_with_brand["cost"]
    user_pick["showPredictedPrice"] = True

    (recommendation, more) = db.get_optimum_pick(**pred_without_brand)
    recommendation["prediction"] = pred_without_brand["cost"]
    recommendation["showPredictedPrice"] = True
    for x in more:
        x["prediction"] = pred_without_brand["cost"]
        x["showPredictedPrice"] = True

    return jsonify({"user_pick": user_pick, "recommendation": recommendation, "more": more})


if __name__ == "__main__":
    app.run(host=os.getenv('HOST'), port=os.getenv('PORT'))
