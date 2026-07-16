from thrustlab import Client

client = Client()
project = client.projects.create(name="my new project")
print(project)
