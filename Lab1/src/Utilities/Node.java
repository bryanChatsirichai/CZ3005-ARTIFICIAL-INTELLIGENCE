package Utilities;

import java.util.Map;




public class Node {
	
	public String id; //node ID
	public Map<Node,EdgeCosts> neighbours; //Node will contain a map to its neighbor and the distance / energy costs
	
	
	//attributes to help with the search algorithms
	
	public double distCost;//Distance cost from startNode to this Node
	public double energyCost;//Energy cost from startNode to thisNode 
	public Node parent;//keep reference to this Node parent  if any
	
	public Node(String id) {
		this.id = id;
		this.neighbours = null;
		this.distCost = 0;
		parent = null;
	}
}
