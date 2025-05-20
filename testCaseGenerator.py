import random

# script to generate pseudo-random test cases for the router
def generate_testcase(filename, size=200, num_obs=8000, num_nets=10, pins_per_net=3):
    with open(filename, "w") as f:
        f.write(f"{size}x{size}\n")
        
        # Generate obstacles
        obs_set = set()
        while len(obs_set) < num_obs:
            y = random.randint(0, size-1)
            x = random.randint(0, size-1)
            obs_set.add((y, x))
        for y, x in obs_set:
            f.write(f"OBS ({y},{x})\n")
        
        # Generate nets
        for net_id in range(1, num_nets+1):
            pins = set()
            while len(pins) < pins_per_net:
                layer = random.randint(0, 1)
                y = random.randint(0, size-1)
                x = random.randint(0, size-1)
                if (y, x) not in obs_set:
                    pins.add((layer, y, x))
            pins_str = ", ".join(f"({l},{y},{x})" for l, y, x in pins)
            f.write(f"net{net_id} {pins_str}\n")

if __name__ == "__main__":
    generate_testcase("Testcases/case.txt")