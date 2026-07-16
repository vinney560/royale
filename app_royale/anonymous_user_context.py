# anonymous_user_context.py
import uuid

def anonymous_user(request):
    """Add anonymous user data to all templates."""
    if not request.session.get('anonymous_user'):
        random_suffix = str(uuid.uuid4())[:8]
        request.session['anonymous_user'] = {
            'username': f'Guest_{random_suffix}',
            'id': str(uuid.uuid4()),
            'is_authenticated': False
        }
        request.session.modified = True
    
    return {
        'anonymous_user': request.session.get('anonymous_user'),
        'is_guest': True,
    }