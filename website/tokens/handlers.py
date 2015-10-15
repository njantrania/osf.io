import httplib as http

from modularodm import Q

from framework.auth.decorators import must_be_logged_in
from framework.exceptions import HTTPError, PermissionsError
from framework import status
from framework.flask import redirect

from website.tokens.exceptions import UnsupportedSanctionHandlerKind, TokenError

def registration_approval_handler(action, registration, registered_from):
    status.push_status_message({
        'approve': 'Your registration approval has been accepted.',
        'reject': 'Your disapproval has been accepted and the registration has been cancelled.',
    }[action], kind='success', trust=False)
    if action == 'approve':
        return redirect(registration.web_url_for('view_project'))
    else:
        return redirect(registered_from.web_url_for('view_project'))

def embargo_handler(action, registration, registered_from):
    status.push_status_message({
        'approve': 'Your embargo approval has been accepted.',
        'reject': 'Your disapproval has been accepted and the embargo has been cancelled.',
    }[action], kind='success', trust=False)
    if action == 'approve':
        return redirect(registration.web_url_for('view_project'))
    else:
        return redirect(registered_from.web_url_for('view_project'))

def retraction_handler(action, registration, registered_from):
    status.push_status_message({
        'approve': 'Your retraction approval has been accepted.',
        'reject': 'Your disapproval has been accepted and the retraction has been cancelled.'
    }[action], kind='success', trust=False)
    if action == 'approve':
        return redirect(registered_from.web_url_for('view_project'))
    elif action == 'reject':
        return redirect(registration.web_url_for('view_project'))

@must_be_logged_in
def sanction_handler(kind, action, payload, encoded_token, auth, **kwargs):
    from website.models import Node, RegistrationApproval, Embargo, Retraction

    Model = {
        'registration': RegistrationApproval,
        'embargo': Embargo,
        'retraction': Retraction
    }.get(kind, None)
    if not Model:
        raise UnsupportedSanctionHandlerKind

    sanction_id = payload.get('sanction_id', None)
    sanction = Model.load(sanction_id)

    err_code = None
    err_message = None
    if not sanction:
        err_code = http.BAD_REQUEST
        err_message = 'There is no {0} associated with this token.'.format(Model.DISPLAY_NAME)
    elif sanction.is_approved:
        err_code = http.BAD_REQUEST if kind in ['registration', 'embargo'] else http.GONE
        err_message = "This registration is not pending {0}.".format(sanction.DISPLAY_NAME)
    elif sanction.is_rejected:
        err_code = http.GONE if kind in ['registration', 'embargo'] else http.BAD_REQUEST
        err_message = "This registration {0} has been rejected.".format(sanction.DISPLAY_NAME)
    if err_code:
        raise HTTPError(err_code, data=dict(
            message_long=err_message
        ))

    do_action = getattr(sanction, action, None)
    if do_action:
        registration = Node.find_one(Q(sanction.SHORT_NAME, 'eq', sanction))
        registered_from = registration.registered_from
        try:
            do_action(auth.user, encoded_token)
        except TokenError as e:
            raise HTTPError(http.BAD_REQUEST, data={
                'message_short': e.message_short,
                'message_long': e.message_long
            })
        except PermissionsError as e:
            raise HTTPError(http.UNAUTHORIZED, data={
                'message_short': 'Unauthorized access',
                'message_long': e.message
            })
        sanction.save()
        return {
            'registration': registration_approval_handler,
            'embargo': embargo_handler,
            'retraction': retraction_handler,
        }[kind](action, registration, registered_from)
