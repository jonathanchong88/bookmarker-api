from flask import Blueprint, request, jsonify, url_for, render_template

webprivacy = Blueprint("webprivacy", __name__)


@webprivacy.get('/policy/privacy')
def get_privacy():
    return render_template('privacy.html')

