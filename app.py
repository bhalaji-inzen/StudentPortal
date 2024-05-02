from flask import Flask, request, render_template
from flask_restful import Resource, Api, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import json


app=Flask(__name__)
db=SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.sqlite3'
db.init_app(app)
app.app_context().push()
api=Api(app)

class course(db.Model):
    __tablename__='course'
    course_id=db.Column(db.Integer, primary_key=True)
    course_name=db.Column(db.String, nullable=False)
    course_code=db.Column(db.String, unique=True, nullable=False)
    course_description=db.Column(db.String)

class student(db.Model):
    __tablename__='student'
    student_id=db.Column(db.Integer, primary_key=True)
    roll_number=db.Column(db.String, unique=True, nullable=False)
    first_name=db.Column(db.String, nullable=False)
    last_name=db.Column(db.String)

class enrollments(db.Model):
    __tablename__='enrollment'
    enrollment_id=db.Column(db.Integer, primary_key=True)
    student_id=db.Column(db.Integer, db.ForeignKey(student.student_id))
    course_id=db.Column(db.Integer, db.ForeignKey(course.course_id))

db.create_all()

course_fields={
    "course_id": fields.Integer,
    "course_name":fields.String,
    "course_code":fields.String,
    "course_description":fields.String
}
student_fields={
    "student_id":fields.Integer,
    "roll_number":fields.String,
    "first_name":fields.String,
    "last_name":fields.String
}
enrollments_fields={
    "enrollment_id":fields.Integer,
    "student_id":fields.Integer,
    "course_id":fields.Integer
}

class course_api(Resource):
    @marshal_with(course_fields)
    def get(self,course_id=None):
        if course_id ==None:
            all_courses=course.query.all()
            return all_courses, 200
        else:
            course_obj=db.session.query(course).filter(course.course_id == course_id).first()
            if course_obj != None:
                return course_obj, 200
            else:
                return '',404

    @marshal_with(course_fields)
    def put(self,course_id):
        course_upd=course.query.filter(course.course_id == course_id).first()
        course_upd.course_name=request.json["course_name"]
        course_upd.course_code=request.json["course_code"]
        course_upd.course_description=request.json["course_description"]
        db.session.add(course_upd)
        db.session.commit()
        return course_upd, 200

    def delete(self, course_id):
        course_del=course.query.filter(course.course_id == course_id).first()
        db.session.delete(course_del)
        enroll_del=enrollments.query.filter(enrollments.course_id == course_id).all()
        for i in enroll_del:
            db.session.delete(i)
        db.session.commit()
        return {"msg":"Successfully Deleted"}, 200

    @marshal_with(course_fields)
    def post(self):
        course_new=course(course_name=request.json["course_name"], course_code=request.json["course_code"], course_description=request.json["course_description"])
        db.session.add(course_new)
        db.session.commit()
        return course_new, 200
        

class student_api(Resource):
    @marshal_with(student_fields)
    def get(self, student_id=None):
        if student_id == None: 
            students_all=student.query.all()
            return students_all, 200
        else:
            student_obj=student.query.filter(student.student_id == student_id).first()
            print(student_obj)
            if student_obj != None:
                return student_obj, 200
            else:
                return "Not Found", 404

    @marshal_with(student_fields)
    def put(self, student_id):
        student_upd=student.query.filter(student.student_id == student_id).first()
        student_upd.first_name=request.json["first_name"]
        student_upd.last_name=request.json["last_name"]
        student_upd.roll_number=request.json["roll_number"]
        db.session.add(student_upd)
        db.session.commit()
        return student_upd, 200

    def delete(self, student_id):
        student_del=student.query.filter(student.student_id == student_id).first()
        db.session.delete(student_del)
        enroll_del=enrollments.query.filter(enrollments.student_id == student_id).all()
        for i in enroll_del:
            db.session.delete(i)
        db.session.commit()
        return {"msg":"Successfully Deleted"},200

    @marshal_with(student_fields)
    def post(self):
        student_new=student(roll_number=request.json["roll_number"], first_name=request.json["first_name"], last_name=request.json["last_name"])
        db.session.add(student_new)
        db.session.commit()
        return student_new, 200


class enrollments_api(Resource):
    @marshal_with(enrollments_fields)
    def get(self,student_id=None):
        if student_id == None :
            all_stud_enroll=enrollments.query.all()
            return all_stud_enroll, 200
        else:
            stud_enroll=enrollments.query.filter(enrollments.student_id == student_id).all()
            return stud_enroll, 200

    @marshal_with(enrollments_fields)
    def post(self,student_id):
        exist_enroll=enrollments.query.filter(enrollments.student_id == student_id, enrollments.course_id == request.json["course_id"]).first()
        #print(exist_enroll.student_id, exist_enroll.course_id)
        if exist_enroll == None:
            new_enroll=enrollments(student_id= student_id, course_id=request.json["course_id"])
            db.session.add(new_enroll)
            db.session.commit()
            return new_enroll, 200
        else:
            return {},400

    def delete(self, student_id, course_id):
        del_enroll=enrollments.query.filter(enrollments.student_id == student_id, enrollments.course_id == course_id).first()
        db.session.delete(del_enroll)
        db.session.commit()
        return {"msg":"Sucessfully Deleted"}, 200

api.add_resource(course_api,'/api/course','/api/course/<int:course_id>')
api.add_resource(student_api,'/api/student','/api/student/<int:student_id>')
api.add_resource(enrollments_api,'/api/enrolldeets','/api/student/<int:student_id>/course','/api/student/<int:student_id>/course/<int:course_id>')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__" :
    app.run(host='0.0.0.0',port=5000)