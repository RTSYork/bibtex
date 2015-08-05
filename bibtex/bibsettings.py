"""
This contains global settings and config options that are not suitable for the Django deployment.

For example, this contains the email address of the current maintainer, not the email server to 
use to send email.
"""

maintainer = {
	"name": "Ian Gray",
	"email": "ian.gray@york.ac.uk"
}

enable_email = True
#target_email_address = 'rts-group@york.ac.uk'
target_email_address = 'ian.gray@york.ac.uk'
from_email_address = 'RTS Bibtex Database <csci669@york.ac.uk>'

"""
Used when composing the notification email, because we cannot resolve the current hose easily. 
"""
base_host_address = "http://www.cs.york.ac.uk"
