import qrcode
import json
from django.http import HttpResponse, HttpResponseBadRequest
# from django.views.decorators.csrf import csrf_exempt

def generate_qr_code(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("POST method required")
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")
    
    text = data.get('data')
    if not text:
        return HttpResponseBadRequest("Missing 'data' field in JSON")
    
    # Optional parameters
    fill_color = data.get('fill_color', 'black')
    back_color = data.get('back_color', 'white')
    size = data.get('size', 10)
    border = data.get('border', 4)
    
    # Generate QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=size,
        border=border,
    )
    qr.add_data(text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response