docker-compose -f docker-compose-test.yml up --abort-on-container-exit --exit-code-from fastapi
RET=$?
docker-compose -f docker-compose-test.yml down
exit $RET
