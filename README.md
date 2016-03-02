# pushka

Push notifications, SMS, and emails on top of asyncio

# Install

    pip install pushka

# Documentation

Latest build on Read The Docs:

    ...

Build locally:

    sphinx-build -b html docs docs/_build

# Examples

Using with **Tornado 4.3+** and **Python 3.5+**:

```python
import tornado.web
from tornado.ioloop import IOLoop
from pushka import AmazonSESService

# NOTE: make sure your Amazon SES user has `ses:SendEmail` permission!
# Here's user policy example:
# {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Effect": "Allow",
#             "Action": [
#                 "ses:SendRawEmail",
#                 "ses:SendEmail"
#             ],
#             "Resource": "*"
#         }
#     ]
# }
access_id='***'
secret_key='***'
mail_to = ['to@example.com']
mail_from = 'from@example.com'


class AsyncMailHandler(tornado.web.RequestHandler):
    async def get(self):
        resp = await self.application.mailer.send_mail(
            text="La-la-la! La-la-la!",
            subject="Pushka SES test",
            recipients=mail_to,
            sender=mail_from)

        self.write(resp)


if __name__ == "__main__":
    IOLoop.configure('tornado.platform.asyncio.AsyncIOMainLoop')

    app = tornado.web.Application([
        (r"/", AsyncMailHandler),
    ], debug=True)

    app.mailer = AmazonSESService(
        access_id=access_id,
        secret_key=secret_key,
        loop=IOLoop.current())

    app.listen(8888)
    IOLoop.current().start()
```
