from thrustlab import Client

client = Client()

# Auto-iterate through all projects
for project in client.projects.list():
    print(f"{project['id']} — {project['name']}")
