docker-compose -f docker-compose.yml -f docker-compose-test.yml up --abort-on-container-exit --exit-code-from fastapi
exit $?
