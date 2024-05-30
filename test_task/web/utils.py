from loguru import logger


def send_email(to_email: str, subject: str, body: str) -> None:
    """
    Send email.

    :param to_email: to_email.
    :param subject: subject.
    :param body: body.
    """
    logger.info(f"Sending email to {to_email}.")
