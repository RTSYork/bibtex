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
#from_email_address = 'RTS Bibtex Database <rtsbibtex-no-reply@cs.york.ac.uk>'
from_email_address = 'rtsbibtex-no-reply@cs.york.ac.uk'
