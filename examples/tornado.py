import tornado.web
from tornado.ioloop import IOLoop
from pushka import AmazonSESService

# NOTE: make sure your Amazon SES user has `ses:SendEmail` permission!
# Here's user policy example:
#
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

mail_to = ['rudy@05bit.com']
mail_from = 'rudy@05bit.com'
subject = "Pushka SES test"
text = "La-la-la! La-la-la!"


class AsyncMailHandler(tornado.web.RequestHandler):
    async def get(self):
        resp = await self.application.mailer.send_mail(
            text=text,
            subject=subject,
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

    print("Running server at http://%s:%s" % ('127.0.0.1', 8888))

    app.listen(8888)
    IOLoop.current().start()
