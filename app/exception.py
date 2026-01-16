from rest_framework.exceptions import APIException


class DetailErrorException(APIException):
    default_code = 'error'
    status_code = 400
    default_detail = 'Bad Request'

