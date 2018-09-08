
# (request.args, msgs_func, user) -> (msgs, offset, next_page, prev_page)
def compute_pages(args, msgs_func, user):
    try:
        offset = int(args.get("p", 0))
    except:
        offset = 0
    if offset < 0:
        offset = 0
    msgs = msgs_func(user, limit = 25 + 1, offset = offset)
    next_page, prev_page = None, None
    if offset > 0:
        prev_page = max(0, offset - 25)
    if len(msgs) > 25:
        next_page = offset + 25
    msgs = msgs[:25]
    return msgs, offset, next_page, prev_page
