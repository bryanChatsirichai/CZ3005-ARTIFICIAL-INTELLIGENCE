package Utilities;



public class EdgeCosts {
	  
	public double distEdgeCost;
	public double energyEdgeCost;
	
	//Refereeing from Node i
	public Node node; 
	
	public EdgeCosts(double distEdgeCost,double eneryEdgeCost) {
		this.distEdgeCost = distEdgeCost;
		this.energyEdgeCost = eneryEdgeCost;
		this.node = null;
		
	}

}
