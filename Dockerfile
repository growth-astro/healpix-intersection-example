FROM python:slim

# Install Python dependencies
COPY requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

# Do some imports that prime some cached data
RUN python -c 'import astropy.coordinates'

CMD python -m example.demo
