from flask import (
    Flask,
    request,
    render_template,
    send_from_directory,
    url_for,
    jsonify
)
from werkzeug import secure_filename
import os
from pymongo import MongoClient


# --------------------Bio Packages--------------------
from Bio import BioInfo
import bioscore as bs
# -----------------Social packages-----------------------
import fb_final as fb
import gmailparser as gp
import social_score as ss

# ---------------------Financial -------------------------
from Bank_final import Bank
from payslip import PaySlip
from bank_basic import BankInfo
from bankscore import BankScore


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)


@app.route('/Bio', methods=['POST'])
def bio():
    try:
        if request.method == 'POST':
            data = request.get_json()
            uid = data["UserID"]
            uri = "mongodb://atlmongo:KcNrtLOiTlz3J7UEgzUl978r3GK8ycJu9d3iPYnQ0yr4hYwpQwVatiFOt6NYJurpq4Q4Odmdl0AcSSo6vYkftw==@atlmongo.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
            client = MongoClient(uri)
            db = client.LOBOT
            doc = db.BorrowerInfo.find_one({"UserID": uid})
            front = doc["front"]
            right = doc['right']
            bio_res = BioInfo(front, right)
            response = bio_res.main()
            # print(response)
            d3 = {"UserID": uid}
            d4 = {"Score": bs.b_score(response)}
            # print(d4)
            response_b = reduce(lambda x, y: dict(x, **y), (response, d3, d4))
            db.Bio.insert_one(response_b)
            print(response_b)
            return jsonify("Success")
    except ImportError:
        d6 = {"UserID": uid}
        response1 = "Too many Faces Found or No Face Found !! "
        err = {'Error': response1}
        response_err = reduce(lambda x, y: dict(x, **y), (err, d6))
        db.Bio.insert_one(response_err)
        return jsonify(response1)
    except:
        d7 = {"UserID": uid}
        response2 = "Unable to read image!!"
        err1 = {'Error': response2}
        response_err1 = reduce(lambda x, y: dict(x, **y), (err1, d7))
        db.Bio.insert_one(response_err1)
        return jsonify(response2)


@app.route('/Social', methods=['POST'])
def social():
    try:
        tokens = request.get_json()
        uid = tokens["UserID"]
        g_token = tokens["GmailToken"]
        fb_token = tokens["FBToken"]
        uri = "mongodb://atlmongo:KcNrtLOiTlz3J7UEgzUl978r3GK8ycJu9d3iPYnQ0yr4hYwpQwVatiFOt6NYJurpq4Q4Odmdl0AcSSo6vYkftw==@atlmongo.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
        client = MongoClient(uri)
        db = client.LOBOT
        # db.BorrowerInfo.find_one_and_update({"UserID": uid}, {'$set': {"g_token": g_token, "fb_token": fb_token}})
        doc = db.BorrowerInfo.find_one({"UserID": uid})
        email = doc["EmailID"]
        mar_status = doc["MaritalStatus"]
        edu = doc["HighestQualification"]
        loc = doc["PresentLocation"]
        rmn = doc["MobileNumber"]
        fam_con = doc["FamilyConnections"]
        d3 = {"UserID": uid}
        err = {"Error": "Invalid Token"}
        try:
            response1 = fb.face_book(fb_token)
            d5 = {'Score': ss.fb_score(response1, mar_status, edu, loc, rmn, fam_con)}
            response_a = reduce(lambda x, y: dict(x, **y), (response1, d3, d5))
            db.Facebook.insert_one(response_a)

        except:
            db.Facebook.insert_one(reduce(lambda x, y: dict(x, **y), (d3, err)))
        try:
            response2 = gp.info_mail(email, g_token)
            d4 = {'Score': ss.g_score(response2)}
            response_b = reduce(lambda x, y: dict(x, **y), (response2, d3, d4))
            db.Mail.insert_one(response_b)
        except:
            db.Mail.insert_one(reduce(lambda x, y: dict(x, **y), (d3, err)))

        return jsonify("Success")

    except:
        return jsonify("Error")


@app.route('/Financial', methods=['POST'])
def financial():
    try:
        data = request.get_json()
        uid = data["UserID"]
        uri = "mongodb://atlmongo:KcNrtLOiTlz3J7UEgzUl978r3GK8ycJu9d3iPYnQ0yr4hYwpQwVatiFOt6NYJurpq4Q4Odmdl0AcSSo6vYkftw==@atlmongo.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
        client = MongoClient(uri)
        db = client.LOBOT
        doc = db.BorrowerInfo.find_one({"UserID":uid})
        name = doc["Name"]
        emp_id = doc["EmployeeID"]
        sal = doc["MonthlyIncome"]
        doj = doc["DateOfJoining"]
        file_path = doc["BankStatementPath"]
        pay_fp = doc["PaySlipPath"]
        bank = doc["BankName"]
        branch = doc["BankBranchName"]
        acc_no = doc["AccountNumber"]
        add = doc["Address"]
        sal_date = doc["SalaryDate"]
        d3 = {"UserID": uid}
        try:
            resp = PaySlip(pay_fp,name,emp_id,sal,doj)
            resp3 = resp.main()
            response_p = reduce(lambda x, y: dict(x, **y), (resp3, d3))
            db.Payslip.insert_one(response_p)
            print("Payslip Done")
        except:
            err2 = {"Error": "File Format not supported"}
            resp_err2 = reduce(lambda x, y: dict(x, **y), (err2, d3))
            db.Payslip.insert_one(resp_err2)

        try:
            resp1 = Bank(file_path,bank)
            d1 = resp1.main()
            # print(d1)
            resp2 = BankInfo(file_path,branch,acc_no,add,bank)
            d2 = resp2.main()
            # print(d2)
            resp4 = BankScore(d1, d2, resp3, sal, sal_date)
            d4 = {'Score': resp4.score()}
            # print(d4)
            response_b = reduce(lambda x, y: dict(x, **y), (d1, d2, d3, d4))
            print(response_b)
            db.Bank.insert_one(response_b)
            print("Bank Done")
        except:
            err1 = {'Error': "File Format Error"}
            resp_err1 = reduce(lambda x, y: dict(x, **y), (err1, d3))
            db.Bank.insert_one(resp_err1)
        return jsonify("Success")
    except:
        return jsonify("Error")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
