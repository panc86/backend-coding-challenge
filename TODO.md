# Archtiecture Improvements

- Can we use a database? What for? SQL or NoSQL?

In this case, using either SQL or NoSQL is feasible.
If we expect the Gist data to have a consistent structure, and we want
to perform complex queries, SQL might be a good choice.

On the other hand, NoSQL databases are a good choice when we want a more
flexible and schema-less data model to handle data, which can vary in structure.
NoSQL databases can be easier to scale horizontally to handle increased loads.


- How can we protect the api from abusing it?

Log and monitor API requests and responses for suspicious or abnormal behavior.
This can help to identify patterns of abuse and take action accordingly.
NoSQL DB could handle this well. Then, we could restrict the number of requests
an IP address can make within a specified time period.
This is relatively easy to achieve with Flask or a reverse proxy.

Further, we could require users to use API keys when making requests to your API.
This allows you to track and identify the source of the requests.
You can monitor the usage of API keys and revoke them if abuse is detected.


- How can we deploy the application in a cloud environment?

We could use a IaaS cloud offering where we could deploy our containerized app and
let a container orchestrator handle issues like load balancing, autoscaling, and network connectivity.


- How can we be sure the application is alive and works as expected when deployed into a cloud environment?

We could make use of an health check regularly logging the uptime status of the app.
This can be monitored via dashboards both inhouse and in the cloud environment.

We could implement a continuous integration and continuous deployment (CI/CD) pipeline that automates deployment and testing processes. This ensures that each deployment goes through a predefined set of tests before reaching the production environment.

Use blue-green deployments to minimize the downtime and any impact from potential issues in production affecting one of the deployments.


- Any other topics you may find interesting and/or important to cover

Few, perhaps good input for the technical interview
