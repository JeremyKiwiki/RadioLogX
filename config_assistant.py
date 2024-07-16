
import json
import os

def get_modulation_params(modulation):
    mod_params = {
        "fm": ["deviation"],
        "am": ["bandwidth"]
    }
    return mod_params.get(modulation, [])

def list_available_modulations():
    modulations = []
    for filename in os.listdir('plugins'):
        if filename.endswith('.py'):
            module_name = filename[:-3]
            modulations.append(module_name)
    return modulations

def create_config():
    config = {}
    config["frequencies"] = []
    
    available_modulations = list_available_modulations()
    print("Available modulations:", ", ".join(available_modulations))
    
    while True:
        freq = int(input("Enter frequency in Hz (or '0' to finish): "))
        if freq == 0:
            break
        modulation = input(f"Enter modulation type ({'/'.join(available_modulations)}): ")
        if modulation not in available_modulations:
            print(f"Invalid modulation type. Please choose from {', '.join(available_modulations)}.")
            continue
        params = {}
        for param in get_modulation_params(modulation):
            params[param] = float(input(f"Enter value for {param}: "))
        config["frequencies"].append({
            "frequency": freq,
            "modulation": modulation,
            "params": params
        })
    
    filename = input("Enter the name for the config file (without extension): ") + ".json"
    with open(os.path.join("config", filename), 'w') as f:
        json.dump(config, f, indent=4)
    print(f"Configuration saved to config/{filename}")

if __name__ == "__main__":
    create_config()
