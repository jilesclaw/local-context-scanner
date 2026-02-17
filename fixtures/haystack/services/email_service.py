# Just noise file
import logging

class EmailService:
    def send(self, to, subject, body):
        logging.info(f"Sending email to {to}")
        
    def send_template(self, user, template_id, context):
        pass
