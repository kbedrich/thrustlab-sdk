from thrustlab import Client

client = Client()
project = client.projects.retrieve("proj_xxx")
print(project)
