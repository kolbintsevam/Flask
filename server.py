from typing import Type
import pydantic
from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from auth import hash_password, check_password
from models import Session, User, Ads
from schema import CreateUser, UpdateUser

app = Flask("app")


class HttpError(Exception):
    def __init__(self, status_code: int, message: str | dict | list):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def error_handler(er: HttpError):
    response = jsonify({"status": "error", "message": er.message})
    response.status_code = er.status_code
    return response


def validate(validation_schema: Type[CreateUser] | Type[UpdateUser], json_data):
    try:
        pydantic_obj = validation_schema(**json_data)
        return pydantic_obj.dict(exclude_none=True)
    except pydantic.ValidationError as er:
        raise HttpError(400, er.errors())


def get_user(session: Session, user_id: int):
    user = session.get(User, user_id)
    if user is None:
        raise HttpError(404, "user not found")
    return user

def get_ads(session: Session, ads_id: int):
    ads = session.get(Ads, ads_id)
    if ads is None:
        raise HttpError(404, "ads not found")
    return ads


class UserViews(MethodView):
    def get(self, user_id: int):
        with Session() as session:
            user = get_user(session, user_id)
            return jsonify(
                {
                    "id": user.id,
                    "name": user.name,
                    "creation_time": user.creation_time.isoformat(),
                }
            )

    def post(self):
        validated_data = validate(CreateUser, request.json)
        validated_data["password"] = hash_password(validated_data["password"])
        with Session() as session:
            new_user = User(**validated_data)
            session.add(new_user)
            try:
                session.commit()
            except IntegrityError as er:
                raise HttpError(409, "user already exist")
            return jsonify({"id": new_user.id})

    def patch(self, user_id):
        validated_data = validate(UpdateUser, request.json)
        if "password" in validated_data:
            validated_data["password"] = hash_password(validated_data["password"])
        with Session() as session:
            user = get_user(session, user_id)
            for field, value in validated_data.items():
                setattr(user, field, value)
            session.add(user)
            try:
                session.commit()
            except IntegrityError as er:
                raise HttpError(409, "user already exist")
            return jsonify({"id": user.id})

    def delete(self, user_id: int):
        with Session() as session:
            user = get_user(session, user_id)
            session.delete(user)
            session.commit()
            return jsonify({"status": "deleted"})


user_view = UserViews.as_view("users")

app.add_url_rule(
    "/user/<int:user_id>", view_func=user_view, methods=["GET", "PATCH", "DELETE"]
)
app.add_url_rule("/user", view_func=user_view, methods=["POST"])


class AdsViews(MethodView):
    def get(self, ads_id: int):
        with Session() as session:
            ads = get_ads(session, ads_id)
            return jsonify(
                {
                    "id": ads.id,
                    "title": ads.title,
                    "description": ads.description,
                    "creation_time": ads.creation_time.isoformat(),
                    "user_id": ads.user_id
                }
            )
    def post(self):
        user_data = request.headers
        ads_data = request.json
        check_pass = hash_password(user_data["password"])
        with Session() as session:
            user = session.query(User).filter(User.name == user_data["name"]).all()
            right_pass = user[0].password
            if user == []:
                raise HttpError(401, "wrong user")
            else:
                if check_password(right_pass, check_pass) is True:
                    ads_data.update({"user_id": user[0].id})
                    new_ads = Ads(**ads_data)
                    session.add(new_ads)
                    session.commit()
                    return jsonify({"id": new_ads.id})
                else:
                    raise HttpError(401, "wrong password")

    def patch(self, ads_id:int):
        user_data = request.headers
        ads_data = request.json
        check_pass = hash_password(user_data["password"])
        with Session() as session:
            user = session.query(User).filter(User.name == user_data["name"]).all()
            right_pass = user[0].password
            if user == []:
                raise HttpError(401, "user not found")
            else:
                if check_password(right_pass, check_pass) is True:
                    ads = get_ads(session, ads_id)
                    if ads.user_id == user[0].id:
                        ads_data.update({"user_id": user[0].id})
                        for field, value in ads_data.items():
                            setattr(ads, field, value)
                            session.add(ads)
                        new_ads = Ads(**ads_data)
                        session.add(new_ads)
                        session.commit()
                        return jsonify({"id": ads.id, "name": ads.title})
                    else:
                        raise HttpError(401, "user has not access")
                else:
                    raise HttpError(401, "wrong password")

    def delete(self, ads_id: int):
        user_data = request.headers
        check_pass = hash_password(user_data["password"])
        with Session() as session:
            user = session.query(User).filter(User.name == user_data["name"]).all()
            right_pass = user[0].password
            if user == []:
                raise HttpError(404, "user not found")
            else:
                if check_password(right_pass, check_pass) is True:
                    ads = get_ads(session, ads_id)
                    if ads.user_id == user[0].id:
                        session.delete(ads)
                        session.commit()
                        return jsonify({"status": "deleted"})
                    else:
                        raise HttpError(401, "user has not access")
                else:
                    raise HttpError(401, "wrong password")

ads_view = AdsViews.as_view("ads")

app.add_url_rule(
    "/ads/<int:ads_id>", view_func=ads_view, methods=["GET", "PATCH", "DELETE"]
)
app.add_url_rule("/ads", view_func=ads_view, methods=["POST"])

if __name__ == "__main__":
    app.run()