import uuid
import logging

class AssignUniqueSessionCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.session_key:
            logging.debug("Asignando nueva sesión")
            request.session.create()
            request.session['session_id'] = str(uuid.uuid4())
        else:
            logging.debug(f"Sesión existente: {request.session.session_key}")

        response = self.get_response(request)
        return response

class ClearSessionOnNavigateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Limpiar datos de alerta y estado de escaneo QR si la URL no es del formulario de alerta
        if not request.path.startswith('/formulario_alerta/'):
            if 'alerta_data' in request.session:
                del request.session['alerta_data']
            if 'qr_scanned' in request.session:
                del request.session['qr_scanned']

        return response