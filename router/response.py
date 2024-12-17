def Ok(data):
    return dict(
        code=200,
        data=data,
        msg="success"
    )


def Bad(msg):
    return dict(
        code=400,
        data=None,
        msg=msg
    )


def NotFound():
    return dict(
        code=404,
        data=None,
        msg="not found"
    )
