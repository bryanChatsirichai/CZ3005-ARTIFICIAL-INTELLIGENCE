package Utilities;

public class Coordinate {
	
	public double x;
	public double y;
	
	public Coordinate(double latitude,double longtitude) {
		this.x = latitude;
		this.y = longtitude;
	}
	
	public double getEuclideanDistance(Coordinate coord2) {
		if(coord2 == null) {
			return 0;
		}
		else {
			/*
			 *  h = sqrt ( (current_cell.x – goal.x)2 + 
            	(current_cell.y – goal.y)2 )
			 */
			double x1x2 = (this.x - coord2.x);
			double y1y2 = (this.y - coord2.y);
			return Math.sqrt((x1x2 * x1x2) + (y1y2 * y1y2) );
		}
	}
}
