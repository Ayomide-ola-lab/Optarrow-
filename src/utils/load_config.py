import os
import yaml

def load_config_section(config_path: str, section: str) -> dict:
    """
    Load a section (e.g., 'julia', 'grpc', 'http') from a YAML config file.
    
    Args:
        config_path (str): Path to YAML config file
        section (str): Section name to load

    Returns:
        dict: Section config with defaults applied

    Raises:
        FileNotFoundError: If config file does not exist
        ValueError: If YAML parsing fails
        KeyError: If section not found
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            nested_data = yaml.safe_load(file) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file {config_path}: {e}")

    section_cfg = nested_data.get(section, {})
    if not section_cfg:
        raise KeyError(f"Missing '{section}' configuration in {config_path}")

    return section_cfg
