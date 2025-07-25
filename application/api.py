from flask_restful import Resource
from application.models import Service, User, ServiceRequest, Coupon
from application.database import db
from datetime import datetime
from flask import request

class ServiceAPI(Resource):
    def delete(self,id):
        service = Service.query.filter_by(id=id).first()
        professionals = User.query.filter_by(service_id=id).all()
        service_requests = ServiceRequest.query.filter_by(service_id=id).all()
        for service_request in service_requests:
            db.session.delete(service_request)
        for professional in professionals:
            db.session.delete(professional)
        db.session.delete(service)
        db.session.commit()
        return {"message": "Service deleted"} , 200
    

class UserAPI(Resource):
    def delete(self,id):
        user = User.query.filter_by(id=id).first()
        if user.role == "professional":
            service_requests = ServiceRequest.query.filter_by(professional_id=id).all()
        elif user.role == "customer":
            service_requests = ServiceRequest.query.filter_by(customer_id=id).all()
        else:
            return {"message": "Cannot delete admin"}, 403
        for service_request in service_requests:
            db.session.delete(service_request)
        
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"} , 200
    
class ProfessionalAPI(Resource):
    def put(self, action, id):
        user = User.query.filter_by(id=id).first()
        if action == "approve":
            data = request.get_json()
            user.service_id = data['service_id']
            user.service_name = data['service_name']
            user.approval_status = "approved"
            message = "User approved"
        elif action == "reject":
            user.approval_status = "rejected"
            message = "User rejected"
        db.session.commit()
        return {"message": message}, 200

class ServiceRequestAPI(Resource):
    def delete(self,id):
        service_request = ServiceRequest.query.filter_by(id=id).first()
        db.session.delete(service_request)
        db.session.commit()
        return {"message": "Service request deleted"} , 200
    
    def put(self, action, request_id):
        service_request = ServiceRequest.query.filter_by(id=request_id).first()
        if action == "accept":
            service_request.status = "assigned"
            message = "Service request assigned"
        elif action == "reject":
            service_request.status = "rejected"
            message = "Service request rejected"
        elif action == "close":
            service_request.status = "closed"
            service_request.date_of_completion = datetime.now().strftime("%d-%m-%y")
            message = "Service request closed"
        db.session.commit()
        return {"message": message}, 200
    
    def post(self, customer_id, service_id , professional_id):
        service_request = ServiceRequest(customer_id=customer_id, service_id=service_id, professional_id=professional_id, status="requested")
        service_request.date_of_request = datetime.now().strftime("%d-%m-%y")
        service_request.professional_name = User.query.filter_by(id=professional_id).first().name
        db.session.add(service_request)
        db.session.commit()
        return {"message": "Service request created"}, 200

class CouponAPI(Resource):
    def delete(self, id):
        coupon = Coupon.query.filter_by(id=id).first()
        db.session.delete(coupon)
        db.session.commit()
        return {"message": "Coupon deleted"} , 200