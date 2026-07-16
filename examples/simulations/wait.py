from thrustlab import Client

client = Client()

# Assuming simulation is already running
sim_id = "sim_xxx"
result = client.simulations.wait(sim_id, timeout=300, poll_interval=2.0)
print(f"simulation {sim_id} reached terminal state: {result['status']}")
