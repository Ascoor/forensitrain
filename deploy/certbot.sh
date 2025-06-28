#!/bin/bash
# Obtain or renew Let's Encrypt certificates using certbot
# Example: ./deploy/certbot.sh yourdomain.com

set -e
DOMAIN=$1
if [ -z "$DOMAIN" ]; then
  echo "Usage: $0 <domain>" >&2
  exit 1
fi

sudo docker run --rm -it \
  -v $(pwd)/certbot/www:/var/www/certbot \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  certbot/certbot certonly \
  --webroot -w /var/www/certbot \
  --agree-tos --no-eff-email --email admin@$DOMAIN \
  -d $DOMAIN
