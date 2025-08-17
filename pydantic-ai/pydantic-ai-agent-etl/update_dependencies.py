import os
import yaml

def update_dependencies():
    # Read .env file
    env_vars = {}
    with open(".env", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                env_vars[key] = value

    # Read dependencies.yaml file
    with open("dependencies.yaml", "r") as f:
        dependencies = yaml.safe_load(f)

    # Create a dictionary of dependency URLs
    dependency_urls = {}
    if "dependencies" in dependencies:
        for dependency_name, dependency_config in dependencies["dependencies"].items():
            if "url" in dependency_config:
                dependency_urls[dependency_config["url"]] = f"${{dependencies.{dependency_name}.url}}"

    # Update app.env section with .env variables
    if "app" in dependencies and "env" in dependencies["app"]:
        for key, value in env_vars.items():
            if value in dependency_urls:
                dependencies["app"]["env"][key] = dependency_urls[value]
            else:
                dependencies["app"]["env"][key] = value
    else:
        dependencies["app"] = {"env": env_vars}

    # Write updated dependencies back to dependencies.yaml
    with open("dependencies.yaml", "w") as f:
        yaml.dump(dependencies, f, indent=2, sort_keys=False)

if __name__ == "__main__":
    update_dependencies()