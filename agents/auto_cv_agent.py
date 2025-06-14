# Resume management
class AutoCVAgent:
    def __init__(self):
        self.cv_sections = {
            'personal_info': {},
            'work_experience': [],
            'education': [],
            'skills': [],
            'certifications': []
        }

    def update(self, new_experience: dict) -> bool:
        """
        Updates the CV with new experience information
        
        Args:
            new_experience (dict): Dictionary containing the new experience details
                                 with section and content keys
        
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            section = new_experience.get('section')
            content = new_experience.get('content')
            
            if not section or not content:
                print("Error: Invalid experience format. Must contain 'section' and 'content'")
                return False
                
            if section not in self.cv_sections:
                print(f"Error: Invalid section '{section}'")
                return False
                
            if isinstance(self.cv_sections[section], list):
                self.cv_sections[section].append(content)
            else:
                self.cv_sections[section].update(content)
                
            print(f"AutoCVAgent: Successfully updated CV section '{section}'")
            return True
            
        except Exception as e:
            print(f"Error updating CV: {str(e)}")
            return False
            
    def get_cv(self) -> dict:
        """Returns the current CV content"""
        return self.cv_sections
