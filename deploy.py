import subprocess
import configparser

config = configparser.ConfigParser()
config.read('app/config.ini')
default_conf = config['DEFAULT']
ROCKET_URL = default_conf.get('ROCKET_URL', 'empty')

rocket_slug_pieces = ROCKET_URL.split('/')

assert len(rocket_slug_pieces) == 3, "Rocket Slug must contain 3 pieces `username`, `rocketName` and `label`"

rocket_slug = "/".join(rocket_slug_pieces[:2])
rocket_tag = rocket_slug_pieces[-1]

print(f"Uploading container with rocket {rocket_slug} and tag {rocket_tag}")

command = ''

# build the container
command += f'docker build --tag {rocket_slug}:{rocket_tag} .; '

# tag the container
command += f'docker tag {rocket_slug}:{rocket_tag} gcr.io/rockethub/rocket/{rocket_slug}:{rocket_tag}; '

# upload the container
command += f'docker push gcr.io/rockethub/rocket/{rocket_slug}:{rocket_tag}; '

subprocess.run(command, shell=True)

