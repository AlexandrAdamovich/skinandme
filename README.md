# Skin + Me - Tech Assessment - Backend

## How to start the project
1. Clone the git repository https://github.com/AlexandrAdamovich/skindandmetest
2. Install Docker
3. Install Make if not yet installed (e.g. on Windows systems it doesn't come out of the box)
Start the application and a MySQL database:
4. Run the comman `make start`
    It should have created 5 containers: 
   1. `backend-assessment-factory-app-1`
   2. `backend-assessment-factory-db-1`
   3. `backend-assessment-factory-celery-beat-1`
   4. `backend-assessment-factory-celery_worker-1`
   5. `backend-assessment-factory-redis-1`
5. You should now be able to curl: http://0.0.0.0:5000/api/health and receive a 200 response saying: "This system is alive!"

Stop the application and the MySQL database:
```
make stop
```

Credentials and secrets can be found under `./environments/dev.txt`

### Testing

Create a virtual environment and install dependencies with
```
make venv deps
```

Then you can run the tests using
```
make tests
```

## Productionalisation considerations

- Adding a full-fledged logging system with alerts like Datadog or Google logger
- Adding permissions system for API endpoints
- Adding migrations system for the database
- Adding Flower or other monitoring system for celery tasks
- Adding more unit tests to cover edge cases and increase coverage in general
- Adding integration tests for celery