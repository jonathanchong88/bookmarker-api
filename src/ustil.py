import os

def solve(key, val, lis):
    return next((i for i, d in enumerate(lis) if d[key] == val), None)


GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
ROWS_PER_PAGE = 5
basedir = os.path.abspath(os.path.dirname(__file__))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
