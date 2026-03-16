import datetime

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
templates.env.filters["strftime"] = lambda epoch: datetime.datetime.fromtimestamp(epoch).strftime("%d %b %Y, %I:%M %p")
