import sys
from typing import List, Optional
# Plugin system
import importlib.util
class Plugin:
    def __init__(self, name: str, module: object):
        self.name = name
        self.module = module

class PluginManager:
    def __init__(self):
        self.plugins: List[Plugin] = []
    
    def load_plugin(self, path: str) -> Optional[Plugin]:
        """
        Dynamically loads a Python module from the given path and registers it as a plugin.
        
        Args:
            path: File path to the plugin module
            
        Returns:
            Plugin object if successfully loaded, None otherwise
        """
        try:
            print(f"Loading plugin from {path}...")
            
            # Get the module name from the file path
            module_name = path.split('/')[-1].replace('.py', '')
            
            # Load module specification
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None:
                raise ImportError(f"Could not load specification for module {module_name}")
                
            # Create module instance
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            
            # Execute the module
            if spec.loader:
                spec.loader.exec_module(module)
                
            # Create and register plugin
            plugin = Plugin(module_name, module)
            self.plugins.append(plugin)
            
            print(f"Successfully loaded plugin: {module_name}")
            return plugin
            
        except Exception as e:
            print(f"Failed to load plugin from {path}: {str(e)}")
            return None

# Initialize plugin manager
plugin_manager = PluginManager()
