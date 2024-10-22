from http import HTTPStatus
from secrets import token_urlsafe

from flask import current_app, jsonify, request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session
from werkzeug.exceptions import BadRequest

from app.configs.auth import auth
from app.models.admin_model import AdminModel
from app.services.register_login_service import validate_request
from app.services.user_admin_service import check_request_update


def signup():
    try:
        session: Session = current_app.db.session

        admin_data = request.get_json()

        validate_data = validate_request(admin_data)

        validate_data['adm_key'] = token_urlsafe(16)

        password_to_hash = validate_data.pop("password")

        new_admin = AdminModel(**validate_data)

        new_admin.password = password_to_hash


        session.add(new_admin)
        session.commit()

        return jsonify(new_admin), HTTPStatus.CREATED

    except BadRequest as error:
        return error.description, error.code

    except IntegrityError:
        return {"error": "Admin already exists"}, HTTPStatus.CONFLICT

def signin():
    try:
        admin_data =  request.get_json()

        validate_login = validate_request(admin_data, type_login=True)
        
        admin: AdminModel = AdminModel.query.filter_by(email = validate_login['email']).first()

        if not admin:
            return {"error": "email not found"}, HTTPStatus.UNAUTHORIZED
        
        if not admin.verify_password(validate_login['password']):
            return {"error": "email and password missmatch"}, HTTPStatus.UNAUTHORIZED

    except BadRequest as error:
        return error.description, error.code

    return jsonify({"admin_key": admin.adm_key}), HTTPStatus.OK


@auth.login_required
def get_all_admin():   
    admins: AdminModel = AdminModel.query.all()
    return jsonify(admins), HTTPStatus.OK
    

@auth.login_required
def delete_admin():
    session = current_app.db.session
    admin = auth.current_user()
    
    session.delete(admin)
    session.commit()

    return {"msg": f"Admin {admin.name} has been deleted."}, HTTPStatus.OK

@auth.login_required
def update_admin(): 
    try:
        session = current_app.db.session
        data = request.get_json()
        admin = auth.current_user()
        
        valid_request = check_request_update(data)
        
        for key, value in valid_request.items():
            setattr(admin, key, value)

        session.add(admin)
        session.commit()

        return jsonify(admin), HTTPStatus.OK

    except BadRequest as e:
        return e.description, e.code
    except IntegrityError:
        return {"error": "Admin already exists"}, HTTPStatus.CONFLICT