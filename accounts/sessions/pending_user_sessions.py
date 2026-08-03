
class PendingUserSession:
    """
    Pending User Session.
    """
    KEY = "pending_user_id"

    @classmethod
    def store(cls, request, user):
        request.session[cls.KEY] = user.id

    @classmethod
    def get_user_id(cls, request):
        user_id = request.session.get(cls.KEY)
        if not user_id:
            return None
        return user_id

    @classmethod
    def clear(cls, request):
        request.session.pop(cls.KEY, None)