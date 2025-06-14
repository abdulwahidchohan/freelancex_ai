# Digital products
class MerchandiseCreator:
    def __init__(self):
        self.designs = []
        self.mockups = []
        
    def create_product(self, idea, product_type="general", dimensions=None, colors=None):
        """
        Creates a merchandise product based on the provided idea and specifications.
        
        Args:
            idea (str): The main concept/idea for the product
            product_type (str): Type of merchandise (e.g., t-shirt, mug, poster)
            dimensions (tuple): Product dimensions (width, height)
            colors (list): List of colors to be used in the design
        
        Returns:
            dict: Product details including design, mockup and status
        """
        print(f"MerchandiseCreator: Creating {product_type} based on idea: {idea}")
        
        try:
            # Generate design
            design = self._generate_design(idea, dimensions, colors)
            self.designs.append(design)
            
            # Create mockup
            mockup = self._create_mockup(design, product_type)
            self.mockups.append(mockup)
            
            # Prepare product details
            product_details = {
                "id": len(self.designs),
                "idea": idea,
                "type": product_type,
                "design": design,
                "mockup": mockup,
                "status": "created",
                "timestamp": datetime.now().isoformat()
            }
            
            return product_details
            
        except Exception as e:
            print(f"Error creating product: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def _generate_design(self, idea, dimensions, colors):
        """Mock design generation process"""
        return f"Design for '{idea}' generated"
        
    def _create_mockup(self, design, product_type):
        """Mock mockup creation process"""
        return f"Mockup created for {product_type} with {design}"
