docker-compose -f docker-compose-test.yml down
docker-compose -f docker-compose-test.yml up --abort-on-container-exit --exit-code-from fastapi_test
exit $?
