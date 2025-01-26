 
### run locallly
docker-compose -f docker-compose.yml -f docker-compose.override.mac.yml build
docker-compose -f docker-compose.yml -f docker-compose.override.mac.yml up 

### run on server
docker-compose -f docker-compose.yml -f docker-compose.override.ubuntu.yml build
docker-compose -f docker-compose.yml -f docker-compose.override.ubuntu.yml up 

but there is a git hook that will do this automatically