
MSGS_PER_PAGE = 25

# (request.args, msgs_func, *func_args) -> (msgs, offset, next_page, prev_page)
def compute_pages(args, msgs_func, *func_args):
    try:
        before = max(0, int(args.get("b", None)))
    except:
        before = None
    try:
        after = max(0, int(args.get("a", None)))
    except:
        after = None
    msgs = msgs_func(*func_args, limit = MSGS_PER_PAGE + 1, before = before, after = after)
    next_page, prev_page = None, None
    if before != None or after != None:
        prev_page = msgs[0]["id"]
        # fetch newest possible ID, if equals prev_page set None
        newest = msgs_func(*func_args, limit = 1, before = None, after = None)
        if newest:
            newest_id = newest[0]["id"]
            if newest_id <= prev_page:
                prev_page = None
        else:
            prev_page = None
    if len(msgs) > MSGS_PER_PAGE:
        next_page = msgs[MSGS_PER_PAGE]["id"]
    msgs = msgs[:MSGS_PER_PAGE]
    return msgs, next_page, prev_page
