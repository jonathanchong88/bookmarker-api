import os

from itsdangerous import URLSafeTimedSerializer

ts = URLSafeTimedSerializer(os.environ.get("SECRET_KEY"))
